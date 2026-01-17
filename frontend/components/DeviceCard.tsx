import React from 'react';
import { DeviceStatus } from '../types';

interface DeviceCardProps {
  status: DeviceStatus;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({ status }) => {
  return (
    <div
      className="w-full bg-white/40 backdrop-blur-xl border border-white/50 shadow-[0_8px_32px_-10px_rgba(0,0,0,0.01)] rounded-[24px] p-6 mb-6 flex flex-col items-start gap-5 opacity-0 animate-[fadeSlideUp_1s_cubic-bezier(0.2,0.8,0.2,1)_forwards]"
      style={{ animationDelay: '150ms' }}
    >
      {/* Module Title */}
      <span className="text-[10px] font-semibold tracking-[0.2em] text-slate-400/40 uppercase ml-1">
        My Device
      </span>

      <div className="w-full flex items-center justify-between pl-1">
        {/* Connection Info */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full ${status.isConnected ? 'bg-purple-300' : 'bg-slate-300'}`} />
            <span className={`text-[15px] font-medium tracking-wide ${status.isConnected ? 'text-slate-600' : 'text-slate-400'}`}>
              {status.isConnected ? "Connected" : "Not connected"}
            </span>
          </div>
          <span className="text-xs font-light text-slate-400/60 pl-3.5">
            {status.deviceName}
          </span>
        </div>

        {/* Battery Info */}
        <div className="flex flex-col items-end gap-2.5">
           <span className="text-[11px] font-medium text-slate-400/60 tracking-wider">
             Battery · {status.batteryLevel}%
           </span>
           
           {/* Minimalist Battery Capsule */}
           <div className="relative w-16 h-2 bg-white/50 rounded-full overflow-hidden shadow-inner ring-1 ring-white/40">
             <div
               className="absolute top-0 left-0 h-full rounded-full bg-gradient-to-r from-purple-200 to-pink-200 transition-all duration-1000 ease-out"
               style={{ width: `${status.batteryLevel}%` }}
             />
           </div>
        </div>
      </div>
    </div>
  );
};