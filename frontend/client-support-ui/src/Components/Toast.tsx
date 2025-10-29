import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ToastProps {
  message: string | null;
}

export const Toast: React.FC<ToastProps> = ({ message }) => {
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 50, scale: 0.9 }}
          className="fixed bottom-8 right-8 z-50"
        >
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl blur-lg opacity-50"></div>
            <div className="relative backdrop-blur-xl bg-slate-900/90 dark:bg-slate-800/90 text-white px-6 py-4 rounded-2xl shadow-2xl border border-purple-500/20 flex items-center gap-3">
              <div className="w-2 h-2 bg-gradient-to-r from-purple-400 to-cyan-400 rounded-full animate-pulse"></div>
              <span className="font-medium">{message}</span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};