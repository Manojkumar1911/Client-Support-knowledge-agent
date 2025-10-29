import { useState, useEffect } from 'react';
import type { Message, ChatHistory } from '../types';

export const useChat = () => {
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>(() => {
    const stored = localStorage.getItem('chatHistories');
    return stored ? JSON.parse(stored, (key, value) => {
      if (key === 'timestamp' || key === 'lastUpdated') {
        return new Date(value);
      }
      return value;
    }) : [];
  });

  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    localStorage.setItem('chatHistories', JSON.stringify(chatHistories));
  }, [chatHistories]);

  const startNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
  };

  const loadChat = (chatId: string) => {
    const chat = chatHistories.find(c => c.id === chatId);
    if (chat) {
      setMessages(chat.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })));
      setCurrentChatId(chatId);
    }
  };

  const deleteChat = (chatId: string) => {
    setChatHistories(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId) {
      startNewChat();
    }
  };

  const clearHistory = () => {
    setChatHistories([]);
    setMessages([]);
    setCurrentChatId(null);
  };

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const updateChatHistory = (userMessage: Message, assistantMessage: Message) => {
    const newMessages = [...messages, userMessage, assistantMessage];
    
    if (currentChatId) {
      setChatHistories(prev =>
        prev.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: newMessages, lastUpdated: new Date() }
            : chat
        )
      );
    } else {
      const newChat: ChatHistory = {
        id: Date.now().toString(),
        title: userMessage.content.slice(0, 50),
        messages: newMessages,
        lastUpdated: new Date(),
      };
      setChatHistories(prev => [newChat, ...prev]);
      setCurrentChatId(newChat.id);
    }
  };

  return {
    chatHistories,
    currentChatId,
    messages,
    setMessages,
    startNewChat,
    loadChat,
    deleteChat,
    clearHistory,
    addMessage,
    updateChatHistory,
  };
};
