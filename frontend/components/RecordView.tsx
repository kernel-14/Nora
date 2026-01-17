import React, { useMemo } from 'react';
import { RecordItem, RecordSource } from '../types';
import { RecordCard } from './RecordCard';

interface RecordViewProps {
  items: RecordItem[];
}

export const RecordView: React.FC<RecordViewProps> = ({ items }) => {
  
  // Group items by date
  const groupedItems = useMemo(() => {
    const groups: Record<string, RecordItem[]> = {};
    
    items.forEach(item => {
      const date = new Date(item.createdAt);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      let key = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      if (date.toDateString() === today.toDateString()) {
        key = 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        key = 'Yesterday';
      }

      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(item);
    });

    return groups;
  }, [items]);

  return (
    <div className="w-full h-full flex flex-col pt-16 px-6 pb-32 overflow-y-auto no-scrollbar scroll-smooth">
      {/* Subtle Header */}
      <div className="mb-10 text-center opacity-0 animate-[fadeSlideUp_1s_ease-out_forwards]">
        <h2 className="text-xl font-light text-slate-600/60 tracking-tight font-serif italic">
          Your words, gently kept.
        </h2>
      </div>

      {/* List of Groups */}
      <div className="flex flex-col gap-8">
        {Object.entries(groupedItems).map(([dateLabel, groupItems], groupIndex) => (
          <div key={dateLabel} className="flex flex-col">
            {/* Date Group Header - Extremely subtle */}
            <div 
              className="sticky top-0 z-20 py-2 mb-3 text-xs font-semibold tracking-widest text-slate-300/80 uppercase backdrop-blur-[2px]"
              style={{ animationDelay: `${groupIndex * 100}ms` }}
            >
              {dateLabel}
            </div>
            
            {/* Cards */}
            <div className="flex flex-col gap-1">
              {(groupItems as RecordItem[])
                .sort((a, b) => b.createdAt - a.createdAt) // Newest first
                .map((item, index) => (
                  <RecordCard 
                    key={item.id} 
                    item={item} 
                    index={index} 
                  />
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Spacer for bottom nav */}
      <div className="h-20" />
    </div>
  );
};