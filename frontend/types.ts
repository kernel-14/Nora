export enum Tab {
  HOME = 'HOME',
  RECORD = 'RECORD',
  COMMUNITY = 'COMMUNITY',
  MINE = 'MINE'
}

export enum MoodAction {
  MOOD = 'MOOD',
  INSPIRATION = 'INSPIRATION',
  TODO = 'TODO'
}

export enum RecordSource {
  MOOD = 'MOOD',
  INSPIRATION = 'INSPIRATION',
  VOICE = 'VOICE',
  MANUAL = 'MANUAL'
}

export enum MoodType {
  HAPPY = 'HAPPY',   // Warm Pink/Coral
  CALM = 'CALM',     // Lavender
  TIRED = 'TIRED',   // Foggy Blue
  ANXIOUS = 'ANXIOUS', // Warm Beige/Grey
  HOPEFUL = 'HOPEFUL' // Creamy Yellow
}

export interface NavItem {
  id: Tab;
  label: string;
  iconName: string;
}

export interface ActionItem {
  id: MoodAction;
  label: string;
  iconName: string;
}

export interface RecordItem {
  id: string;
  content: string;
  createdAt: number; // Unix timestamp
  sourceType: RecordSource;
}

export interface CommunityPost {
  id: string;
  user: {
    name: string;
    avatarColor: string; // Tailwind bg class
  };
  content: string;
  createdAt: number;
  likeCount: number;
  isLiked: boolean;
  commentCount: number;
}

export interface Profile {
  name: string;
  birthday: string; // e.g., "Mar 12"
  moodStatus: string;
  avatarUrl?: string; // Optional image URL
}

export interface DeviceStatus {
  isConnected: boolean;
  batteryLevel: number; // 0-100
  deviceName: string;
}

export interface MoodItem {
  id: string;
  type: MoodType;
  date: number;
  intensity: number; // 0-1 (affects size)
  x?: number; // relative position percentage (optional for random placement)
  y?: number; // relative position percentage
}

export interface InspirationItem {
  id: string;
  content: string;
  createdAt: number;
  tags?: string[];
}

export type TodoCategory = 'study' | 'work' | 'life' | 'health';

export interface TodoItem {
  id: string;
  title: string;
  createdAt: number;
  scheduledAt?: number;
  isDone: boolean;
  category?: TodoCategory;
  location?: string;
  time?: string;
}