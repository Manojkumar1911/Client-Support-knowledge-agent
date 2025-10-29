
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  userId: string;
  apiUrl: string;
  onClose: () => void;
  onUserIdChange: (userId: string) => void;
  onApiUrlChange: (apiUrl: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  userId,
  apiUrl,
  onClose,
  onUserIdChange,
  onApiUrlChange,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="relative backdrop-blur-xl bg-white/90 dark:bg-slate-800/90 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-white/20 dark:border-purple-500/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-cyan-500/10 rounded-3xl"></div>
            <div className="relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-xl blur-md opacity-50"></div>
                  <div className="relative bg-gradient-to-r from-purple-500 to-cyan-500 p-2.5 rounded-xl">
                    <Settings className="w-6 h-6 text-white" />
                  </div>
                </div>
                <h2 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-purple-600 to-cyan-600 dark:from-purple-400 dark:to-cyan-400 bg-clip-text text-transparent">
                  Settings
                </h2>
              </div>
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full"></span>
                    User ID
                  </label>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => onUserIdChange(e.target.value)}
                    className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 dark:bg-slate-700/50 border border-white/20 dark:border-purple-500/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-cyan-500 text-gray-900 dark:text-white transition-all duration-300"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full"></span>
                    API URL
                  </label>
                  <input
                    type="text"
                    value={apiUrl}
                    onChange={(e) => onApiUrlChange(e.target.value)}
                    className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 dark:bg-slate-700/50 border border-white/20 dark:border-purple-500/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-cyan-500 text-gray-900 dark:text-white transition-all duration-300"
                  />
                </div>
              </div>
              <div className="mt-8 flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={onClose}
                  className="flex-1 relative overflow-hidden px-6 py-3 rounded-xl font-medium text-white shadow-lg"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500"></div>
                  <span className="relative">Close</span>
                </motion.button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};