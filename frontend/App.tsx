import React, { useState, useEffect } from 'react';
import { AIEntity } from './components/AIEntity';
import { TopActions } from './components/TopActions';
import { BottomNav } from './components/BottomNav';
import { CustomizationButton } from './components/CustomizationButton';
import { CharacterCustomizationDialog, CharacterPreferences } from './components/CharacterCustomizationDialog';
import { ChatDialog } from './components/ChatDialog';
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

// Mock Data: Records - 丰富多样的记录数据
const generateMockRecords = (): RecordItem[] => {
  const now = Date.now();
  const hour = 60 * 60 * 1000;
  const day = 24 * hour;
  
  return [
    // 今天 - 早晨
    {
      id: '1',
      content: "早上6点醒来，窗外的鸟鸣声特别清脆。新的一天，充满期待。",
      createdAt: now - hour * 2, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '2',
      content: "晨跑时看到日出，天空从深蓝渐变到橙粉色，美得让人想哭。",
      createdAt: now - hour * 1.5, 
      sourceType: RecordSource.VOICE
    },
    // 今天 - 上午
    {
      id: '3',
      content: "咖啡店里的音乐很好听，是一首法语歌。要记得回去搜一下。",
      createdAt: now - hour, 
      sourceType: RecordSource.INSPIRATION
    },
    {
      id: '4',
      content: "工作会议上提出的方案被采纳了，同事们的认可让我很开心。",
      createdAt: now - hour * 0.5, 
      sourceType: RecordSource.MOOD
    },
    // 昨天 - 下午
    {
      id: '5',
      content: "午后的阳光透过百叶窗，在桌上投下一道道光影。时间仿佛静止了。",
      createdAt: now - day - hour * 6, 
      sourceType: RecordSource.MANUAL
    },
    {
      id: '6',
      content: "突然想到：如果每个人的记忆都能变成一本书，那会是什么样子？",
      createdAt: now - day - hour * 5, 
      sourceType: RecordSource.INSPIRATION
    },
    // 昨天 - 傍晚
    {
      id: '7',
      content: "下班路上遇到一只流浪猫，蹲下来和它对视了很久。它的眼睛很清澈。",
      createdAt: now - day - hour * 2, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '8',
      content: "晚餐做了番茄炒蛋，虽然简单，但吃得很满足。生活的幸福就是这样。",
      createdAt: now - day - hour, 
      sourceType: RecordSource.MOOD
    },
    // 前天 - 全天
    {
      id: '9',
      content: "今天有点焦虑，deadline临近，但还有很多工作没完成。深呼吸，一步一步来。",
      createdAt: now - day * 2 - hour * 8, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '10',
      content: "中午和老朋友视频通话，虽然各自忙碌，但友谊依然温暖。",
      createdAt: now - day * 2 - hour * 6, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '11',
      content: "读到一句话：'不要因为走得太远，而忘记为什么出发。' 很有共鸣。",
      createdAt: now - day * 2 - hour * 3, 
      sourceType: RecordSource.MANUAL
    },
    {
      id: '12',
      content: "晚上加班到很晚，但看到项目进展顺利，疲惫中带着一丝成就感。",
      createdAt: now - day * 2 - hour, 
      sourceType: RecordSource.MOOD
    },
    // 三天前
    {
      id: '13',
      content: "周末去了郊外，看到一大片向日葵田。金黄色的花海，治愈了整个人。",
      createdAt: now - day * 3 - hour * 10, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '14',
      content: "在书店翻到一本旧书，扉页上有人写的字：'愿你永远保持好奇心'。",
      createdAt: now - day * 3 - hour * 7, 
      sourceType: RecordSource.INSPIRATION
    },
    {
      id: '15',
      content: "下午茶时间，点了一块抹茶蛋糕。甜食真的能让心情变好。",
      createdAt: now - day * 3 - hour * 4, 
      sourceType: RecordSource.MOOD
    },
    // 四天前
    {
      id: '16',
      content: "今天状态不太好，做什么都提不起劲。也许只是需要好好休息一下。",
      createdAt: now - day * 4 - hour * 9, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '17',
      content: "妈妈打电话来，聊了很久。她说最近在学广场舞，听起来很开心。",
      createdAt: now - day * 4 - hour * 5, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '18',
      content: "晚上看了一部老电影，《天使爱美丽》。生活需要一些小确幸和浪漫。",
      createdAt: now - day * 4 - hour * 2, 
      sourceType: RecordSource.MANUAL
    },
    // 五天前
    {
      id: '19',
      content: "早起去菜市场，看到各种新鲜的蔬菜水果，感受到生活的烟火气。",
      createdAt: now - day * 5 - hour * 11, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '20',
      content: "灵感：设计一个'慢生活'主题的摄影集，记录日常中被忽略的美好瞬间。",
      createdAt: now - day * 5 - hour * 8, 
      sourceType: RecordSource.INSPIRATION
    },
    {
      id: '21',
      content: "下午在公园散步，看到一对老夫妻手牵手。希望自己老了也能这样。",
      createdAt: now - day * 5 - hour * 4, 
      sourceType: RecordSource.VOICE
    },
    // 六天前
    {
      id: '22',
      content: "工作上遇到了一些挫折，有点沮丧。但转念一想，这也是成长的机会。",
      createdAt: now - day * 6 - hour * 10, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '23',
      content: "中午吃饭时，餐厅放的背景音乐是《月亮代表我的心》，突然很想家。",
      createdAt: now - day * 6 - hour * 6, 
      sourceType: RecordSource.MANUAL
    },
    {
      id: '24',
      content: "晚上和室友一起做饭，虽然厨艺不精，但笑声不断。这就是生活的乐趣。",
      createdAt: now - day * 6 - hour * 2, 
      sourceType: RecordSource.VOICE
    },
    // 一周前
    {
      id: '25',
      content: "今天是周一，新的一周开始。给自己定个小目标：每天进步一点点。",
      createdAt: now - day * 7 - hour * 9, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '26',
      content: "路过花店，买了一束雏菊。白色的花瓣，简单却很美。",
      createdAt: now - day * 7 - hour * 5, 
      sourceType: RecordSource.MANUAL
    },
    {
      id: '27',
      content: "晚上写日记时想到：记录生活不是为了回忆，而是为了更好地活在当下。",
      createdAt: now - day * 7 - hour * 1, 
      sourceType: RecordSource.INSPIRATION
    },
    // 更早之前
    {
      id: '28',
      content: "雨后的街道，空气中弥漫着泥土的清香。这是大自然的馈赠。",
      createdAt: now - day * 10 - hour * 7, 
      sourceType: RecordSource.VOICE
    },
    {
      id: '29',
      content: "完成了一个困扰很久的难题，那种豁然开朗的感觉太棒了！",
      createdAt: now - day * 12 - hour * 4, 
      sourceType: RecordSource.MOOD
    },
    {
      id: '30',
      content: "深夜听歌，突然被一句歌词击中：'我们都在时光里跌跌撞撞地成长'。",
      createdAt: now - day * 14 - hour * 2, 
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

// Mock Data: Moods - 包含所有情绪类型
const generateMockMoods = (): MoodItem[] => {
  const now = Date.now();
  const hour = 60 * 60 * 1000;
  return [
    // HAPPY - 开心
    {
      id: 'm1',
      type: MoodType.HAPPY,
      date: now - hour * 2,
      intensity: 0.9,
      x: 25,
      y: 30
    },
    {
      id: 'm2',
      type: MoodType.HAPPY,
      date: now - hour * 5,
      intensity: 0.7,
      x: 70,
      y: 25
    },
    // CALM - 平静
    {
      id: 'm3',
      type: MoodType.CALM,
      date: now - hour * 1,
      intensity: 0.8,
      x: 35,
      y: 45
    },
    {
      id: 'm4',
      type: MoodType.CALM,
      date: now - hour * 8,
      intensity: 0.6,
      x: 55,
      y: 60
    },
    {
      id: 'm5',
      type: MoodType.CALM,
      date: now - hour * 12,
      intensity: 0.75,
      x: 20,
      y: 70
    },
    // TIRED - 疲惫
    {
      id: 'm6',
      type: MoodType.TIRED,
      date: now - hour * 3,
      intensity: 0.5,
      x: 65,
      y: 50
    },
    {
      id: 'm7',
      type: MoodType.TIRED,
      date: now - hour * 10,
      intensity: 0.4,
      x: 45,
      y: 75
    },
    // ANXIOUS - 焦虑
    {
      id: 'm8',
      type: MoodType.ANXIOUS,
      date: now - hour * 4,
      intensity: 0.6,
      x: 80,
      y: 40
    },
    {
      id: 'm9',
      type: MoodType.ANXIOUS,
      date: now - hour * 6,
      intensity: 0.55,
      x: 30,
      y: 55
    },
    // HOPEFUL - 充满希望
    {
      id: 'm10',
      type: MoodType.HOPEFUL,
      date: now,
      intensity: 0.85,
      x: 50,
      y: 35
    },
    {
      id: 'm11',
      type: MoodType.HOPEFUL,
      date: now - hour * 7,
      intensity: 0.7,
      x: 75,
      y: 65
    },
    {
      id: 'm12',
      type: MoodType.HOPEFUL,
      date: now - hour * 11,
      intensity: 0.65,
      x: 40,
      y: 20
    }
  ];
};

// Mock Data: Inspirations - 丰富的灵感数据
const generateMockInspirations = (): InspirationItem[] => {
  const now = Date.now();
  const hour = 60 * 60 * 1000;
  const day = 24 * hour;
  return [
    {
      id: 'i1',
      content: "如果云朵只是地球在做梦呢？",
      createdAt: now - hour * 2,
      tags: ['随想', '自然']
    },
    {
      id: 'i2',
      content: "设计概念：一个不显示数字的时钟，只用颜色代表一天的能量。",
      createdAt: now - hour * 5,
      tags: ['设计', '创意']
    },
    {
      id: 'i3',
      content: "旧书和咖啡的香气，是时光最温柔的记忆。",
      createdAt: now - hour * 8,
      tags: ['生活', '随想']
    },
    {
      id: 'i4',
      content: "记得在接电话前深呼吸，给自己三秒钟的准备时间。",
      createdAt: now - day,
      tags: ['提醒', '生活']
    },
    {
      id: 'i5',
      content: "也许每个人都是一座岛屿，而友谊是连接彼此的桥梁。",
      createdAt: now - day - hour * 3,
      tags: ['随想', '友情']
    },
    {
      id: 'i6',
      content: "学习新技能时，不要害怕犯错，错误是成长的阶梯。",
      createdAt: now - day * 2,
      tags: ['学习', '成长']
    },
    {
      id: 'i7',
      content: "工作灵感：用番茄工作法，25分钟专注，5分钟放松。",
      createdAt: now - day * 2 - hour * 4,
      tags: ['工作', '提醒']
    },
    {
      id: 'i8',
      content: "雨后的空气里藏着大地的秘密。",
      createdAt: now - day * 3,
      tags: ['自然', '随想']
    },
    {
      id: 'i9',
      content: "创意想法：设计一个记录每天小确幸的应用。",
      createdAt: now - day * 3 - hour * 6,
      tags: ['创意', '设计']
    },
    {
      id: 'i10',
      content: "真正的朋友，是那个在你沉默时也能理解你的人。",
      createdAt: now - day * 4,
      tags: ['友情', '生活']
    },
    {
      id: 'i11',
      content: "每天写三件感恩的事，心态会慢慢变得更积极。",
      createdAt: now - day * 5,
      tags: ['成长', '提醒']
    },
    {
      id: 'i12',
      content: "工作中遇到困难时，试着换个角度思考问题。",
      createdAt: now - day * 5 - hour * 2,
      tags: ['工作', '成长']
    },
    {
      id: 'i13',
      content: "学习笔记：费曼学习法 - 用简单的语言解释复杂的概念。",
      createdAt: now - day * 6,
      tags: ['学习', '工作']
    },
    {
      id: 'i14',
      content: "窗外的鸟鸣声，是大自然送给城市的礼物。",
      createdAt: now - day * 7,
      tags: ['自然', '生活']
    },
    {
      id: 'i15',
      content: "设计理念：少即是多，简洁才是最高级的美。",
      createdAt: now - day * 8,
      tags: ['设计', '随想']
    }
  ];
};

// Mock Data: Todos - 丰富的待办数据
const generateMockTodos = (): TodoItem[] => {
  const now = Date.now();
  const hour = 60 * 60 * 1000;
  const day = 24 * hour;
  return [
    {
      id: 't1',
      title: "慢慢喝一杯水",
      createdAt: now,
      scheduledAt: now + hour / 2,
      isDone: false,
      category: 'health'
    },
    {
      id: 't2',
      title: "读《小王子》20页",
      createdAt: now - hour,
      scheduledAt: now + hour * 2,
      isDone: false,
      category: 'life'
    },
    {
      id: 't3',
      title: "回复小雪关于项目的邮件",
      createdAt: now - hour * 4,
      scheduledAt: now + day,
      isDone: false,
      category: 'work'
    },
    {
      id: 't4',
      title: "整理学习笔记",
      createdAt: now - hour * 6,
      scheduledAt: now + day,
      isDone: false,
      category: 'study'
    },
    {
      id: 't5',
      title: "晚上8点运动30分钟",
      createdAt: now - day,
      scheduledAt: now + hour * 8,
      isDone: false,
      category: 'health'
    },
    {
      id: 't6',
      title: "准备明天的会议材料",
      createdAt: now - day,
      scheduledAt: now + day,
      isDone: false,
      category: 'work'
    },
    {
      id: 't7',
      title: "买鲜花",
      createdAt: now - day,
      isDone: true,
      category: 'life'
    },
    {
      id: 't8',
      title: "完成英语作业",
      createdAt: now - day * 2,
      isDone: true,
      category: 'study'
    },
    {
      id: 't9',
      title: "给植物浇水",
      createdAt: now - day * 2,
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
  const [showChatDialog, setShowChatDialog] = useState(false);
  
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

  // 获取最近的录音记录
  const latestVoiceRecord = records
    .filter(r => r.sourceType === RecordSource.VOICE)
    .sort((a, b) => b.createdAt - a.createdAt)[0]?.content;

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

  const handleTabChange = (tab: Tab) => {
    // 如果有打开的全屏页面，先关闭它
    if (activeActionView) {
      setActiveActionView(null);
    }
    // 然后切换标签
    setCurrentTab(tab);
  };

  const handleOpenChat = () => {
    setShowChatDialog(true);
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
               
               <AIEntity 
                 imageUrl={characterImageUrl}
                 latestRecord={latestVoiceRecord}
                 onGreeting={(greeting) => console.log('AI greeting:', greeting)}
                 onOpenChat={handleOpenChat}
               />
               
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
        
        {/* Bottom Navigation - 始终显示，z-index 最高 */}
        <BottomNav currentTab={currentTab} onTabChange={handleTabChange} />
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

      {/* Chat Dialog */}
      <ChatDialog
        isOpen={showChatDialog}
        onClose={() => setShowChatDialog(false)}
        characterImageUrl={characterImageUrl}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}