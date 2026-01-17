import React, { useState, useRef } from 'react';
import { X, Send, Mic, Square, Loader2 } from 'lucide-react';

interface AddInspirationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string, isVoice: boolean) => Promise<void>;
}

export const AddInspirationDialog: React.FC<AddInspirationDialogProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit 
}) => {
  const [content, setContent] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  if (!isOpen) return null;

  const handleTextSubmit = async () => {
    if (!content.trim() || isProcessing) return;

    setIsProcessing(true);
    try {
      await onSubmit(content, false);
      setContent('');
      onClose();
    } catch (error) {
      console.error('Failed to submit inspiration:', error);
    } finally {
      setIsProcessing(false);
    }
  };

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
    } catch (err) {
      console.error('Failed to start recording:', err);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      
      // 这里调用 API 处理音频
      // 暂时使用文本提交的方式
      await onSubmit('语音录制的灵感', true);
      onClose();
    } catch (error) {
      console.error('Failed to process audio:', error);
      alert('语音处理失败，请重试');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTextSubmit();
    }
  };

  return (
    <div className="
      fixed inset-0 z-[100] 
      flex items-center justify-center
      bg-black/20 backdrop-blur-sm
      animate-[fadeIn_0.3s_ease-out]
      p-4
    ">
      <div className="
        relative w-full max-w-md
        bg-gradient-to-br from-white/95 to-purple-50/95
        backdrop-blur-xl
        rounded-3xl shadow-2xl
        border border-white/50
        p-6
        animate-[slideUp_0.3s_ease-out]
      ">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-slate-700">
            ✨ 记录灵感
          </h3>
          <button 
            onClick={onClose}
            className="
              p-2 rounded-full
              text-slate-400 hover:text-slate-600
              hover:bg-white/50
              transition-all duration-200
            "
          >
            <X size={20} />
          </button>
        </div>

        {/* 输入区域 */}
        <div className="space-y-4">
          {/* 文本输入 */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="写下你的灵感..."
            disabled={isProcessing || isRecording}
            rows={4}
            className="
              w-full px-4 py-3 rounded-2xl
              bg-white/80 border border-white/50
              text-slate-700 placeholder:text-slate-400
              focus:outline-none focus:ring-2 focus:ring-purple-300
              disabled:opacity-50 disabled:cursor-not-allowed
              resize-none
            "
          />

          {/* 按钮组 */}
          <div className="flex items-center gap-3">
            {/* 语音按钮 */}
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing}
              className={`
                flex-1 flex items-center justify-center gap-2
                px-4 py-3 rounded-2xl
                ${isRecording 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                  : 'bg-gradient-to-br from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500'
                }
                text-white font-medium
                transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:scale-105 active:scale-95
              `}
            >
              {isRecording ? (
                <>
                  <Square size={18} />
                  <span>停止录音</span>
                </>
              ) : (
                <>
                  <Mic size={18} />
                  <span>语音输入</span>
                </>
              )}
            </button>

            {/* 提交按钮 */}
            <button
              onClick={handleTextSubmit}
              disabled={!content.trim() || isProcessing || isRecording}
              className="
                flex items-center justify-center
                w-12 h-12 rounded-full
                bg-gradient-to-br from-purple-400 to-pink-400
                hover:from-purple-500 hover:to-pink-500
                text-white
                transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:scale-105 active:scale-95
              "
            >
              {isProcessing ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>

          {/* 提示文字 */}
          <p className="text-xs text-slate-400 text-center">
            {isRecording 
              ? '正在录音中...' 
              : '按 Enter 提交，Shift + Enter 换行'
            }
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to { 
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
};
