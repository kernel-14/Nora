import React, { useState } from 'react';
import { Heart, MessageCircle } from 'lucide-react';
import { CommunityPost } from '../types';

interface CommunityCardProps {
  post: CommunityPost;
  index: number;
}

export const CommunityCard: React.FC<CommunityCardProps> = ({ post, index }) => {
  const [isLiked, setIsLiked] = useState(post.isLiked);
  const [likeCount, setLikeCount] = useState(post.likeCount);

  const handleLike = () => {
    // Optimistic UI update
    const newLikedState = !isLiked;
    setIsLiked(newLikedState);
    setLikeCount(prev => newLikedState ? prev + 1 : prev - 1);
  };

  // Format time strictly relative or simple (e.g., "10 min ago" or "Evening")
  const getTimeString = (timestamp: number) => {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return new Date(timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <div
      className="group relative w-full bg-white/40 backdrop-blur-xl border border-white/50 shadow-[0_8px_32px_-10px_rgba(0,0,0,0.02)] rounded-[24px] p-6 mb-6 transition-all duration-700 hover:bg-white/50"
      style={{
        animation: `fadeSlideUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards`,
        animationDelay: `${index * 150}ms`,
        opacity: 0
      }}
    >
      {/* Top Row: User info (Anonymous) - very subtle */}
      <div className="flex items-center gap-2 mb-3 opacity-60">
        <div className={`w-5 h-5 rounded-full ${post.user.avatarColor} opacity-50`}></div>
        <span className="text-xs font-medium text-slate-500 tracking-wide">{post.user.name}</span>
      </div>

      {/* Content */}
      <div className="relative z-10 mb-4">
        <p className="text-[15px] leading-7 font-normal text-slate-700/80 font-sans whitespace-pre-wrap">
          {post.content}
        </p>
      </div>

      {/* Footer: Interactions + Time */}
      <div className="flex items-center justify-between mt-2">
        <div className="flex items-center gap-6">
          {/* Like Button */}
          <button
            onClick={handleLike}
            className="flex items-center gap-1.5 group/btn transition-transform active:scale-95 focus:outline-none"
          >
            <Heart
              size={18}
              strokeWidth={1.5}
              className={`transition-all duration-500 ${isLiked ? 'fill-pink-300 stroke-pink-300 scale-110' : 'stroke-slate-300 fill-transparent group-hover/btn:stroke-pink-300/50'}`}
            />
            <span className={`text-xs font-medium transition-colors duration-500 ${isLiked ? 'text-pink-300' : 'text-slate-300'}`}>
              {likeCount > 0 ? likeCount : ''}
            </span>
          </button>

          {/* Comment Button (Visual only for now) */}
          <button className="flex items-center gap-1.5 group/btn transition-transform active:scale-95 focus:outline-none">
            <MessageCircle size={18} strokeWidth={1.5} className="stroke-slate-300 transition-colors duration-300 group-hover/btn:stroke-purple-300/50" />
             <span className="text-xs font-medium text-slate-300">
               {post.commentCount > 0 ? post.commentCount : ''}
             </span>
          </button>
        </div>

        {/* Timestamp */}
        <span className="text-[11px] font-light text-slate-400/30 tracking-widest uppercase">
          {getTimeString(post.createdAt)}
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