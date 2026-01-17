import React from 'react';
import { X } from 'lucide-react';
import { MoodItem, MoodType } from '../types';

interface MoodDetailDialogProps {
  mood: MoodItem | null;
  onClose: () => void;
}

export const MoodDetailDialog: React.FC<MoodDetailDialogProps> = ({ mood, onClose }) => {
  if (!mood) return null;

  const getMoodEmoji = (type: MoodType) => {
    switch (type) {
      case MoodType.HAPPY: return '😊';
      case MoodType.CALM: return '😌';
      case MoodType.TIRED: return '😴';
      case MoodType.ANXIOUS: return '😰';
      case MoodType.HOPEFUL: return '🌟';
      default: return '😐';
    }
  };

  const getMoodColor = (type: MoodType) => {
    switch (type) {
      case MoodType.HAPPY: return 'from-rose-200 to-orange-100';
      case MoodType.CALM: return 'from-violet-200 to-purple-100';
      case MoodType.TIRED: return 'from-blue-200 to-slate-200';
      case MoodType.ANXIOUS: return 'from-stone-200 to-orange-50';
      case MoodType.HOPEFUL: return 'from-yellow-100 to-amber-50';
      default: return 'from-slate-200 to-slate-100';
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (days === 1) {
      return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
    }
  };

  return (
    <div className="
      fixed inset-0 z-[200] 
      flex items-center justify-center
      bg-black/30 backdrop-blur-sm
      animate-[fadeIn_0.3s_ease-out]
      p-4
    ">
      <div className={`
        relative w-full max-w-sm
        bg-gradient-to-br ${getMoodColor(mood.type)}
        rounded-3xl shadow-2xl
        border border-white/50
        p-6
        animate-[slideUp_0.3s_ease-out]
      `}>
        {/* 关闭按钮 */}
        <button 
          onClick={onClose}
          className="
            absolute top-4 right-4
            p-2 rounded-full
            bg-white/50 hover:bg-white/70
            text-slate-600 hover:text-slate-800
            transition-all duration-200
          "
        >
          <X size={20} />
        </button>

        {/* 内容 */}
        <div className="flex flex-col items-center text-center space-y-4">
          {/* Emoji */}
          <div className="text-6xl animate-bounce">
            {getMoodEmoji(mood.type)}
          </div>

          {/* 心情类型 */}
          <h3 className="text-2xl font-medium text-slate-700">
            {mood.type}
          </h3>

          {/* 强度指示器 */}
          <div className="w-full space-y-2">
            <div className="flex justify-between text-sm text-slate-600">
              <span>情绪强度</span>
              <span className="font-medium">{Math.round(mood.intensity * 10)}/10</span>
            </div>
            <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-slate-400 to-slate-600 rounded-full transition-all duration-500"
                style={{ width: `${mood.intensity * 100}%` }}
              />
            </div>
          </div>

          {/* 时间 */}
          <div className="text-sm text-slate-600">
            {formatDate(mood.date)}
          </div>

          {/* 提示 */}
          <p className="text-xs text-slate-500 italic">
            "每一种情绪都值得被记录和珍惜"
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
