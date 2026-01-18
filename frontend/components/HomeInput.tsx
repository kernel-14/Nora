import React, { useState, useRef } from 'react';
import { Mic, Square, Send, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

interface HomeInputProps {
  onRecordComplete?: () => void;
}

/**
 * Home page input component for recording inspirations
 * This component allows users to record voice or type text
 * The input is processed and split into inspirations, todos, and moods
 */
export function HomeInput({ onRecordComplete }: HomeInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Try to use audio/wav if supported, otherwise use default
      let options: MediaRecorderOptions = { mimeType: 'audio/webm' };
      
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        options = { mimeType: 'audio/wav' };
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options = { mimeType: 'audio/webm;codecs=opus' };
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options = { mimeType: 'audio/webm' };
      }
      
      const mediaRecorder = new MediaRecorder(stream, options);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType;
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await processAudio(audioBlob, mimeType);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setError(null);
      setShowSuccess(false);
    } catch (err) {
      console.error('Failed to start recording:', err);
      setError('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob, mimeType: string) => {
    setProcessing(true);
    setError(null);
    
    try {
      // Determine file extension based on mime type
      let extension = 'webm';
      let fileName = 'recording.webm';
      
      if (mimeType.includes('wav')) {
        extension = 'wav';
        fileName = 'recording.wav';
      } else if (mimeType.includes('mp4') || mimeType.includes('m4a')) {
        extension = 'm4a';
        fileName = 'recording.m4a';
      } else if (mimeType.includes('mpeg') || mimeType.includes('mp3')) {
        extension = 'mp3';
        fileName = 'recording.mp3';
      }
      
      // If it's webm, we need to convert it or send with proper naming
      // For now, we'll try to send as wav by renaming (browser may support it)
      if (extension === 'webm') {
        // Try to convert webm to wav using Web Audio API
        try {
          const wavBlob = await convertWebmToWav(audioBlob);
          const file = new File([wavBlob], 'recording.wav', { type: 'audio/wav' });
          await apiService.processInput(file);
        } catch (conversionError) {
          console.error('Conversion failed, trying direct upload:', conversionError);
          // Fallback: try sending as mp3 (some backends might accept webm as mp3)
          const file = new File([audioBlob], 'recording.mp3', { type: 'audio/mpeg' });
          await apiService.processInput(file);
        }
      } else {
        const file = new File([audioBlob], fileName, { type: mimeType });
        await apiService.processInput(file);
      }
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      
      if (onRecordComplete) {
        onRecordComplete();
      }
    } catch (err: any) {
      console.error('Failed to process audio:', err);
      setError(err.message || '处理失败，请重试');
    } finally {
      setProcessing(false);
    }
  };

  // Convert webm to wav using Web Audio API
  const convertWebmToWav = async (webmBlob: Blob): Promise<Blob> => {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const arrayBuffer = await webmBlob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    // Convert to WAV format
    const wavBuffer = audioBufferToWav(audioBuffer);
    return new Blob([wavBuffer], { type: 'audio/wav' });
  };

  // Convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const length = buffer.length * buffer.numberOfChannels * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);
    const channels: Float32Array[] = [];
    let offset = 0;
    let pos = 0;

    // Write WAV header
    const setUint16 = (data: number) => {
      view.setUint16(pos, data, true);
      pos += 2;
    };
    const setUint32 = (data: number) => {
      view.setUint32(pos, data, true);
      pos += 4;
    };

    // RIFF identifier
    setUint32(0x46464952);
    // File length
    setUint32(length - 8);
    // RIFF type
    setUint32(0x45564157);
    // Format chunk identifier
    setUint32(0x20746d66);
    // Format chunk length
    setUint32(16);
    // Sample format (raw)
    setUint16(1);
    // Channel count
    setUint16(buffer.numberOfChannels);
    // Sample rate
    setUint32(buffer.sampleRate);
    // Byte rate
    setUint32(buffer.sampleRate * buffer.numberOfChannels * 2);
    // Block align
    setUint16(buffer.numberOfChannels * 2);
    // Bits per sample
    setUint16(16);
    // Data chunk identifier
    setUint32(0x61746164);
    // Data chunk length
    setUint32(length - pos - 4);

    // Write interleaved data
    for (let i = 0; i < buffer.numberOfChannels; i++) {
      channels.push(buffer.getChannelData(i));
    }

    while (pos < length) {
      for (let i = 0; i < buffer.numberOfChannels; i++) {
        let sample = Math.max(-1, Math.min(1, channels[i][offset]));
        sample = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
        view.setInt16(pos, sample, true);
        pos += 2;
      }
      offset++;
    }

    return arrayBuffer;
  };

  const processText = async () => {
    if (!textInput.trim()) return;
    
    setProcessing(true);
    setError(null);
    
    try {
      await apiService.processInput(undefined, textInput);
      setTextInput('');
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      
      if (onRecordComplete) {
        onRecordComplete();
      }
    } catch (err: any) {
      console.error('Failed to process text:', err);
      setError(err.message || '处理失败，请重试');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto px-6 space-y-4">
      {/* Voice Recording Button */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={processing}
          className={`
            relative p-8 rounded-full transition-all duration-300 shadow-2xl
            ${isRecording 
              ? 'bg-gradient-to-br from-red-400 to-red-600 animate-pulse scale-110' 
              : 'bg-gradient-to-br from-purple-400 to-pink-500 hover:scale-105'
            }
            text-white disabled:opacity-50 disabled:cursor-not-allowed
            ${!processing && !isRecording ? 'hover:shadow-purple-300' : ''}
          `}
          aria-label={isRecording ? '停止录音' : '开始录音'}
        >
          {isRecording ? <Square size={36} /> : <Mic size={36} />}
          
          {/* Recording indicator ring */}
          {isRecording && (
            <span className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping" />
          )}
        </button>
      </div>
      
      {/* Recording status text */}
      {isRecording && (
        <div className="text-center">
          <span className="text-sm text-slate-600 animate-pulse">
            正在录音... 点击停止
          </span>
        </div>
      )}

      {/* Text Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && processText()}
          placeholder="或者在这里输入文字..."
          disabled={processing || isRecording}
          className="
            flex-1 px-5 py-3 rounded-full
            bg-white/90 backdrop-blur-sm
            border-2 border-slate-200
            focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            placeholder:text-slate-400
            transition-all duration-200
          "
        />
        <button
          onClick={processText}
          disabled={processing || isRecording || !textInput.trim()}
          className="
            px-6 py-3 rounded-full
            bg-gradient-to-r from-purple-500 to-pink-500
            hover:from-purple-600 hover:to-pink-600
            text-white transition-all duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            shadow-lg hover:shadow-xl
            flex items-center gap-2
          "
          aria-label="发送"
        >
          {processing ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>

      {/* Processing Indicator */}
      {processing && (
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-100 text-purple-700">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">正在分析...</span>
          </div>
        </div>
      )}

      {/* Success Message */}
      {showSuccess && (
        <div className="text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-green-100 text-green-700 shadow-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="text-sm font-medium">记录成功！</span>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-red-100 text-red-700 shadow-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Hint text */}
      <div className="text-center">
        <p className="text-xs text-slate-400 leading-relaxed">
          说出或写下你的想法、灵感、待办事项<br />
          我会帮你整理和记录
        </p>
      </div>
    </div>
  );
}
