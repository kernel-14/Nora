import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';

interface AIEntityProps {
  imageUrl?: string;
  onGreeting?: (greeting: string) => void;
  onOpenChat?: () => void;
  latestRecord?: string;
}

export const AIEntity: React.FC<AIEntityProps> = ({ imageUrl, onGreeting, onOpenChat, latestRecord }) => {
  const [showGreeting, setShowGreeting] = useState(false);
  const [greeting, setGreeting] = useState('');
  const [isHovered, setIsHovered] = useState(false);

  // 生成个性化问候语
  const generateGreeting = () => {
    if (latestRecord) {
      // 基于最近的录音生成问候
      const greetings = [
        `刚才你说"${latestRecord.substring(0, 20)}..."，想聊聊吗？`,
        `关于"${latestRecord.substring(0, 20)}..."，我有些想法想和你分享~`,
        `听到你说"${latestRecord.substring(0, 20)}..."，我很想了解更多呢`,
        `"${latestRecord.substring(0, 20)}..."这让我想起了一些事情，要聊聊吗？`,
      ];
      return greetings[Math.floor(Math.random() * greetings.length)];
    } else {
      // 默认问候语
      const defaultGreetings = [
        '嗨！今天过得怎么样呀？',
        '你好呀！有什么想和我分享的吗？',
        'Hi~ 我一直在这里陪着你哦',
        '嘿！要不要聊聊天？',
        '你来啦！今天感觉如何？',
      ];
      return defaultGreetings[Math.floor(Math.random() * defaultGreetings.length)];
    }
  };

  const handleClick = () => {
    const newGreeting = generateGreeting();
    setGreeting(newGreeting);
    setShowGreeting(true);
    if (onGreeting) {
      onGreeting(newGreeting);
    }
  };

  const handleCloseGreeting = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowGreeting(false);
  };

  const handleOpenChat = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onOpenChat) {
      onOpenChat();
    }
  };

  return (
    <div className="relative w-72 h-72 flex items-center justify-center select-none">
      {/* Outer Glow / Aura - 增强动效 */}
      <div className="absolute inset-0 bg-purple-200/30 blur-[60px] rounded-full animate-pulse pointer-events-none"></div>
      
      {imageUrl ? (
        // 显示角色图片
        <>
          {/* 背景光晕 - 增强动效 */}
          <div className="absolute w-64 h-64 opacity-60 animate-morph animate-float duration-[10s]">
            <div className="w-full h-full rounded-full bg-gradient-to-br from-pink-300 via-purple-300 to-indigo-200 blur-2xl animate-gradient-slow"></div>
          </div>
          
          {/* 角色图片 - 添加悬停和点击效果 */}
          <div 
            className={`
              relative z-10 w-56 h-56 rounded-full overflow-hidden 
              border-4 border-white/50 shadow-2xl 
              animate-float cursor-pointer
              transition-all duration-500 ease-out
              ${isHovered ? 'scale-110 border-purple-300/70 shadow-purple-300/50' : 'scale-100'}
              ${showGreeting ? 'scale-105' : ''}
            `}
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            <img 
              src={imageUrl} 
              alt="AI Character" 
              className="w-full h-full object-cover"
            />
            
            {/* 悬停时的光效 */}
            {isHovered && (
              <div className="absolute inset-0 bg-gradient-to-t from-purple-400/20 to-transparent animate-pulse"></div>
            )}
          </div>
          
          {/* 前景光效 - 增强 */}
          <div className="absolute w-32 h-32 bg-white/20 blur-[40px] rounded-full animate-breathe pointer-events-none"></div>
          
          {/* 悬停提示 */}
          {isHovered && !showGreeting && (
            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 z-20 animate-[fadeIn_0.3s_ease-out]">
              <div className="flex items-center gap-1 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-full shadow-lg border border-purple-200/50">
                <MessageCircle size={14} className="text-purple-500" />
                <span className="text-xs text-slate-600 font-medium">点击和我聊天</span>
              </div>
            </div>
          )}
        </>
      ) : (
        // 默认的抽象形态 - 增强动效
        <>
          {/* Main Morphing Blob 1 */}
          <div className="absolute w-64 h-64 opacity-80 animate-morph animate-float duration-[10s]">
            <div className="w-full h-full rounded-[inherit] bg-gradient-to-br from-pink-300 via-purple-300 to-indigo-200 blur-xl animate-gradient-slow opacity-80"></div>
          </div>

          {/* Secondary Morphing Blob 2 */}
          <div className="absolute w-60 h-60 opacity-60 animate-morph animate-float duration-[12s] delay-1000 rotate-45">
            <div className="w-full h-full rounded-[inherit] bg-gradient-to-tl from-indigo-200 via-pink-200 to-white blur-lg animate-gradient-slow"></div>
          </div>

          {/* Core "Soul" Light */}
          <div className="absolute w-32 h-32 bg-white/40 blur-[40px] rounded-full animate-breathe pointer-events-none"></div>
          
          {/* 可点击区域 */}
          <div 
            className={`
              absolute inset-0 rounded-full cursor-pointer z-10 
              transition-transform duration-700 ease-out
              ${isHovered ? 'scale-110' : 'scale-100'}
              active:scale-95
            `}
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          ></div>
        </>
      )}
      
      {/* 可爱的对话框 */}
      {showGreeting && (
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 z-30 w-64 animate-[bounceIn_0.5s_ease-out]">
          <div className="relative bg-white/95 backdrop-blur-xl rounded-3xl p-4 shadow-2xl border-2 border-purple-200/50">
            {/* 关闭按钮 */}
            <button
              onClick={handleCloseGreeting}
              className="absolute -top-2 -right-2 p-1.5 bg-purple-100 hover:bg-purple-200 rounded-full shadow-lg transition-colors"
            >
              <X size={14} className="text-purple-600" />
            </button>
            
            {/* 对话内容 */}
            <div className="flex items-start gap-3">
              <button
                onClick={handleOpenChat}
                className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-md hover:scale-110 hover:shadow-lg transition-all duration-300 cursor-pointer group"
                title="点击打开对话"
              >
                <MessageCircle size={20} className="text-white group-hover:scale-110 transition-transform" />
              </button>
              <div className="flex-1">
                <p className="text-sm text-slate-700 leading-relaxed">
                  {greeting}
                </p>
              </div>
            </div>
            
            {/* 小尾巴 */}
            <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-6 h-6 bg-white/95 backdrop-blur-xl rotate-45 border-r-2 border-b-2 border-purple-200/50"></div>
          </div>
        </div>
      )}
    </div>
  );
};