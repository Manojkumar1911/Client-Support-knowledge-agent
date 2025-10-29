export const getIntentGradient = (intent?: string): string => {
  const gradients: Record<string, string> = {
    general_query: 'from-blue-500 via-cyan-500 to-teal-500',
    reset_password: 'from-emerald-500 via-green-500 to-lime-500',
    ticket_status: 'from-orange-500 via-amber-500 to-yellow-500',
    billing: 'from-purple-500 via-fuchsia-500 to-pink-500',
    technical_support: 'from-red-500 via-rose-500 to-pink-500',
  };
  return gradients[intent || ''] || 'from-gray-500 to-gray-600';
};

export const generateUserId = (): string => {
  return `user_${Math.random().toString(36).substr(2, 9)}`;
};