
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Download, Trash2, Plus, MessageSquare, Sparkles, Zap, X as XIcon } from 'lucide-react';
import type { ChatHistory } from '../types';

interface SidebarProps {
  isOpen: boolean;
  chatHistories: ChatHistory[];
  currentChatId: string | null;
  onNewChat: () => void;
  onLoadChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  onExportChat: () => void;
  onClearHistory: () => void;
  messagesCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  chatHistories,
  currentChatId,
  onNewChat,
  onLoadChat,
  onDeleteChat,
  onExportChat,
  onClearHistory,
  messagesCount,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          exit={{ x: -300 }}
          transition={{ type: 'spring', damping: 20 }}
          className="w-80 backdrop-blur-xl bg-white/80 dark:bg-slate-900/80 border-r border-white/20 dark:border-purple-500/20 flex flex-col relative z-10 shadow-2xl"
        >
          <div className="p-6 border-b border-white/20 dark:border-purple-500/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-xl blur-lg opacity-50"></div>
                <div className="relative bg-gradient-to-r from-purple-500 to-cyan-500 p-2 rounded-xl">
                  <Bot className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h2 className="font-bold text-gray-900 dark:text-white bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                  AI Support Agent
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Powered by Intelligence</p>
              </div>
            </div>
            
            <button
              onClick={onNewChat}
              className="w-full relative group overflow-hidden px-6 py-3 rounded-xl font-medium text-white transition-all duration-300 hover:scale-105"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500 transition-all duration-300 group-hover:scale-110"></div>
              <div className="relative flex items-center justify-center gap-2">
                <Plus className="w-5 h-5" />
                <span>New Conversation</span>
                <Sparkles className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3 flex items-center gap-2">
              <Zap className="w-3 h-3" />
              Recent Chats
            </h3>
            <div className="space-y-2">
              {chatHistories.map(chat => (
                <motion.div
                  key={chat.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`relative group w-full text-left p-4 rounded-xl transition-all duration-300 backdrop-blur-sm ${
                    currentChatId === chat.id
                      ? 'bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-400/50 dark:border-cyan-400/50 shadow-lg'
                      : 'bg-white/50 dark:bg-slate-800/50 hover:bg-white/70 dark:hover:bg-slate-800/70 border border-transparent'
                  }`}
                >
                  <button
                    onClick={() => onLoadChat(chat.id)}
                    className="w-full"
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1 p-1.5 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-lg">
                        <MessageSquare className="w-3.5 h-3.5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {chat.title}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {new Date(chat.lastUpdated).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteChat(chat.id);
                    }}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-2 hover:bg-red-500/20 rounded-lg transition-all"
                  >
                    <XIcon className="w-4 h-4 text-red-500" />
                  </button>
                </motion.div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-white/20 dark:border-purple-500/20 space-y-2">
            <button
              onClick={onExportChat}
              disabled={messagesCount === 0}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 backdrop-blur-sm bg-white/50 dark:bg-slate-800/50 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-white/70 dark:hover:bg-slate-800/70 transition-all duration-300 disabled:opacity-50 border border-white/20 dark:border-slate-700/50"
            >
              <Download className="w-4 h-4" />
              Export Chat
            </button>
            <button
              onClick={onClearHistory}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 backdrop-blur-sm bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 rounded-xl hover:bg-red-500/20 dark:hover:bg-red-500/30 transition-all duration-300 border border-red-500/20"
            >
              <Trash2 className="w-4 h-4" />
              Clear History
            </button>
            <div className="text-xs text-center text-gray-500 dark:text-gray-400 pt-3 font-mono">
              <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent font-bold">
                inextlabs.ai
              </span>
              <span className="mx-2">•</span>
              v1.0.0
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};