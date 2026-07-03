import { format, formatDistanceToNow, parseISO } from 'date-fns';

export const formatDate = (dateString: string): string => {
  const date = parseISO(dateString);
  return format(date, 'MMM d, yyyy');
};

export const formatDateTime = (dateString: string): string => {
  const date = parseISO(dateString);
  return format(date, 'MMM d, yyyy h:mm a');
};

export const formatRelativeTime = (dateString: string): string => {
  const date = parseISO(dateString);
  return formatDistanceToNow(date, { addSuffix: true });
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

export const getSentimentColor = (sentiment: string): string => {
  const colors = {
    positive: 'text-green-600',
    negative: 'text-red-600',
    neutral: 'text-gray-600',
    unknown: 'text-purple-600',
  };
  return colors[sentiment as keyof typeof colors] || colors.unknown;
};

export const getSentimentBgColor = (sentiment: string): string => {
  const colors = {
    positive: 'bg-green-100 text-green-800',
    negative: 'bg-red-100 text-red-800',
    neutral: 'bg-gray-100 text-gray-800',
    unknown: 'bg-purple-100 text-purple-800',
  };
  return colors[sentiment as keyof typeof colors] || colors.unknown;
};
