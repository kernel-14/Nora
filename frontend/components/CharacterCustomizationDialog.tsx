import React, { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, Check, History, Plus } from 'lucide-react';
import { apiService } from '../services/api';

interface CharacterCustomizationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (preferences: CharacterPreferences) => Promise<void>;
  onSelectHistory: (imageUrl: string) => void;
  currentPreferences?: CharacterPreferences;
  currentImageUrl?: string;
}

export interface CharacterPreferences {
  color: string;
  personality: string;
  appearance: string;
  role: string;
}

interface HistoricalImage {
  filename: string;
  url: string;
  color: string;
  personality: string;
  timestamp: string;
  created_at: number;
  size: number;
}

const COLOR_OPTIONS = [
  { value: '温暖粉', label: '温暖粉', color: 'bg-pink-200' },
  { value: '天空蓝', label: '天空蓝', color: 'bg-blue-200' },
  { value: '薄荷绿', label: '薄荷绿', color: 'bg-green-200' },
  { value: '奶油黄', label: '奶油黄', color: 'bg-yellow-200' },
  { value: '薰衣草紫', label: '薰衣草紫', color: 'bg-purple-200' },
  { value: '珊瑚橙', label: '珊瑚橙', color: 'bg-orange-200' },
  { value: '纯白', label: '纯白', color: 'bg-white border border-gray-300' },
  { value: '浅灰', label: '浅灰', color: 'bg-gray-200' },
];

const PERSONALITY_OPTIONS = [
  { value: '活泼', label: '活泼', emoji: '😄' },
  { value: '温柔', label: '温柔', emoji: '😊' },
  { value: '聪明', label: '聪明', emoji: '🤓' },
  { value: '慵懒', label: '慵懒', emoji: '😴' },
  { value: '勇敢', label: '勇敢', emoji: '💪' },
  { value: '害羞', label: '害羞', emoji: '😳' },
];

const APPEARANCE_OPTIONS = [
  { value: '戴眼镜', label: '戴眼镜', emoji: '👓' },
  { value: '戴帽子', label: '戴帽子', emoji: '🎩' },
  { value: '戴围巾', label: '戴围巾', emoji: '🧣' },
  { value: '戴蝴蝶结', label: '戴蝴蝶结', emoji: '🎀' },
  { value: '无配饰', label: '无配饰', emoji: '✨' },
];

const ROLE_OPTIONS = [
  { value: '陪伴式朋友', label: '陪伴式朋友', emoji: '🤝' },
  { value: '温柔照顾型长辈', label: '温柔照顾型长辈', emoji: '🤗' },
  { value: '引导型老师', label: '引导型老师', emoji: '👨‍🏫' },
];

export const CharacterCustomizationDialog: React.FC<CharacterCustomizationDialogProps> = ({
  isOpen,
  onClose,
  onGenerate,
  onSelectHistory,
  currentPreferences,
  currentImageUrl,
}) => {
  const [mode, setMode] = useState<'history' | 'create'>('history');
  const [preferences, setPreferences] = useState<CharacterPreferences>({
    color: '温暖粉',
    personality: '温柔',
    appearance: '无配饰',
    role: '陪伴式朋友',
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [historyImages, setHistoryImages] = useState<HistoricalImage[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedHistoryImage, setSelectedHistoryImage] = useState<string | null>(null);

  useEffect(() => {
    if (currentPreferences) {
      setPreferences(currentPreferences);
    }
  }, [currentPreferences]);

  useEffect(() => {
    if (isOpen && mode === 'history') {
      loadHistory();
    }
  }, [isOpen, mode]);

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await apiService.getCharacterHistory();
      setHistoryImages(response.images);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSelectHistoryImage = async (image: HistoricalImage) => {
    setSelectedHistoryImage(image.filename);
    try {
      const response = await apiService.selectCharacter(image.filename);
      onSelectHistory(response.image_url);
      setTimeout(() => {
        onClose();
        setMode('history');
        setStep(1);
        setError(null);
        setSelectedHistoryImage(null);
      }, 500);
    } catch (error: any) {
      console.error('Failed to select character:', error);
      setError(error.message || '选择失败，请重试');
      setSelectedHistoryImage(null);
    }
  };

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      await onGenerate(preferences);
      setTimeout(() => {
        onClose();
        setMode('history');
        setStep(1);
        setError(null);
      }, 1000);
    } catch (error: any) {
      console.error('Failed to generate character:', error);
      
      let errorMessage = '生成失败，请重试';
      
      if (error.message) {
        if (error.message.includes('MiniMax API 未配置')) {
          errorMessage = 'MiniMax API 未配置，请在 .env 文件中配置 MINIMAX_API_KEY';
        } else if (error.message.includes('invalid api key')) {
          errorMessage = 'API 密钥无效，请检查 MINIMAX_API_KEY 配置';
        } else if (error.message.includes('配额不足')) {
          errorMessage = 'API 配额不足，请充值或等待配额恢复';
        } else if (error.message.includes('timeout') || error.message.includes('超时')) {
          errorMessage = '请求超时，图像生成时间较长（约60-90秒），请耐心等待或稍后重试';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          errorMessage = '网络连接失败，请检查：\n1. 后端服务是否运行\n2. 网络连接是否正常\n3. 防火墙是否允许访问';
        } else {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const renderHistoryView = () => (
    <div className="space-y-4">
      {loadingHistory ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={32} className="animate-spin text-purple-400" />
        </div>
      ) : historyImages.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-400 mb-4">还没有历史形象</p>
          <button
            onClick={() => setMode('create')}
            className="
              px-6 py-3 rounded-2xl
              bg-gradient-to-br from-purple-400 to-pink-400
              hover:from-purple-500 hover:to-pink-500
              text-white font-medium
              transition-all duration-200
              hover:scale-105 active:scale-95
            "
          >
            创建第一个形象
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 max-h-[400px] overflow-y-auto pr-2">
          {historyImages.map((image) => (
            <button
              key={image.filename}
              onClick={() => handleSelectHistoryImage(image)}
              disabled={selectedHistoryImage === image.filename}
              className={`
                relative p-3 rounded-2xl bg-white/80
                hover:bg-white hover:scale-105
                transition-all duration-200
                ${selectedHistoryImage === image.filename ? 'opacity-50' : ''}
              `}
            >
              <img
                src={image.url}
                alt={`${image.color} ${image.personality}`}
                className="w-full aspect-square rounded-xl object-cover mb-2"
              />
              <div className="text-xs text-slate-600 space-y-0.5">
                <p>🎨 {image.color}</p>
                <p>😊 {image.personality}</p>
              </div>
              {selectedHistoryImage === image.filename && (
                <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-2xl">
                  <Loader2 size={24} className="animate-spin text-purple-400" />
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-3">选择颜色</h4>
        <div className="grid grid-cols-4 gap-3">
          {COLOR_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setPreferences({ ...preferences, color: option.value })}
              className={`
                relative p-3 rounded-xl transition-all duration-200
                ${preferences.color === option.value
                  ? 'ring-2 ring-purple-400 scale-105'
                  : 'hover:scale-105'
                }
              `}
            >
              <div className={`w-full h-12 rounded-lg ${option.color}`} />
              <p className="text-xs text-slate-600 mt-2">{option.label}</p>
              {preferences.color === option.value && (
                <div className="absolute top-1 right-1 w-5 h-5 bg-purple-400 rounded-full flex items-center justify-center">
                  <Check size={12} className="text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-3">选择性格</h4>
        <div className="grid grid-cols-3 gap-3">
          {PERSONALITY_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setPreferences({ ...preferences, personality: option.value })}
              className={`
                relative p-3 rounded-xl bg-white/80 transition-all duration-200
                ${preferences.personality === option.value
                  ? 'ring-2 ring-purple-400 scale-105'
                  : 'hover:scale-105'
                }
              `}
            >
              <div className="text-2xl mb-1">{option.emoji}</div>
              <p className="text-xs text-slate-600">{option.label}</p>
              {preferences.personality === option.value && (
                <div className="absolute top-1 right-1 w-5 h-5 bg-purple-400 rounded-full flex items-center justify-center">
                  <Check size={12} className="text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-3">选择外观</h4>
        <div className="grid grid-cols-3 gap-3">
          {APPEARANCE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setPreferences({ ...preferences, appearance: option.value })}
              className={`
                relative p-3 rounded-xl bg-white/80 transition-all duration-200
                ${preferences.appearance === option.value
                  ? 'ring-2 ring-purple-400 scale-105'
                  : 'hover:scale-105'
                }
              `}
            >
              <div className="text-2xl mb-1">{option.emoji}</div>
              <p className="text-xs text-slate-600">{option.label}</p>
              {preferences.appearance === option.value && (
                <div className="absolute top-1 right-1 w-5 h-5 bg-purple-400 rounded-full flex items-center justify-center">
                  <Check size={12} className="text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-3">选择角色</h4>
        <div className="grid grid-cols-1 gap-3">
          {ROLE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setPreferences({ ...preferences, role: option.value })}
              className={`
                relative p-4 rounded-xl bg-white/80 transition-all duration-200
                flex items-center gap-3
                ${preferences.role === option.value
                  ? 'ring-2 ring-purple-400 scale-105'
                  : 'hover:scale-105'
                }
              `}
            >
              <div className="text-2xl">{option.emoji}</div>
              <p className="text-sm text-slate-700">{option.label}</p>
              {preferences.role === option.value && (
                <div className="absolute top-3 right-3 w-5 h-5 bg-purple-400 rounded-full flex items-center justify-center">
                  <Check size={12} className="text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="
      fixed inset-0 z-[100]
      flex items-center justify-center
      bg-black/30 backdrop-blur-sm
      animate-[fadeIn_0.3s_ease-out]
      p-4
    ">
      <div className="
        relative w-full max-w-lg
        bg-gradient-to-br from-white/95 to-purple-50/95
        backdrop-blur-xl
        rounded-3xl shadow-2xl
        border border-white/50
        p-6
        animate-[slideUp_0.3s_ease-out]
        max-h-[90vh]
        overflow-y-auto
      ">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Sparkles className="text-purple-400" size={20} />
            <h3 className="text-lg font-medium text-slate-700">
              AI 形象定制
            </h3>
          </div>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="
              p-2 rounded-full
              text-slate-400 hover:text-slate-600
              hover:bg-white/50
              transition-all duration-200
              disabled:opacity-50
            "
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('history')}
            className={`
              flex-1 flex items-center justify-center gap-2
              px-4 py-2 rounded-xl
              transition-all duration-200
              ${mode === 'history'
                ? 'bg-purple-400 text-white'
                : 'bg-white/80 text-slate-600 hover:bg-white'
              }
            `}
          >
            <History size={16} />
            <span className="text-sm">历史形象</span>
          </button>
          <button
            onClick={() => {
              setMode('create');
              setStep(1);
            }}
            className={`
              flex-1 flex items-center justify-center gap-2
              px-4 py-2 rounded-xl
              transition-all duration-200
              ${mode === 'create'
                ? 'bg-purple-400 text-white'
                : 'bg-white/80 text-slate-600 hover:bg-white'
              }
            `}
          >
            <Plus size={16} />
            <span className="text-sm">生成新形象</span>
          </button>
        </div>

        {mode === 'create' && currentImageUrl && (
          <div className="mb-6 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl border border-purple-100">
            <div className="flex items-center gap-4">
              <img
                src={currentImageUrl}
                alt="Current character"
                className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-700 mb-1">当前形象</p>
                <div className="text-xs text-slate-500 space-y-0.5">
                  <p>🎨 {preferences.color}</p>
                  <p>😊 {preferences.personality}</p>
                  <p>✨ {preferences.appearance}</p>
                  <p>🎭 {preferences.role}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {mode === 'history' ? (
          renderHistoryView()
        ) : (
          <>
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${step === 1 ? 'bg-purple-400 text-white' : 'bg-white/80 text-slate-400'}
              `}>
                1
              </div>
              <div className="w-12 h-0.5 bg-slate-200" />
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${step === 2 ? 'bg-purple-400 text-white' : 'bg-white/80 text-slate-400'}
              `}>
                2
              </div>
            </div>

            {step === 1 ? renderStep1() : renderStep2()}

            <div className="flex gap-3 mt-6">
              {step === 2 && (
                <button
                  onClick={() => setStep(1)}
                  disabled={isGenerating}
                  className="
                    flex-1 px-4 py-3 rounded-2xl
                    bg-white/80 text-slate-600
                    hover:bg-white
                    transition-all duration-200
                    disabled:opacity-50
                  "
                >
                  上一步
                </button>
              )}
              
              {step === 1 ? (
                <button
                  onClick={() => setStep(2)}
                  className="
                    flex-1 px-4 py-3 rounded-2xl
                    bg-gradient-to-br from-purple-400 to-pink-400
                    hover:from-purple-500 hover:to-pink-500
                    text-white font-medium
                    transition-all duration-200
                    hover:scale-105 active:scale-95
                  "
                >
                  下一步
                </button>
              ) : (
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="
                    flex-1 flex items-center justify-center gap-2
                    px-4 py-3 rounded-2xl
                    bg-gradient-to-br from-purple-400 to-pink-400
                    hover:from-purple-500 hover:to-pink-500
                    text-white font-medium
                    transition-all duration-200
                    disabled:opacity-50
                    hover:scale-105 active:scale-95
                  "
                >
                  {isGenerating ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>生成中...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      <span>{currentImageUrl ? '重新生成' : '生成形象'}</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-600 text-center">{error}</p>
          </div>
        )}

        <p className="text-xs text-slate-400 text-center mt-4">
          {mode === 'history'
            ? '点击历史形象即可切换，或创建新形象'
            : isGenerating
            ? '正在生成你的专属 AI 形象，请稍候（约 30-60 秒）...'
            : currentImageUrl
            ? '修改选项后点击"重新生成"更新形象'
            : '选择你喜欢的风格，生成专属的 AI 陪伴形象'
          }
        </p>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
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
