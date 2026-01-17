import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Mic, Loader2 } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatDialogProps {
  isOpen: boolean;
  onClose: () => void;
  characterImageUrl?: string;
  onSendMessage: (message: string) => Promise<string>;
}

export const ChatDialog: React.FC<ChatDialogProps> = ({ 
  isOpen, 
  onClose, 
  characterImageUrl,
  onSendMessage 
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好呀~ 我在这里陪着你，有什么想聊的吗？',
      timestamp: Date.now()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 打开时聚焦输入框
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await onSendMessage(inputText);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，我现在有点累了，稍后再聊好吗？',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="
      fixed inset-0 z-[100] 
      flex items-center justify-center
      bg-black/20 backdrop-blur-sm
      animate-[fadeIn_0.3s_ease-out]
    ">
      {/* 对话框容器 */}
      <div className="
        relative w-full max-w-md h-[600px] mx-4
        bg-gradient-to-br from-white/95 to-purple-50/95
        backdrop-blur-xl
        rounded-3xl shadow-2xl
        border border-white/50
        flex flex-col
        animate-[slideUp_0.3s_ease-out]
      ">
        {/* 头部 */}
        <div className="
          flex items-center justify-between
          px-6 py-4
          border-b border-white/50
        ">
          <div className="flex items-center gap-3">
            {/* 角色头像 */}
            {characterImageUrl ? (
              <img 
                src={characterImageUrl} 
                alt="AI Companion" 
                className="w-10 h-10 rounded-full object-cover border-2 border-white shadow-md"
              />
            ) : (
              <div className="
                w-10 h-10 rounded-full 
                bg-gradient-to-br from-purple-200 to-pink-200
                border-2 border-white shadow-md
                flex items-center justify-center
              ">
                <span className="text-lg">🐱</span>
              </div>
            )}
            
            <div>
              <h3 className="text-base font-medium text-slate-700">
                小喵陪伴
              </h3>
              <p className="text-xs text-slate-400">
                在线 · 随时陪你聊天
              </p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="
              p-2 rounded-full
              text-slate-400 hover:text-slate-600
              hover:bg-white/50
              transition-all duration-200
            "
          >
            <X size={20} />
          </button>
        </div>

        {/* 消息列表 */}
        <div className="
          flex-1 overflow-y-auto
          px-6 py-4
          space-y-4
        ">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`
                flex gap-3
                ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}
              `}
            >
              {/* 头像 */}
              {message.role === 'assistant' && (
                <div className="
                  w-8 h-8 rounded-full flex-shrink-0
                  bg-gradient-to-br from-purple-200 to-pink-200
                  flex items-center justify-center
                  text-sm
                ">
                  🐱
                </div>
              )}

              {/* 消息气泡 */}
              <div
                className={`
                  max-w-[75%] px-4 py-2.5 rounded-2xl
                  ${message.role === 'user' 
                    ? 'bg-gradient-to-br from-purple-400 to-pink-400 text-white rounded-tr-sm' 
                    : 'bg-white/80 text-slate-700 rounded-tl-sm'
                  }
                  shadow-sm
                `}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
              </div>

              {/* 用户头像 */}
              {message.role === 'user' && (
                <div className="
                  w-8 h-8 rounded-full flex-shrink-0
                  bg-gradient-to-br from-blue-200 to-cyan-200
                  flex items-center justify-center
                  text-sm
                ">
                  👤
                </div>
              )}
            </div>
          ))}

          {/* 加载指示器 */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="
                w-8 h-8 rounded-full
                bg-gradient-to-br from-purple-200 to-pink-200
                flex items-center justify-center
                text-sm
              ">
                🐱
              </div>
              <div className="
                px-4 py-2.5 rounded-2xl rounded-tl-sm
                bg-white/80
                flex items-center gap-2
              ">
                <Loader2 size={16} className="animate-spin text-purple-400" />
                <span className="text-sm text-slate-400">思考中...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="
          px-6 py-4
          border-t border-white/50
        ">
          <div className="
            flex items-center gap-2
            bg-white/80 rounded-2xl
            px-4 py-2
            border border-white/50
            shadow-sm
          ">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="说点什么吧..."
              disabled={isLoading}
              className="
                flex-1 bg-transparent
                text-sm text-slate-700
                placeholder:text-slate-400
                outline-none
                disabled:opacity-50
              "
            />

            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading}
              className="
                p-2 rounded-full
                bg-gradient-to-br from-purple-400 to-pink-400
                text-white
                hover:from-purple-500 hover:to-pink-500
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                hover:scale-105
              "
            >
              <Send size={16} />
            </button>
          </div>

          <p className="text-xs text-slate-400 text-center mt-2">
            按 Enter 发送，Shift + Enter 换行
          </p>
        </div>
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
