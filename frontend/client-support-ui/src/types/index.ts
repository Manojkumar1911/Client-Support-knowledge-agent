export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  confidence?: number;
  sources?: string[];
  timestamp: Date;
}

export interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
  lastUpdated: Date;
}

export interface ApiResponse {
  intent: string;
  confidence: number;
  response: string;
  sources: string[];
  action_invoked: string;
  timestamp: string;
}