import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Plus } from 'lucide-react';
import { MoodItem } from '../types';
import { SimpleMoodBubble, MoodData } from './SimpleMoodBubble';
import { PageHeader } from './PageHeader';
import { ChatDialog } from './ChatDialog';
import { apiService } from '../services/api';

interface MoodViewProps {
  items: MoodItem[];
  onClose: () => void;
  characterImageUrl?: string;
  onSendMessage: (message: string) => Promise<string>;
}

interface MoodDetailData extends MoodData {
  // 扩展字段用于详情显示
}

export const MoodView: React.FC<MoodViewProps> = ({ 
  items, 
  onClose, 
  characterImageUrl,
  onSendMessage 
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedMood, setSelectedMood] = useState<MoodDetailData | null>(null);
  const [moodsData, setMoodsData] = useState<MoodData[]>([]);

  // 从后端加载完整的 moods 数据
  useEffect(() => {
    const loadMoodsData = async () => {
      try {
        console.log('🫧 开始加载心情数据...');
        const response = await apiService.getMoods();
        console.log('📊 后端返回的心情数据:', response);
        
        // 只显示最近7天的心情
        const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
        console.log('📅 7天前的时间戳:', new Date(sevenDaysAgo).toISOString());
        
        const recentMoods = response.moods
          .filter((mood: any) => {
            const timestamp = new Date(mood.timestamp).getTime();
            const isRecent = timestamp >= sevenDaysAgo;
            console.log(`  - ${mood.type} (${mood.timestamp}): ${isRecent ? '✅ 显示' : '❌ 过滤'}`);
            return isRecent;
          })
          .map((mood: any) => ({
            id: mood.record_id,
            type: mood.type,
            intensity: mood.intensity,
            timestamp: mood.timestamp,
            keywords: mood.keywords || [],
          }));
        
        console.log('✨ 最终显示的心情数据:', recentMoods);
        console.log(`🎯 共 ${recentMoods.length} 个气泡`);
        setMoodsData(recentMoods);
      } catch (error) {
        console.error('❌ 加载心情数据失败:', error);
        // 使用传入的 items 作为后备
        console.log('🔄 使用后备数据 (items):', items);
        const fallbackMoods = items.map(item => ({
          id: item.id,
          type: item.type,
          intensity: item.intensity * 10,
          timestamp: new Date(item.date).toISOString(),
          keywords: [],
        }));
        console.log('🔄 转换后的后备数据:', fallbackMoods);
        setMoodsData(fallbackMoods);
      }
    };

    loadMoodsData();
  }, [items]);

  const handleMoodClick = useCallback((mood: MoodData) => {
    setSelectedMood(mood as MoodDetailData);
  }, []);

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (days === 1) {
      return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
    }
  };

  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center animate-[fadeIn_0.5s_ease-out]">
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/90 via-pink-50/90 to-white/90 backdrop-blur-xl" />

      {/* Content Layer */}
      <div className="relative z-10 w-full h-full flex flex-col items-center">
        
        {/* 页面头部 */}
        <PageHeader
          title="心情气泡池"
          subtitle="Your emotions, floating freely"
          onBack={onClose}
          onChat={() => setIsChatOpen(true)}
          characterImageUrl={characterImageUrl}
        />

        {/* 物理引擎气泡容器 */}
        <div className="flex-1 w-full max-w-md mx-auto relative overflow-hidden">
          {/* 提示文字 */}
          {moodsData.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-slate-400 text-sm">暂无心情记录</p>
            </div>
          )}

          {/* 物理气泡 */}
          {moodsData.length > 0 && (
            <SimpleMoodBubble
              moods={moodsData}
              onMoodClick={handleMoodClick}
            />
          )}

          {/* 使用说明 */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-center">
            <p className="text-xs text-slate-400 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full">
              💡 点击气泡查看详情 · 拖动气泡互动
            </p>
          </div>
        </div>

        {/* Bottom Floating Action Button */}
        <div className="mb-32 opacity-0 animate-[fadeSlideUp_1s_ease-out_forwards] delay-500">
           <button 
             className="
               group relative flex items-center justify-center w-16 h-16
               bg-white/40 backdrop-blur-xl rounded-full 
               border border-white/50 shadow-lg shadow-purple-100/50
               hover:bg-white/60 hover:scale-105 transition-all duration-700 ease-out
             "
           >
             <Plus size={24} className="text-slate-400 group-hover:text-purple-400 transition-colors duration-500" strokeWidth={1.5} />
           </button>
        </div>

      </div>

      {/* 心情详情弹窗 */}
      {selectedMood && (
        <div className="
          fixed inset-0 z-[200] 
          flex items-center justify-center
          bg-black/30 backdrop-blur-sm
          animate-[fadeIn_0.3s_ease-out]
          p-4
        " onClick={() => setSelectedMood(null)}>
          <div 
            className="
              relative w-full max-w-sm
              bg-gradient-to-br from-white/95 to-purple-50/95
              rounded-3xl shadow-2xl
              border border-white/50
              p-6
              animate-[slideUp_0.3s_ease-out]
            "
            onClick={(e) => e.stopPropagation()}
          >
            {/* 关闭按钮 */}
            <button 
              onClick={() => setSelectedMood(null)}
              className="
                absolute top-4 right-4
                p-2 rounded-full
                bg-white/50 hover:bg-white/70
                text-slate-600 hover:text-slate-800
                transition-all duration-200
              "
            >
              ✕
            </button>

            {/* 内容 */}
            <div className="flex flex-col space-y-4">
              {/* 心情类型 */}
              <div className="text-center">
                <h3 className="text-3xl font-medium text-slate-700 mb-2">
                  {selectedMood.type}
                </h3>
                <p className="text-sm text-slate-500">
                  {formatDate(selectedMood.timestamp)}
                </p>
              </div>

              {/* 强度指示器 */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-slate-600">
                  <span>情绪强度</span>
                  <span className="font-medium">{selectedMood.intensity}/10</span>
                </div>
                <div className="w-full h-3 bg-slate-200/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full transition-all duration-500"
                    style={{ width: `${(selectedMood.intensity / 10) * 100}%` }}
                  />
                </div>
              </div>

              {/* 关键词 */}
              {selectedMood.keywords && selectedMood.keywords.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm text-slate-600 font-medium">关键词</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedMood.keywords.map((keyword, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-purple-100/80 text-purple-700 text-xs rounded-full"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* 提示 */}
              <div className="pt-4 border-t border-slate-200">
                <p className="text-xs text-slate-500 italic text-center">
                  "每一种情绪都值得被记录和珍惜"
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 对话弹窗 */}
      <ChatDialog
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        characterImageUrl={characterImageUrl}
        onSendMessage={onSendMessage}
      />

      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeSlideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeSlideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to { 
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
};