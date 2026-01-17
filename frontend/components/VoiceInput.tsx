import React, { useState, useRef } from 'react';
import { Mic, Square, Send } from 'lucide-react';
import { apiService } from '../services/api';

interface VoiceInputProps {
  onProcessComplete?: () => void;
}

export function VoiceInput({ onProcessComplete }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      console.error('Failed to start recording:', err);
      setError('无法访问麦克风');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    setProcessing(true);
    setError(null);
    
    try {
      // Convert to supported format (mp3)
      const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      const response = await apiService.processInput(file);
      
      setResult(response);
      if (onProcessComplete) {
        onProcessComplete();
      }
    } catch (err: any) {
      console.error('Failed to process audio:', err);
      setError(err.message || '处理失败');
    } finally {
      setProcessing(false);
    }
  };

  const processText = async () => {
    if (!textInput.trim()) return;
    
    setProcessing(true);
    setError(null);
    
    try {
      const response = await apiService.processInput(undefined, textInput);
      setResult(response);
      setTextInput('');
      
      if (onProcessComplete) {
        onProcessComplete();
      }
    } catch (err: any) {
      console.error('Failed to process text:', err);
      setError(err.message || '处理失败');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-4">
      {/* Voice Recording */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={processing}
          className={`
            p-6 rounded-full transition-all duration-300
            ${isRecording 
              ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
              : 'bg-purple-500 hover:bg-purple-600'
            }
            text-white shadow-lg disabled:opacity-50 disabled:cursor-not-allowed
          `}
        >
          {isRecording ? <Square size={32} /> : <Mic size={32} />}
        </button>
        
        {isRecording && (
          <span className="text-sm text-slate-600 animate-pulse">
            录音中...
          </span>
        )}
      </div>

      {/* Text Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && processText()}
          placeholder="或者输入文字..."
          disabled={processing || isRecording}
          className="
            flex-1 px-4 py-3 rounded-2xl
            bg-white/80 backdrop-blur-sm
            border border-slate-200
            focus:outline-none focus:ring-2 focus:ring-purple-300
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        />
        <button
          onClick={processText}
          disabled={processing || isRecording || !textInput.trim()}
          className="
            px-6 py-3 rounded-2xl
            bg-purple-500 hover:bg-purple-600
            text-white transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          <Send size={20} />
        </button>
      </div>

      {/* Processing Indicator */}
      {processing && (
        <div className="text-center text-sm text-slate-600">
          处理中...
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-2xl bg-red-50 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="p-6 rounded-2xl bg-white/80 backdrop-blur-sm space-y-4">
          <h3 className="font-medium text-slate-700">处理结果</h3>
          
          {result.mood && (
            <div className="space-y-1">
              <div className="text-sm font-medium text-purple-600">情绪</div>
              <div className="text-sm text-slate-600">
                {result.mood.type} (强度: {result.mood.intensity}/10)
              </div>
              {result.mood.keywords.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {result.mood.keywords.map((kw: string, i: number) => (
                    <span key={i} className="px-2 py-1 rounded-full bg-purple-100 text-purple-700 text-xs">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {result.inspirations.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-pink-600">灵感</div>
              {result.inspirations.map((insp: any, i: number) => (
                <div key={i} className="text-sm text-slate-600 pl-4 border-l-2 border-pink-200">
                  {insp.core_idea}
                  <div className="flex gap-1 mt-1">
                    {insp.tags.map((tag: string, j: number) => (
                      <span key={j} className="px-2 py-0.5 rounded-full bg-pink-100 text-pink-700 text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {result.todos.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-blue-600">待办</div>
              {result.todos.map((todo: any, i: number) => (
                <div key={i} className="text-sm text-slate-600 pl-4 border-l-2 border-blue-200">
                  {todo.task}
                  {todo.time && <span className="text-xs text-slate-400 ml-2">({todo.time})</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
