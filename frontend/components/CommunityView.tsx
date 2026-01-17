import React, { useState } from 'react';
import { PenLine, X } from 'lucide-react';
import { CommunityPost } from '../types';
import { CommunityCard } from './CommunityCard';

interface CommunityViewProps {
  posts: CommunityPost[];
  onAddPost: (content: string) => void;
}

export const CommunityView: React.FC<CommunityViewProps> = ({ posts, onAddPost }) => {
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [newContent, setNewContent] = useState('');

  const handleSubmit = () => {
    if (!newContent.trim()) return;
    onAddPost(newContent);
    setNewContent('');
    setIsComposeOpen(false);
  };

  return (
    <div className="w-full h-full relative">
      <div className="w-full h-full flex flex-col pt-16 px-6 pb-32 overflow-y-auto no-scrollbar scroll-smooth">
        {/* Header */}
        <div className="mb-8 text-center opacity-0 animate-[fadeSlideUp_1s_ease-out_forwards]">
          <h2 className="text-xl font-light text-slate-600/60 tracking-tight font-serif italic">
            你并不孤单
          </h2>
        </div>

        {/* Feed */}
        <div className="flex flex-col w-full max-w-md mx-auto">
          {posts.map((post, index) => (
            <CommunityCard key={post.id} post={post} index={index} />
          ))}
        </div>
        
        {/* Spacer for bottom nav */}
        <div className="h-24" />
      </div>

      {/* Floating Compose Button */}
      {!isComposeOpen && (
        <div className="fixed bottom-28 right-6 z-40 animate-[fadeSlideUp_0.5s_ease-out]">
          <button 
            onClick={() => setIsComposeOpen(true)}
            className="
              group relative flex items-center justify-center w-14 h-14 
              bg-white/60 backdrop-blur-md rounded-full shadow-lg shadow-purple-100/50
              ring-1 ring-white/60 text-purple-400
              hover:bg-white/80 hover:text-purple-500 hover:scale-105
              active:scale-95 transition-all duration-500
            "
          >
            <PenLine size={24} strokeWidth={1.5} />
          </button>
        </div>
      )}

      {/* Compose Overlay */}
      {isComposeOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-6 bg-white/10 backdrop-blur-sm transition-all duration-500 animate-[fadeIn_0.3s_ease-out]">
          <div className="relative w-full max-w-md bg-white/70 backdrop-blur-xl border border-white/60 shadow-2xl rounded-[32px] p-6 animate-[scaleIn_0.4s_cubic-bezier(0.16,1,0.3,1)]">
            
            {/* Close Button */}
            <button 
              onClick={() => setIsComposeOpen(false)}
              className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={20} />
            </button>

            <h3 className="text-lg font-medium text-slate-600 mb-6 pl-1">分享一个想法...</h3>

            <textarea
              className="w-full h-32 bg-transparent text-slate-700 text-lg font-light placeholder:text-slate-400/50 resize-none focus:outline-none"
              placeholder="此刻你在想什么？轻轻说出来吧。"
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              autoFocus
            />

            <div className="flex justify-end mt-4">
              <button
                onClick={handleSubmit}
                disabled={!newContent.trim()}
                className={`
                  px-6 py-2.5 rounded-full font-medium text-sm transition-all duration-300
                  ${newContent.trim() 
                    ? 'bg-gradient-to-r from-purple-300 to-pink-300 text-white shadow-md hover:shadow-lg transform hover:-translate-y-0.5' 
                    : 'bg-slate-200/50 text-slate-400 cursor-not-allowed'}
                `}
              >
                发布
              </button>
            </div>
          </div>
        </div>
      )}
      
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
      `}</style>
    </div>
  );
};
