import React from 'react';

interface AIEntityProps {
  imageUrl?: string;
}

export const AIEntity: React.FC<AIEntityProps> = ({ imageUrl }) => {
  return (
    <div className="relative w-72 h-72 flex items-center justify-center pointer-events-none select-none">
      {/* Outer Glow / Aura */}
      <div className="absolute inset-0 bg-purple-200/30 blur-[60px] rounded-full animate-pulse pointer-events-none"></div>
      
      {imageUrl ? (
        // 显示角色图片
        <>
          {/* 背景光晕 */}
          <div className="absolute w-64 h-64 opacity-60 animate-morph animate-float duration-[10s]">
            <div className="w-full h-full rounded-full bg-gradient-to-br from-pink-300 via-purple-300 to-indigo-200 blur-2xl animate-gradient-slow"></div>
          </div>
          
          {/* 角色图片 */}
          <div className="relative z-10 w-56 h-56 rounded-full overflow-hidden border-4 border-white/50 shadow-2xl animate-float">
            <img 
              src={imageUrl} 
              alt="AI Character" 
              className="w-full h-full object-cover"
            />
          </div>
          
          {/* 前景光效 */}
          <div className="absolute w-32 h-32 bg-white/20 blur-[40px] rounded-full animate-breathe pointer-events-none"></div>
        </>
      ) : (
        // 默认的抽象形态
        <>
          {/* Main Morphing Blob 1 */}
          <div className="absolute w-64 h-64 opacity-80 animate-morph animate-float duration-[10s]">
            <div className="w-full h-full rounded-[inherit] bg-gradient-to-br from-pink-300 via-purple-300 to-indigo-200 blur-xl animate-gradient-slow opacity-80"></div>
          </div>

          {/* Secondary Morphing Blob 2 (Overlay for depth) */}
          <div className="absolute w-60 h-60 opacity-60 animate-morph animate-float duration-[12s] delay-1000 rotate-45">
            <div className="w-full h-full rounded-[inherit] bg-gradient-to-tl from-indigo-200 via-pink-200 to-white blur-lg animate-gradient-slow"></div>
          </div>

          {/* Core "Soul" Light */}
          <div className="absolute w-32 h-32 bg-white/40 blur-[40px] rounded-full animate-breathe pointer-events-none"></div>
        </>
      )}
      
      {/* Interactive Hit Area (Invisible but clickable for feedback) */}
      <div 
        className="absolute inset-0 rounded-full cursor-pointer pointer-events-auto z-10 active:scale-95 transition-transform duration-700 ease-out"
        onClick={() => {
          // Simple visual feedback logic could go here, or handled by parent
          console.log("Touched AI entity");
        }}
      ></div>
    </div>
  );
};