import React from 'react';
import { Smile, Sparkles, Mic, PenLine } from 'lucide-react';
import { RecordItem, RecordSource } from '../types';

interface RecordCardProps {
  item: RecordItem;
  index: number;
}

export const RecordCard: React.FC<RecordCardProps> = ({ item, index }) => {
  // Format time (e.g., 10:42 AM)
  const timeString = new Date(item.createdAt).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  const getSourceIcon = (source: RecordSource) => {
    switch (source) {
      case RecordSource.MOOD: return <Smile size={12} />;
      case RecordSource.INSPIRATION: return <Sparkles size={12} />;
      case RecordSource.VOICE: return <Mic size={12} />;
      case RecordSource.MANUAL: return <PenLine size={12} />;
    }
  };

  const getSourceLabel = (source: RecordSource) => {
    switch (source) {
      case RecordSource.MOOD: return 'Mood';
      case RecordSource.INSPIRATION: return 'Idea';
      case RecordSource.VOICE: return 'Voice';
      case RecordSource.MANUAL: return 'Note';
    }
  };

  return (
    <div 
      className="group relative w-full bg-white/30 backdrop-blur-xl border border-white/40 shadow-[0_4px_20px_-10px_rgba(0,0,0,0.02)] hover:bg-white/40 transition-all duration-500 rounded-[24px] p-5 mb-4 animate-morph"
      style={{
        animation: `fadeSlideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards`,
        animationDelay: `${index * 100}ms`,
        opacity: 0 // Start hidden for animation
      }}
    >
      {/* Inner highlight for "3D glass" feel */}
      <div className="absolute inset-0 rounded-[24px] ring-1 ring-inset ring-white/30 pointer-events-none" />

      {/* Main Content */}
      <div className="relative z-10">
        <p className="text-[15px] leading-relaxed font-normal text-slate-800/80 line-clamp-3 font-sans">
          {item.content}
        </p>
      </div>

      {/* Meta Data */}
      <div className="relative z-10 flex items-center justify-between mt-4">
        {/* Source Tag - Extremely subtle */}
        <div className="flex items-center gap-1.5 text-slate-400/40 text-[11px] font-medium tracking-wide group-hover:text-slate-500/60 transition-colors duration-300">
          {getSourceIcon(item.sourceType)}
          <span>{getSourceLabel(item.sourceType)}</span>
        </div>

        {/* Timestamp */}
        <span className="text-[11px] font-light text-slate-400/30 tracking-wider">
          {timeString}
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