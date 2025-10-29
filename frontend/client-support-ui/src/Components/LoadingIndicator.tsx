import React from 'react';
import { motion } from 'framer-motion';

export const LoadingIndicator: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex justify-start"
    >
      <div className="relative sm:mr-12">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-3xl rounded-bl-md blur-md opacity-30"></div>
        <div className="relative backdrop-blur-xl bg-white/90 dark:bg-slate-800/90 rounded-3xl rounded-bl-md px-6 sm:px-8 py-4 sm:py-5 shadow-xl border border-white/20 dark:border-purple-500/20">
          <div className="flex gap-2">
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 0 }}
              className="w-2 h-2 sm:w-2.5 sm:h-2.5 bg-gradient-to-r from-purple-500 to-fuchsia-500 rounded-full"
            />
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 0, delay: 0.2 }}
              className="w-2 h-2 sm:w-2.5 sm:h-2.5 bg-gradient-to-r from-fuchsia-500 to-cyan-500 rounded-full"
            />
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, repeatDelay: 0, delay: 0.4 }}
              className="w-2 h-2 sm:w-2.5 sm:h-2.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};