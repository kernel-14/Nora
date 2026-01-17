import React from 'react';
import { InspirationItem } from '../types';

interface InspirationCardProps {
  item: InspirationItem;
  index: number;
}

export const InspirationCard: React.FC<InspirationCardProps> = ({ item, index }) => {
  // Format time (e.g., "10:42 AM" or "Jan 17 · Evening")
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      const monthDay = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      // Simple logic to approximate time of day for "companion" feel
      const hour = date.getHours();
      let timeOfDay = 'Day';
      if (hour < 12) timeOfDay = 'Morning';
      else if (hour < 18) timeOfDay = 'Afternoon';
      else timeOfDay = 'Evening';
      
      return `${monthDay} · ${timeOfDay}`;
    }
  };

  return (
    <div
      className="group relative w-full bg-white/40 backdrop-blur-xl border border-white/50 shadow-[0_4px_24px_-8px_rgba(0,0,0,0.02)] rounded-[24px] p-6 mb-5 transition-all duration-700 hover:bg-white/50 active:scale-[0.99]"
      style={{
        animation: `fadeSlideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards`,
        animationDelay: `${index * 100}ms`,
        opacity: 0
      }}
    >
      {/* Inner Highlight */}
      <div className="absolute inset-0 rounded-[24px] ring-1 ring-inset ring-white/40 pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 mb-4">
        <p className="text-[16px] leading-relaxed font-normal text-slate-800/80 font-sans whitespace-pre-wrap">
          {item.content}
        </p>
      </div>

      {/* Footer: Tags + Time */}
      <div className="relative z-10 flex items-end justify-between mt-2">
        
        {/* Tags */}
        <div className="flex flex-wrap gap-2 max-w-[70%]">
          {item.tags?.map((tag, i) => (
            <span 
              key={i}
              className="px-2.5 py-1 rounded-full bg-white/30 border border-white/40 text-[11px] font-medium text-slate-500/70 tracking-wide backdrop-blur-sm"
            >
              #{tag}
            </span>
          ))}
        </div>

        {/* Timestamp */}
        <span className="text-[12px] font-light text-slate-400/40 tracking-wider ml-2 whitespace-nowrap">
          {formatTime(item.createdAt)}
        </span>
      </div>
      
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};