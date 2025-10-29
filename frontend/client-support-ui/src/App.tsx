
import { useState, useEffect } from 'react';
import { Background } from './Components/Background';
import { Sidebar } from './Components/Sidebar';
import { Topbar } from './Components/Topbar';
import { ChatArea } from './Components/ChatArea';
import { ChatInput } from './Components/ChatInput';
import { SettingsModal } from './Components/SettingsModal';
import { Toast } from './Components/Toast';
import { useChat } from './hooks/useChat';
import { sendQueryToAPI, exportChatAsText } from './lib/api';
import { generateUserId } from './utils/helpers';
import type { Message } from './types';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const stored = localStorage.getItem('theme');
    return (stored as 'light' | 'dark') || 'dark';
  });
  
  const [userId, setUserId] = useState(() => {
    const stored = localStorage.getItem('userId');
    return stored || generateUserId();
  });
  
  const [apiUrl, setApiUrl] = useState(() => {
    const stored = localStorage.getItem('apiUrl');
    return stored || 'http://localhost:8000/api/ask';
  });
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showToast, setShowToast] = useState<string | null>(null);

  const {
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
  } = useChat();

  // Apply theme
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Save userId
  useEffect(() => {
    localStorage.setItem('userId', userId);
  }, [userId]);

  // Save apiUrl
  useEffect(() => {
    localStorage.setItem('apiUrl', apiUrl);
  }, [apiUrl]);

  // Toast auto-hide
  useEffect(() => {
    if (showToast) {
      const timer = setTimeout(() => setShowToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [showToast]);

  // Handle responsive sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInputValue('');
    setIsLoading(true);

    try {
      const data = await sendQueryToAPI(apiUrl, userId, inputValue);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        confidence: data.confidence,
        sources: data.sources,
        timestamp: new Date(),
      };

      addMessage(assistantMessage);
      updateChatHistory(userMessage, assistantMessage);
    } catch (error) {
      setShowToast('Failed to get response. Please check your connection.');
      console.error('Error:', error);
      
      // Remove the user message if API fails
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportChat = () => {
    if (messages.length === 0) {
      setShowToast('No messages to export');
      return;
    }
    exportChatAsText(messages);
    setShowToast('Chat exported successfully');
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all chat history?')) {
      clearHistory();
      setShowToast('Chat history cleared');
    }
  };

  const handleDeleteChat = (chatId: string) => {
    if (window.confirm('Are you sure you want to delete this chat?')) {
      deleteChat(chatId);
      setShowToast('Chat deleted');
    }
  };

  const handleNewChat = () => {
    startNewChat();
    setShowToast('New conversation started');
  };

  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <div className="h-screen flex overflow-hidden">
        <Background />

        <Sidebar
          isOpen={sidebarOpen}
          chatHistories={chatHistories}
          currentChatId={currentChatId}
          onNewChat={handleNewChat}
          onLoadChat={loadChat}
          onDeleteChat={handleDeleteChat}
          onExportChat={handleExportChat}
          onClearHistory={handleClearHistory}
          messagesCount={messages.length}
        />

        <div className="flex-1 flex flex-col relative z-10">
          <Topbar
            theme={theme}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            onToggleTheme={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            onOpenSettings={() => setSettingsOpen(true)}
          />

          <ChatArea messages={messages} isLoading={isLoading} />

          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSend={sendMessage}
            isLoading={isLoading}
          />
        </div>

        <SettingsModal
          isOpen={settingsOpen}
          userId={userId}
          apiUrl={apiUrl}
          onClose={() => setSettingsOpen(false)}
          onUserIdChange={setUserId}
          onApiUrlChange={setApiUrl}
        />

        <Toast message={showToast} />

        <style>{`
          .custom-scrollbar::-webkit-scrollbar {
            width: 8px;
            height: 8px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: linear-gradient(to bottom, rgba(168, 85, 247, 0.4), rgba(6, 182, 212, 0.4));
            border-radius: 10px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(to bottom, rgba(168, 85, 247, 0.6), rgba(6, 182, 212, 0.6));
          }
        `}</style>
      </div>
    </div>
  );
}

export default App;