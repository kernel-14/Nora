import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { InspirationItem } from '../types';
import { InspirationCard } from './InspirationCard';
import { PageHeader } from './PageHeader';
import { ChatDialog } from './ChatDialog';
import { AddInspirationDialog } from './AddInspirationDialog';

interface InspirationViewProps {
  items: InspirationItem[];
  onClose: () => void;
  onAdd?: (content: string, isVoice: boolean) => Promise<void>;
  characterImageUrl?: string;
  onSendMessage: (message: string) => Promise<string>;
}

export const InspirationView: React.FC<InspirationViewProps> = ({ 
  items, 
  onClose, 
  onAdd,
  characterImageUrl,
  onSendMessage 
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  const handleAddInspiration = async (content: string, isVoice: boolean) => {
    if (onAdd) {
      await onAdd(content, isVoice);
    }
  };

  return (
    <div className="absolute inset-0 z-50 flex flex-col animate-[fadeIn_0.5s_ease-out]">
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/95 via-pink-50/95 to-white/95 backdrop-blur-xl" />

      {/* 页面头部 */}
      <PageHeader
        title="灵感记录"
        subtitle="A thought worth keeping"
        onBack={onClose}
        onChat={() => setIsChatOpen(true)}
        characterImageUrl={characterImageUrl}
      />

      {/* Scrollable List */}
      <div className="relative z-10 flex-1 overflow-y-auto no-scrollbar scroll-smooth px-6 pt-2 pb-32">
        <div className="w-full max-w-lg mx-auto flex flex-col gap-2">
           {items.map((item, index) => (
             <InspirationCard key={item.id} item={item} index={index} />
           ))}
        </div>
        
        {/* Empty state gentle prompt if no items */}
        {items.length === 0 && (
          <div className="flex flex-col items-center justify-center h-[60vh] text-center opacity-40">
            <Sparkles size={32} className="text-purple-300 mb-4 animate-pulse" strokeWidth={1} />
            <p className="text-slate-400 font-light tracking-wide">Waiting for a spark...</p>
          </div>
        )}
      </div>

      {/* Floating Action Button */}
      <div className="absolute bottom-24 right-6 z-30 opacity-0 animate-[fadeSlideUp_0.8s_ease-out_forwards] delay-300">
        <button 
          onClick={() => setIsAddDialogOpen(true)}
          className="
            group relative flex items-center justify-center w-14 h-14 
            bg-white/60 backdrop-blur-xl rounded-full shadow-lg shadow-purple-100/50
            ring-1 ring-white/60 text-purple-400
            hover:bg-white/80 hover:text-purple-500 hover:scale-105
            active:scale-95 transition-all duration-500
          "
        >
          <Sparkles size={22} strokeWidth={1.5} className="group-hover:rotate-12 transition-transform duration-500" />
        </button>
      </div>

      {/* 添加灵感对话框 */}
      <AddInspirationDialog
        isOpen={isAddDialogOpen}
        onClose={() => setIsAddDialogOpen(false)}
        onSubmit={handleAddInspiration}
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
        @keyframes fadeSlideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
};