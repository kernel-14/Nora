import React from 'react';
import { MoodItem, MoodType } from '../types';

interface MoodBubbleProps {
  item: MoodItem;
  index: number;
  onClick?: (item: MoodItem) => void;
}

export const MoodBubble: React.FC<MoodBubbleProps> = ({ item, index, onClick }) => {
  
  const getColorClasses = (type: MoodType) => {
    switch (type) {
      case MoodType.HAPPY:
        return 'bg-gradient-to-tr from-rose-200/80 to-orange-100/80 shadow-[0_0_30px_rgba(251,113,133,0.2)]';
      case MoodType.CALM:
        return 'bg-gradient-to-tr from-violet-200/80 to-purple-100/80 shadow-[0_0_30px_rgba(167,139,250,0.2)]';
      case MoodType.TIRED:
        return 'bg-gradient-to-tr from-blue-200/80 to-slate-200/80 shadow-[0_0_30px_rgba(148,163,184,0.2)]';
      case MoodType.ANXIOUS:
        return 'bg-gradient-to-tr from-stone-200/80 to-orange-50/80 shadow-[0_0_30px_rgba(214,211,209,0.2)]';
      case MoodType.HOPEFUL:
        return 'bg-gradient-to-tr from-yellow-100/90 to-amber-50/80 shadow-[0_0_30px_rgba(253,230,138,0.2)]';
      default:
        return 'bg-slate-200/50';
    }
  };

  // Calculate random-ish animation durations based on index to avoid uniform movement
  const floatDuration = 8 + (index % 3) * 2; 
  const breatheDuration = 4 + (index % 2) * 2;
  const delay = index * 0.5;

  // Base size calculation
  const size = 80 + (item.intensity * 40); // 80px to 120px

  return (
    <div
      onClick={() => onClick?.(item)}
      className="absolute transition-all duration-1000 ease-in-out cursor-pointer hover:scale-110 hover:brightness-105 active:scale-95 group"
      style={{
        left: `${item.x || 50}%`,
        top: `${item.y || 50}%`,
        width: `${size}px`,
        height: `${size}px`,
        transform: 'translate(-50%, -50%)', // Center on coordinate
      }}
      title={`${item.type} - 点击查看详情`}
    >
      <div 
        className={`
          w-full h-full rounded-full backdrop-blur-[2px] 
          ${getColorClasses(item.type)}
        `}
        style={{
          animation: `
            float ${floatDuration}s ease-in-out infinite,
            breathe ${breatheDuration}s ease-in-out infinite
          `,
          animationDelay: `${delay}s`
        }}
      >
        {/* Inner Highlight for bubble effect */}
        <div className="absolute top-[20%] left-[20%] w-[20%] h-[15%] bg-white/40 rounded-full blur-[2px] rotate-45" />
      </div>
    </div>
  );
};