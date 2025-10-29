import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';
import type { Message } from '../types';
import { MessageBubble } from './MessageBubble';
import { LoadingIndicator } from './LoadingIndicator';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12 sm:py-20"
          >
            <div className="relative inline-block mb-6">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-3xl blur-2xl opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-r from-purple-500 to-cyan-500 p-6 sm:p-8 rounded-3xl">
                <Bot className="w-16 h-16 sm:w-20 sm:h-20 text-white" />
              </div>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-purple-600 via-fuchsia-600 to-cyan-600 dark:from-purple-400 dark:via-fuchsia-400 dark:to-cyan-400 bg-clip-text text-transparent mb-3">
              Welcome to the Future of Support
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-base sm:text-lg px-4">
              Ask me anything about your account, billing, or technical issues
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3 px-4">
              {['Account Help', 'Billing Info', 'Technical Support'].map((item, i) => (
                <div
                  key={i}
                  className="px-4 sm:px-6 py-2 sm:py-3 backdrop-blur-sm bg-white/50 dark:bg-slate-800/50 rounded-full text-sm text-gray-700 dark:text-gray-300 border border-white/20 dark:border-purple-500/20"
                >
                  {item}
                </div>
              ))}
            </div>
          </motion.div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble key={message.id} message={message} index={index} />
          ))
        )}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
