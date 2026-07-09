export const formatTime = (ts: number) => {
  return new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' }).format(new Date(ts));
};

export const generateId = () => Math.random().toString(36).substr(2, 9);
