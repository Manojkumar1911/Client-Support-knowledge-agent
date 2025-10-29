import React from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  isLoading,
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/80 dark:bg-slate-900/80 border-t border-white/20 dark:border-purple-500/20 p-4 sm:p-6 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-2 sm:gap-4">
          <div className="flex-1 relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500 rounded-2xl blur-md opacity-0 group-hover:opacity-30 transition-opacity"></div>
            <input
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              disabled={isLoading}
              className="relative w-full px-4 sm:px-6 py-3 sm:py-4 backdrop-blur-sm bg-white/90 dark:bg-slate-800/90 border border-white/20 dark:border-purple-500/20 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-cyan-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 transition-all duration-300 shadow-lg text-sm sm:text-base"
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onSend}
            disabled={!value.trim() || isLoading}
            className="relative px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-medium text-white disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden shadow-xl transition-all duration-300"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500"></div>
            <div className="relative flex items-center gap-2">
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </motion.button>
        </div>
      </div>
    </div>
  );
};