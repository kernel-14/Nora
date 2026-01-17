import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import { MoodItem } from '../types';
import { MoodBubble } from './MoodBubble';
import { PageHeader } from './PageHeader';
import { ChatDialog } from './ChatDialog';
import { MoodDetailDialog } from './MoodDetailDialog';

interface MoodViewProps {
  items: MoodItem[];
  onClose: () => void;
  characterImageUrl?: string;
  onSendMessage: (message: string) => Promise<string>;
}

export const MoodView: React.FC<MoodViewProps> = ({ 
  items, 
  onClose, 
  characterImageUrl,
  onSendMessage 
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedMood, setSelectedMood] = useState<MoodItem | null>(null);

  const handleMoodClick = (mood: MoodItem) => {
    setSelectedMood(mood);
  };

  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center animate-[fadeIn_0.5s_ease-out]">
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/90 via-pink-50/90 to-white/90 backdrop-blur-xl" />

      {/* Content Layer */}
      <div className="relative z-10 w-full h-full flex flex-col items-center">
        
        {/* 页面头部 */}
        <PageHeader
          title="心情记录"
          subtitle="How are you feeling today?"
          onBack={onClose}
          onChat={() => setIsChatOpen(true)}
          characterImageUrl={characterImageUrl}
        />

        {/* Central Mood Container */}
        <div className="flex-1 flex items-center justify-center w-full relative">
          
          {/* The Glass Vessel */}
          <div className="
            relative w-[320px] h-[320px] rounded-[45%] 
            bg-white/10 backdrop-blur-2xl
            border border-white/30
            shadow-[inset_0_0_60px_rgba(255,255,255,0.4),0_20px_60px_-10px_rgba(0,0,0,0.02)]
            animate-morph duration-[15s]
            flex items-center justify-center
            overflow-hidden
          ">
             {/* Subtle internal shine */}
             <div className="absolute inset-0 bg-gradient-to-t from-white/10 to-transparent opacity-50 pointer-events-none" />

             {/* Bubbles */}
             {items.map((item, index) => (
               <MoodBubble 
                 key={item.id} 
                 item={item} 
                 index={index}
                 onClick={handleMoodClick}
               />
             ))}
          </div>

        </div>

        {/* Bottom Floating Action Button */}
        <div className="mb-32 opacity-0 animate-[fadeSlideUp_1s_ease-out_forwards] delay-500">
           <button 
             className="
               group relative flex items-center justify-center w-16 h-16
               bg-white/40 backdrop-blur-xl rounded-full 
               border border-white/50 shadow-lg shadow-purple-100/50
               hover:bg-white/60 hover:scale-105 transition-all duration-700 ease-out
             "
           >
             <Plus size={24} className="text-slate-400 group-hover:text-purple-400 transition-colors duration-500" strokeWidth={1.5} />
           </button>
        </div>

      </div>

      {/* 心情详情弹窗 */}
      <MoodDetailDialog
        mood={selectedMood}
        onClose={() => setSelectedMood(null)}
      />

      {/* 对话弹窗 */}
      <ChatDialog
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        characterImageUrl={characterImageUrl}
        onSendMessage={onSendMessage}
      />

      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeSlideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeSlideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
};