import React from 'react';
import { ArrowLeft, MessageCircle } from 'lucide-react';

interface PageHeaderProps {
  title?: string;
  subtitle?: string;
  onBack: () => void;
  onChat: () => void;
  showCharacter?: boolean;
  characterImageUrl?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ 
  title, 
  subtitle, 
  onBack, 
  onChat,
  showCharacter = true,
  characterImageUrl 
}) => {
  return (
    <div className="w-full px-6 pt-8 pb-4 flex items-center justify-between relative z-10">
      {/* 返回按钮 */}
      <button 
        onClick={onBack}
        className="
          p-2.5 rounded-full 
          bg-white/40 backdrop-blur-sm
          border border-white/50
          text-slate-600 hover:text-slate-800
          hover:bg-white/60 hover:scale-105
          transition-all duration-300
          shadow-sm hover:shadow-md
        "
      >
        <ArrowLeft size={20} strokeWidth={2} />
      </button>

      {/* 中间标题区域 */}
      <div className="flex-1 flex flex-col items-center justify-center mx-4">
        {showCharacter && (
          <div className="mb-2 relative">
            {characterImageUrl ? (
              <img 
                src={characterImageUrl} 
                alt="AI Companion" 
                className="w-12 h-12 rounded-full object-cover border-2 border-white/50 shadow-md"
              />
            ) : (
              <div className="
                w-12 h-12 rounded-full 
                bg-gradient-to-br from-purple-200 to-pink-200
                border-2 border-white/50 shadow-md
                flex items-center justify-center
              ">
                <span className="text-lg">🐱</span>
              </div>
            )}
            {/* 在线状态指示器 */}
            <div className="
              absolute -bottom-0.5 -right-0.5 
              w-3 h-3 rounded-full 
              bg-green-400 border-2 border-white
              animate-pulse
            " />
          </div>
        )}
        
        {title && (
          <h2 className="text-lg font-medium text-slate-700 tracking-wide">
            {title}
          </h2>
        )}
        
        {subtitle && (
          <p className="text-xs text-slate-400 mt-0.5 tracking-wider">
            {subtitle}
          </p>
        )}
      </div>

      {/* 对话按钮 */}
      <button 
        onClick={onChat}
        className="
          relative p-2.5 rounded-full 
          bg-gradient-to-br from-purple-400 to-pink-400
          text-white
          hover:from-purple-500 hover:to-pink-500
          hover:scale-105
          transition-all duration-300
          shadow-md hover:shadow-lg
          animate-pulse-slow
        "
      >
        <MessageCircle size={20} strokeWidth={2} />
        
        {/* 提示气泡 */}
        <div className="
          absolute -top-1 -right-1 
          w-2 h-2 rounded-full 
          bg-red-400 border border-white
        " />
      </button>

      <style>{`
        @keyframes pulse-slow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }
        .animate-pulse-slow {
          animation: pulse-slow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};
