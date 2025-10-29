import type { ApiResponse } from '../types';

export const sendQueryToAPI = async (
  apiUrl: string,
  userId: string,
  query: string
): Promise<ApiResponse> => {
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        user_id: userId, 
        query 
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API request failed: ${response.status}`);
    }

    const data = await response.json();
    return {
      ...data,
      // Ensure all required fields are present with defaults
      intent: data.intent || 'general_query',
      confidence: data.confidence || 0,
      response: data.response || 'Sorry, I could not process your request.',
      sources: data.sources || [],
      action_invoked: data.action_invoked || null,
      timestamp: data.timestamp || new Date().toISOString(),
    };
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export const exportChatAsText = (messages: any[]) => {
  const chatText = messages
    .map(m => `${m.role.toUpperCase()}: ${m.content}\n${m.timestamp ? new Date(m.timestamp).toLocaleString() : ''}`)
    .join('\n\n---\n\n');
  
  const blob = new Blob([chatText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `chat_${new Date().toISOString().split('T')[0]}.txt`;
  a.click();
  URL.revokeObjectURL(url);
};
