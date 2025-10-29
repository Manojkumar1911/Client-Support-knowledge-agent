
import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Moon, Sun, Settings, Menu, X } from 'lucide-react';

interface TopbarProps {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  onToggleTheme: () => void;
  onOpenSettings: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  theme,
  sidebarOpen,
  onToggleSidebar,
  onToggleTheme,
  onOpenSettings,
}) => {
  return (
    <header className="backdrop-blur-xl bg-white/80 dark:bg-slate-900/80 border-b border-white/20 dark:border-purple-500/20 px-4 sm:px-6 py-4 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 sm:gap-4">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onToggleSidebar}
            className="p-2.5 hover:bg-white/50 dark:hover:bg-slate-800/50 rounded-xl transition-all duration-300 backdrop-blur-sm border border-transparent hover:border-purple-400/30"
          >
            {sidebarOpen ? (
              <X className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            ) : (
              <Menu className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            )}
          </motion.button>
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-xl blur-md opacity-50"></div>
              <div className="relative bg-gradient-to-r from-purple-500 to-cyan-500 p-2 rounded-xl">
                <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
            </div>
            <h1 className="text-sm sm:text-xl font-bold bg-gradient-to-r from-purple-600 via-fuchsia-600 to-cyan-600 dark:from-purple-400 dark:via-fuchsia-400 dark:to-cyan-400 bg-clip-text text-transparent">
              <span className="hidden sm:inline">Client Support Knowledge Agent</span>
              <span className="sm:hidden">Support AI</span>
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.1, rotate: 180 }}
            whileTap={{ scale: 0.9 }}
            onClick={onToggleTheme}
            className="p-2.5 hover:bg-white/50 dark:hover:bg-slate-800/50 rounded-xl transition-all duration-300 backdrop-blur-sm border border-transparent hover:border-purple-400/30"
          >
            {theme === 'light' ? (
              <Moon className="w-5 h-5 text-gray-700" />
            ) : (
              <Sun className="w-5 h-5 text-yellow-400" />
            )}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            onClick={onOpenSettings}
            className="p-2.5 hover:bg-white/50 dark:hover:bg-slate-800/50 rounded-xl transition-all duration-300 backdrop-blur-sm border border-transparent hover:border-purple-400/30"
          >
            <Settings className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </motion.button>
        </div>
      </div>
    </header>
  );
};