import React from 'react';
import { Profile } from '../types';

interface ProfileCardProps {
  profile: Profile;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  return (
    <div
      className="flex flex-col items-center justify-center p-6 mb-8 opacity-0 animate-[fadeSlideUp_1s_cubic-bezier(0.2,0.8,0.2,1)_forwards]"
    >
      {/* Avatar Container */}
      <div className="w-32 h-32 rounded-full mb-6 relative overflow-hidden ring-4 ring-white/30 shadow-[0_10px_40px_-10px_rgba(167,139,250,0.3)]">
        {profile.avatarUrl ? (
          <img src={profile.avatarUrl} alt={profile.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-purple-100 via-pink-100 to-white flex items-center justify-center">
            <span className="text-4xl text-purple-300/50 font-light">{profile.name.charAt(0)}</span>
          </div>
        )}
        
        {/* Subtle shine overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent pointer-events-none" />
      </div>

      {/* Name */}
      <h2 className="text-2xl font-medium text-slate-800/80 mb-1.5 tracking-wide font-sans">
        {profile.name}
      </h2>

      {/* Birthday */}
      <p className="text-[13px] font-light text-slate-400/60 mb-8 tracking-wider uppercase">
        Born on {profile.birthday}
      </p>

      {/* Mood Status Bubble */}
      <div className="px-5 py-2.5 rounded-2xl bg-white/40 backdrop-blur-md border border-white/40 shadow-sm">
        <p className="text-[15px] font-normal text-slate-600/90 italic flex items-center gap-2">
          <span>{profile.moodStatus}</span>
          <span className="text-lg opacity-80">🍃</span>
        </p>
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