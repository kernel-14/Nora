import React, { useState, useEffect } from 'react';
import { AIEntity } from './components/AIEntity';
import { TopActions } from './components/TopActions';
import { BottomNav } from './components/BottomNav';
import { CustomizationButton } from './components/CustomizationButton';
import { CharacterCustomizationDialog, CharacterPreferences } from './components/CharacterCustomizationDialog';
import { RecordView } from './components/RecordView';
import { CommunityView } from './components/CommunityView';
import { MineView } from './components/MineView';
import { MoodView } from './components/MoodView';
import { InspirationView } from './components/InspirationView';
import { TodoView } from './components/TodoView';
import { HomeInput } from './components/HomeInput';
import { 
  Tab, 
  MoodAction, 
  RecordItem, 
  RecordSource, 
  CommunityPost, 
  Profile, 
  DeviceStatus,
  MoodItem,
  MoodType,
  InspirationItem,
  TodoItem
} from './types';
import { apiService } from './services/api';
import { 
  transformRecord, 
  transformMood, 
  transformInspiration, 
  transformTodo 
} from './utils/dataTransform';

// Mock Data: Records
const generateMockRecords = (): RecordItem[] => {
  const now = Date.now();
  const day = 24 * 60 * 60 * 1000;
  
  return [
    {
      id: '1',
      content: "今天看云的时候突然感到一阵平静。云朵移动得很慢，提醒我不必着急。",
      createdAt: now - 1000 * 60 * 30, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '2',
      content: "周末的想法：去市中心那家老书店，找一本蓝色封面的书。",
      createdAt: now - 1000 * 60 * 60 * 4, 
      sourceType: RecordSource.INSPIRATION
    },
    {
      id: '3',
      content: "有时候沉默是生活给出的最响亮的答案。我需要学会更多地倾听它。",
      createdAt: now - day, 
      sourceType: RecordSource.MANUAL
    },
    {
      id: '4',
      content: "外面下着大雨。感觉很温馨，但也有点孤独。",
      createdAt: now - day - 1000 * 60 * 60 * 2, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '5',
      content: "记得给妈妈打电话。",
      createdAt: now - day * 2, 
      sourceType: RecordSource.MANUAL
    }
  ];
};

// Mock Data: Community Posts
const generateMockPosts = (): CommunityPost[] => {
  const now = Date.now();
  return [
    {
      id: '101',
      user: { name: '安静的观察者', avatarColor: 'bg-indigo-200' },
      content: "有人也觉得自己在等待一些还没发生的事情吗？这是一种对未来的奇怪怀念。",
      createdAt: now - 1000 * 60 * 10, // 10 mins ago
      likeCount: 12,
      isLiked: false,
      commentCount: 3
    },
    {
      id: '102',
      user: { name: '温柔的灵魂', avatarColor: 'bg-pink-200' },
      content: "泡了一杯茶，看着蒸汽升起看了5分钟。这是我今天最美好的时刻。",
      createdAt: now - 1000 * 60 * 45,
      likeCount: 28,
      isLiked: true,
      commentCount: 5
    },
    {
      id: '103',
      user: { name: '匿名', avatarColor: 'bg-teal-200' },
      content: "今天我试着对自己更温柔一些。这比对别人温柔更难。",
      createdAt: now - 1000 * 60 * 60 * 2,
      likeCount: 45,
      isLiked: false,
      commentCount: 8
    },
     {
      id: '104',
      user: { name: '云中漫步者', avatarColor: 'bg-blue-200' },
      content: "今天的日落特别粉。",
      createdAt: now - 1000 * 60 * 60 * 5,
      likeCount: 8,
      isLiked: false,
      commentCount: 0
    }
  ];
};

// Mock Data: Profile & Device
const mockProfile: Profile = {
  name: "小雅",
  birthday: "3月12日",
  moodStatus: "感觉平静而专注",
};

const mockDeviceStatus: DeviceStatus = {
  isConnected: true,
  batteryLevel: 82,
  deviceName: "心灵伴侣吊坠"
};

// Mock Data: Moods
const generateMockMoods = (): MoodItem[] => {
  const now = Date.now();
  return [
    {
      id: 'm1',
      type: MoodType.CALM,
      date: now,
      intensity: 0.8,
      x: 35, // 35% left
      y: 40  // 40% top
    },
    {
      id: 'm2',
      type: MoodType.HOPEFUL,
      date: now,
      intensity: 0.5,
      x: 65,
      y: 55
    },
    {
      id: 'm3',
      type: MoodType.TIRED,
      date: now,
      intensity: 0.3,
      x: 45,
      y: 65
    }
  ];
};

// Mock Data: Inspirations
const generateMockInspirations = (): InspirationItem[] => {
  const now = Date.now();
  return [
    {
      id: 'i1',
      content: "如果云朵只是地球在做梦呢？",
      createdAt: now - 1000 * 60 * 15,
      tags: ['随想', '自然']
    },
    {
      id: 'i2',
      content: "设计概念：一个不显示数字的时钟，只用颜色代表一天的能量。",
      createdAt: now - 1000 * 60 * 60 * 3,
      tags: ['设计', '创意']
    },
    {
      id: 'i3',
      content: "旧书和咖啡的香气。",
      createdAt: now - 1000 * 60 * 60 * 24 * 2,
      tags: ['生活']
    },
    {
      id: 'i4',
      content: "记得在接电话前深呼吸。",
      createdAt: now - 1000 * 60 * 60 * 24 * 5,
      tags: ['提醒']
    }
  ];
};

// Mock Data: Todos
const generateMockTodos = (): TodoItem[] => {
  const now = Date.now();
  return [
    {
      id: 't1',
      title: "慢慢喝一杯水",
      createdAt: now,
      scheduledAt: now + 1000 * 60 * 30, // 30 mins later
      isDone: false,
      category: 'health'
    },
    {
      id: 't2',
      title: "读《小王子》20页",
      createdAt: now - 1000 * 60 * 60,
      scheduledAt: now + 1000 * 60 * 60 * 2,
      isDone: false,
      category: 'life'
    },
    {
      id: 't3',
      title: "回复小雪关于项目的邮件",
      createdAt: now - 1000 * 60 * 60 * 4,
      scheduledAt: now + 1000 * 60 * 60 * 24, // Tomorrow
      isDone: false,
      category: 'work'
    },
    {
      id: 't4',
      title: "买鲜花",
      createdAt: now - 1000 * 60 * 60 * 24,
      isDone: true,
      category: 'life'
    }
  ];
};

export default function App() {
  const [currentTab, setCurrentTab] = useState<Tab>(Tab.HOME);
  const [records, setRecords] = useState<RecordItem[]>(generateMockRecords());
  const [posts, setPosts] = useState<CommunityPost[]>(generateMockPosts());
  const [moods, setMoods] = useState<MoodItem[]>(generateMockMoods());
  const [inspirations, setInspirations] = useState<InspirationItem[]>(generateMockInspirations());
  const [todos, setTodos] = useState<TodoItem[]>(generateMockTodos());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [characterImageUrl, setCharacterImageUrl] = useState<string | undefined>();
  const [characterPreferences, setCharacterPreferences] = useState<CharacterPreferences | undefined>();
  const [showCustomizationDialog, setShowCustomizationDialog] = useState(false);
  
  // State to manage full-screen action views (like Mood Page)
  const [activeActionView, setActiveActionView] = useState<MoodAction | null>(null);

  // Load data from backend on mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data in parallel
      const [recordsRes, moodsRes, inspirationsRes, todosRes, userConfigRes] = await Promise.all([
        apiService.getRecords().catch(() => ({ records: [] })),
        apiService.getMoods().catch(() => ({ moods: [] })),
        apiService.getInspirations().catch(() => ({ inspirations: [] })),
        apiService.getTodos().catch(() => ({ todos: [] })),
        apiService.getUserConfig().catch(() => null)
      ]);

      // Transform and set data
      if (recordsRes.records.length > 0) {
        setRecords(recordsRes.records.map(transformRecord));
      }
      
      if (moodsRes.moods.length > 0) {
        setMoods(moodsRes.moods.map((m, i) => transformMood(m, i)));
      }
      
      if (inspirationsRes.inspirations.length > 0) {
        setInspirations(inspirationsRes.inspirations.map(transformInspiration));
      }
      
      if (todosRes.todos.length > 0) {
        setTodos(todosRes.todos.map(transformTodo));
      }

      // Set character image
      if (userConfigRes?.character?.image_url) {
        setCharacterImageUrl(userConfigRes.character.image_url);
      }
      
      // Set character preferences
      if (userConfigRes?.character?.preferences) {
        setCharacterPreferences(userConfigRes.character.preferences);
      }

    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load data from server. Using mock data.');
    } finally {
      setLoading(false);
    }
  };

  // Chat with AI
  const handleSendMessage = async (message: string): Promise<string> => {
    try {
      const response = await apiService.chatWithAI(message);
      return response;
    } catch (error) {
      console.error('Failed to chat:', error);
      return '抱歉，我现在有点累了，稍后再聊好吗？';
    }
  };

  // Background gradient configuration
  const bgGradient = "bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-100 via-pink-50 to-blue-50";

  const handleActionClick = (action: MoodAction) => {
    console.log(`Action clicked: ${action}`);
    if (action === MoodAction.MOOD) {
      setActiveActionView(MoodAction.MOOD);
    } else if (action === MoodAction.INSPIRATION) {
      setActiveActionView(MoodAction.INSPIRATION);
    } else if (action === MoodAction.TODO) {
      setActiveActionView(MoodAction.TODO);
    }
  };
  
  const closeActionView = () => {
    setActiveActionView(null);
  };

  const handleAddPost = (content: string) => {
    const newPost: CommunityPost = {
      id: Date.now().toString(),
      user: { name: 'Me', avatarColor: 'bg-purple-300' },
      content: content,
      createdAt: Date.now(),
      likeCount: 0,
      isLiked: false,
      commentCount: 0
    };
    setPosts([newPost, ...posts]);
  };
  
  const handleAddInspiration = async (content: string, isVoice: boolean) => {
    try {
      // 如果是语音，先转换为文字
      if (isVoice) {
        // 这里应该调用语音转文字API
        console.log('Voice input:', content);
      }
      
      // 调用后端API处理灵感
      const response = await apiService.processInput(undefined, content);
      
      // 刷新数据
      await loadAllData();
      
      console.log('Inspiration added:', response);
    } catch (error) {
      console.error('Failed to add inspiration:', error);
      alert('添加灵感失败，请重试');
    }
  };

  const handleAddTodo = () => {
    console.log("Add todo clicked");
    // Placeholder
  };
  
  const handleToggleTodo = async (id: string) => {
    // Optimistic update
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const newStatus = todo.isDone ? 'pending' : 'completed';
    
    setTodos(todos.map(t => 
      t.id === id ? { ...t, isDone: !t.isDone } : t
    ));

    // Update backend
    try {
      await apiService.updateTodoStatus(id, newStatus);
    } catch (err) {
      console.error('Failed to update todo:', err);
      // Revert on error
      setTodos(todos.map(t => 
        t.id === id ? { ...t, isDone: todo.isDone } : t
      ));
    }
  };

  const handleGenerateCharacter = async (preferences: CharacterPreferences) => {
    try {
      console.log('Generating character with preferences:', preferences);
      
      const result = await apiService.generateCharacter(preferences);
      
      console.log('Character generated:', result);
      
      // 更新角色形象
      setCharacterImageUrl(result.image_url);
      setCharacterPreferences(result.preferences);
      
      // 显示成功提示
      alert('AI 形象生成成功！');
      
    } catch (error) {
      console.error('Failed to generate character:', error);
      throw error;
    }
  };

  const isHome = currentTab === Tab.HOME;

  return (
    <div className={`relative w-full h-screen overflow-hidden ${bgGradient} text-slate-700`}>
      {/* Ambient noise texture overlay */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>

      {/* Main Content Area */}
      <main className="relative flex flex-col h-full items-center justify-between">
        
        {/* HOME VIEW */}
        {isHome && !activeActionView && (
          <>
            <TopActions onActionClick={handleActionClick} />
            
            <div className="flex-1 flex flex-col items-center justify-center w-full relative -mt-10">
               <div className="absolute top-10 opacity-60 text-sm font-light tracking-widest text-slate-500 animate-pulse delay-700">
                 I'm here with you
               </div>
               
               <AIEntity imageUrl={characterImageUrl} />
               
               {/* Home Input Component */}
               <div className="mt-8 w-full">
                 <HomeInput onRecordComplete={loadAllData} />
               </div>
            </div>
            
            <CustomizationButton onClick={() => setShowCustomizationDialog(true)} />
          </>
        )}

        {/* RECORD VIEW */}
        {currentTab === Tab.RECORD && !activeActionView && (
          <RecordView items={records} />
        )}

        {/* COMMUNITY VIEW */}
        {currentTab === Tab.COMMUNITY && !activeActionView && (
          <CommunityView posts={posts} onAddPost={handleAddPost} />
        )}
        
        {/* MINE VIEW */}
        {currentTab === Tab.MINE && !activeActionView && (
          <MineView profile={mockProfile} deviceStatus={mockDeviceStatus} />
        )}

        {/* --- FULL SCREEN OVERLAYS --- */}
        
        {/* MOOD PAGE OVERLAY */}
        {activeActionView === MoodAction.MOOD && (
          <MoodView 
            items={moods} 
            onClose={closeActionView}
            characterImageUrl={characterImageUrl}
            onSendMessage={handleSendMessage}
          />
        )}
        
        {/* INSPIRATION PAGE OVERLAY */}
        {activeActionView === MoodAction.INSPIRATION && (
          <InspirationView 
            items={inspirations} 
            onClose={closeActionView} 
            onAdd={handleAddInspiration}
            characterImageUrl={characterImageUrl}
            onSendMessage={handleSendMessage}
          />
        )}
        
        {/* TODO PAGE OVERLAY */}
        {activeActionView === MoodAction.TODO && (
          <TodoView
            items={todos}
            onClose={closeActionView}
            onAdd={handleAddTodo}
            onToggleItem={handleToggleTodo}
            characterImageUrl={characterImageUrl}
            onSendMessage={handleSendMessage}
          />
        )}
        
        {/* Bottom Navigation */}
        <BottomNav currentTab={currentTab} onTabChange={setCurrentTab} />
      </main>

      {/* Character Customization Dialog */}
      <CharacterCustomizationDialog
        isOpen={showCustomizationDialog}
        onClose={() => setShowCustomizationDialog(false)}
        onGenerate={handleGenerateCharacter}
        onSelectHistory={(imageUrl) => {
          setCharacterImageUrl(imageUrl);
        }}
        currentPreferences={characterPreferences}
        currentImageUrl={characterImageUrl}
      />
    </div>
  );
}