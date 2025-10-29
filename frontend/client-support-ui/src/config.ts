export const config = {
  // Default API URL - can be overridden in settings
  defaultApiUrl: 'http://localhost:8000/api/ask',
  
  // Default user ID format
  defaultUserId: 'user_' + Math.random().toString(36).substring(2, 15),
  
  // API endpoints
  endpoints: {
    ask: '/api/ask',
  }
};