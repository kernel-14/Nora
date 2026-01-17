import React from 'react';
import { Smile, Sparkles, CheckCircle2 } from 'lucide-react';
import { MoodAction } from '../types';

interface TopActionsProps {
  onActionClick: (action: MoodAction) => void;
}

export const TopActions: React.FC<TopActionsProps> = ({ onActionClick }) => {
  const actions = [
    { id: MoodAction.MOOD, label: '心情', icon: Smile, color: 'text-pink-400' },
    { id: MoodAction.INSPIRATION, label: '灵感', icon: Sparkles, color: 'text-purple-400' },
    { id: MoodAction.TODO, label: '待办', icon: CheckCircle2, color: 'text-blue-400' },
  ];

  return (
    <div className="flex justify-center items-center gap-8 w-full px-6 pt-12 pb-4 z-20">
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => onActionClick(action.id)}
          className="group flex flex-col items-center justify-center gap-2 p-2 rounded-2xl transition-all duration-500 hover:bg-white/40 active:scale-95"
        >
          <div className={`p-3 rounded-full bg-white/50 shadow-sm backdrop-blur-sm group-hover:shadow-md transition-all duration-500 ring-1 ring-white/50 ${action.color}`}>
            <action.icon size={22} strokeWidth={1.5} className="opacity-80 group-hover:opacity-100 transition-opacity" />
          </div>
          <span className="text-xs font-medium text-slate-500 tracking-wide group-hover:text-slate-700 transition-colors">
            {action.label}
          </span>
        </button>
      ))}
    </div>
  );
};