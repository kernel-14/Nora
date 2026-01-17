import React from 'react';
import { Sparkles } from 'lucide-react';

interface CustomizationButtonProps {
  onClick: () => void;
}

export const CustomizationButton: React.FC<CustomizationButtonProps> = ({ onClick }) => {
  return (
    <div className="fixed bottom-28 right-6 z-40">
      <button 
        onClick={onClick}
        className="
          group relative flex items-center justify-center w-12 h-12 
          bg-white/60 backdrop-blur-md rounded-full shadow-sm 
          ring-1 ring-white/60 text-purple-400
          hover:bg-white/80 hover:text-purple-500 hover:shadow-md hover:scale-105
          active:scale-95 transition-all duration-500
        "
        aria-label="Customize AI"
      >
        <Sparkles size={20} strokeWidth={1.5} />
        {/* Tooltip hint style */}
        <span className="absolute right-full mr-3 text-xs text-slate-400 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          AI形象定制
        </span>
      </button>
    </div>
  );
};