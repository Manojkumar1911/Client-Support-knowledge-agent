
import React from 'react';
import { motion } from 'framer-motion';
import type { Message } from '../types';
import { getIntentGradient } from '../utils/helpers';

interface MessageBubbleProps {
  message: Message;
  index: number;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-2xl w-full sm:w-auto relative ${
          message.role === 'user' ? 'sm:ml-12' : 'sm:mr-12'
        }`}
      >
        {message.role === 'user' ? (
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500 rounded-3xl rounded-br-md blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
            <div className="relative bg-gradient-to-r from-purple-500 via-fuchsia-500 to-cyan-500 text-white rounded-3xl rounded-br-md px-4 sm:px-6 py-3 sm:py-4 shadow-xl">
              <p className="whitespace-pre-wrap text-sm sm:text-base">{message.content}</p>
            </div>
          </div>
        ) : (
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-slate-200 to-slate-300 dark:from-slate-800 dark:to-slate-900 rounded-3xl rounded-bl-md blur-md opacity-50"></div>
            <div className="relative backdrop-blur-xl bg-white/90 dark:bg-slate-800/90 text-gray-900 dark:text-white rounded-3xl rounded-bl-md px-4 sm:px-6 py-3 sm:py-4 shadow-xl border border-white/20 dark:border-purple-500/20">
              {message.intent && (
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <div className="relative px-3 py-1 rounded-full overflow-hidden">
                    <div className={`absolute inset-0 bg-gradient-to-r ${getIntentGradient(message.intent)}`}></div>
                    <span className="relative text-white text-xs font-semibold uppercase tracking-wider">
                      {message.intent.replace('_', ' ')}
                    </span>
                  </div>
                  {message.confidence && (
                    <div className="flex items-center gap-1">
                      <div className="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-500"
                          style={{ width: `${message.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                        {(message.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              )}
              <p className="whitespace-pre-wrap leading-relaxed text-sm sm:text-base">{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <details className="mt-4 text-sm">
                  <summary className="cursor-pointer text-purple-600 dark:text-purple-400 font-medium hover:text-purple-700 dark:hover:text-purple-300 transition-colors">
                    📚 Sources ({message.sources.length})
                  </summary>
                  <ul className="mt-3 space-y-2">
                    {message.sources.map((source, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-600 dark:text-gray-400 pl-2">
                        <span className="text-purple-500">•</span>
                        <span className="break-words">{source}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};