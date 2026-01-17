import React from 'react';
import { Profile, DeviceStatus } from '../types';
import { ProfileCard } from './ProfileCard';
import { DeviceCard } from './DeviceCard';

interface MineViewProps {
  profile: Profile;
  deviceStatus: DeviceStatus;
}

export const MineView: React.FC<MineViewProps> = ({ profile, deviceStatus }) => {
  return (
    <div className="w-full h-full flex flex-col pt-12 px-6 pb-32 overflow-y-auto no-scrollbar scroll-smooth">
      {/* Top Spacer for Profile Image */}
      <div className="h-4" />
      
      {/* Profile Section */}
      <ProfileCard profile={profile} />

      {/* Spacer for flow */}
      <div className="h-6" />

      {/* Device Section */}
      <DeviceCard status={deviceStatus} />

      {/* Bottom padding to ensure content isn't hidden by nav */}
      <div className="h-24" />
    </div>
  );
};