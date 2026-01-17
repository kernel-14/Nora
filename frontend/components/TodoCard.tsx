import React, { useState } from 'react';
import { Circle, CheckCircle2, BookOpen, Briefcase, Coffee, HeartPulse, Calendar, MapPin } from 'lucide-react';
import { TodoItem, TodoCategory } from '../types';

interface TodoCardProps {
  item: TodoItem;
  index: number;
  onToggle: (id: string) => void;
  location?: string;
  time?: string;
}

export const TodoCard: React.FC<TodoCardProps> = ({ item, index, onToggle, location, time }) => {
  const [isDone, setIsDone] = useState(item.isDone);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsDone(!isDone);
    onToggle(item.id);
  };

  const getCategoryIcon = (category?: TodoCategory) => {
    const props = { size: 12, className: "opacity-60" };
    switch (category) {
      case 'study': return <BookOpen {...props} />;
      case 'work': return <Briefcase {...props} />;
      case 'life': return <Coffee {...props} />;
      case 'health': return <HeartPulse {...props} />;
      default: return null;
    }
  };

  const formatScheduledTime = (timestamp?: number) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    // Simple format: "Today · 6:30 PM"
    const timeStr = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    if (isToday) return `Today · ${timeStr}`;
    
    // "Tomorrow" logic could go here, keeping it simple for now
    return `${date.toLocaleDateString([], { month: 'short', day: 'numeric' })} · ${timeStr}`;
  };

  return (
    <div
      className={`
        group relative w-full rounded-[22px] p-5 mb-4 
        border transition-all duration-700 ease-out cursor-pointer
        ${isDone 
          ? 'bg-white/20 border-white/20 shadow-none opacity-60 grayscale-[0.3]' 
          : 'bg-white/40 border-white/50 shadow-[0_4px_24px_-8px_rgba(0,0,0,0.02)] hover:bg-white/50'}
      `}
      style={{
        animation: `fadeSlideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards`,
        animationDelay: `${index * 100}ms`,
        opacity: 0,
        backdropFilter: 'blur(12px)'
      }}
    >
      {/* Inner highlight */}
      <div className="absolute inset-0 rounded-[22px] ring-1 ring-inset ring-white/30 pointer-events-none" />

      <div className="relative z-10 flex items-start gap-4">
        {/* Status Indicator (Left) */}
        <button 
          onClick={handleToggle}
          className="mt-0.5 flex-shrink-0 text-slate-400 hover:text-purple-400 transition-colors duration-300"
        >
          {isDone ? (
            <CheckCircle2 size={20} className="text-purple-300 fill-purple-50" strokeWidth={1.5} />
          ) : (
            <Circle size={20} className="opacity-50" strokeWidth={1.5} />
          )}
        </button>

        {/* Content Area */}
        <div className="flex-1 flex flex-col gap-3">
          {/* Main Title */}
          <p className={`
            text-[16px] leading-relaxed font-normal font-sans transition-all duration-500
            ${isDone ? 'text-slate-400 line-through decoration-slate-300/50' : 'text-slate-700/90'}
          `}>
            {item.title}
          </p>

          {/* Meta Info (Time, Location & Category) */}
          <div className="flex flex-col gap-2">
            {/* Time and Location */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Time */}
              {(item.scheduledAt || time) && (
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Calendar size={14} className="opacity-60" />
                  <span>
                    {time || formatScheduledTime(item.scheduledAt)}
                  </span>
                </div>
              )}

              {/* Location */}
              {location && (
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <MapPin size={14} className="opacity-60" />
                  <span>{location}</span>
                </div>
              )}
            </div>

            {/* Category */}
            {item.category && (
              <div className="flex items-center gap-2">
                <div className="px-2 py-1 rounded-full bg-white/30 border border-white/20 flex items-center gap-1.5 text-slate-500">
                  {getCategoryIcon(item.category)}
                  <span className="text-xs capitalize">{item.category}</span>
                </div>
              </div>
            )}
          </div>
        </div>
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