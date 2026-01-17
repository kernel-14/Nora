import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import { TodoItem } from '../types';
import { TodoCard } from './TodoCard';
import { PageHeader } from './PageHeader';
import { ChatDialog } from './ChatDialog';

interface TodoViewProps {
  items: TodoItem[];
  onClose: () => void;
  onAdd?: () => void;
  onToggleItem: (id: string) => void;
  characterImageUrl?: string;
  onSendMessage: (message: string) => Promise<string>;
}

export const TodoView: React.FC<TodoViewProps> = ({ 
  items, 
  onClose, 
  onAdd, 
  onToggleItem,
  characterImageUrl,
  onSendMessage 
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Sort: Not done first, then by time
  const sortedItems = [...items].sort((a, b) => {
    if (a.isDone === b.isDone) {
      return (a.scheduledAt || 0) - (b.scheduledAt || 0);
    }
    return a.isDone ? 1 : -1;
  });

  return (
    <div className="absolute inset-0 z-50 flex flex-col animate-[fadeIn_0.5s_ease-out]">
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/95 via-pink-50/95 to-white/95 backdrop-blur-xl" />

      {/* 页面头部 */}
      <PageHeader
        title="待办事项"
        subtitle="One thing at a time"
        onBack={onClose}
        onChat={() => setIsChatOpen(true)}
        characterImageUrl={characterImageUrl}
      />

      {/* Scrollable List */}
      <div className="relative z-10 flex-1 overflow-y-auto no-scrollbar scroll-smooth px-6 pt-2 pb-32">
        <div className="w-full max-w-lg mx-auto flex flex-col gap-2">
           {sortedItems.map((item, index) => (
             <TodoCard 
               key={item.id} 
               item={item} 
               index={index} 
               onToggle={onToggleItem}
               location={item.location}
               time={item.time}
             />
           ))}
        </div>
      </div>

      {/* Floating Action Button */}
      <div className="absolute bottom-24 right-6 z-30 opacity-0 animate-[fadeSlideUp_0.8s_ease-out_forwards] delay-300">
        <button 
          onClick={onAdd}
          className="
            group relative flex items-center justify-center w-14 h-14 
            bg-white/60 backdrop-blur-xl rounded-full shadow-lg shadow-purple-100/50
            ring-1 ring-white/60 text-purple-400
            hover:bg-white/80 hover:text-purple-500 hover:scale-105
            active:scale-95 transition-all duration-500
          "
        >
          <Plus size={24} strokeWidth={1.5} className="group-hover:rotate-90 transition-transform duration-500" />
        </button>
      </div>

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