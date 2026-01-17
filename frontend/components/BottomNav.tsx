import React from 'react';
import { Home, NotebookPen, Users, User } from 'lucide-react';
import { Tab } from '../types';

interface BottomNavProps {
  currentTab: Tab;
  onTabChange: (tab: Tab) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentTab, onTabChange }) => {
  const navItems = [
    { id: Tab.HOME, label: '首页', icon: Home },
    { id: Tab.RECORD, label: '记录', icon: NotebookPen },
    { id: Tab.COMMUNITY, label: '社区', icon: Users },
    { id: Tab.MINE, label: '我的', icon: User },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 px-6 pb-6 pt-2">
      <nav className="relative bg-white/70 backdrop-blur-xl shadow-lg shadow-purple-100/50 rounded-3xl flex justify-between items-center px-6 py-4 max-w-md mx-auto ring-1 ring-white/50">
        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className="relative flex flex-col items-center justify-center gap-1 w-12 h-12 transition-all duration-300"
            >
              <div 
                className={`
                  absolute inset-0 rounded-full transition-all duration-500 
                  ${isActive ? 'bg-gradient-to-br from-pink-100 to-purple-100 opacity-100 scale-100' : 'opacity-0 scale-75'}
                `}
              />
              <item.icon 
                size={22} 
                strokeWidth={isActive ? 2 : 1.5}
                className={`relative z-10 transition-colors duration-300 ${isActive ? 'text-purple-600' : 'text-slate-400'}`} 
              />
              <span 
                className={`relative z-10 text-[10px] font-medium transition-colors duration-300 ${isActive ? 'text-purple-700' : 'text-slate-400'}`}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};