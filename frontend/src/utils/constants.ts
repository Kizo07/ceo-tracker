// App Constants

export const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

export const APP_NAME = 'CEO Tracker';

export const SENTIMENT_OPTIONS = [
  { value: 'all', label: 'All Sentiments' },
  { value: 'positive', label: 'Positive' },
  { value: 'negative', label: 'Negative' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'unknown', label: 'Unknown' },
] as const;

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;

export const POLLING_INTERVALS = {
  TASK_STATUS: 2000, // 2 seconds
  FEED_STATUS: 10000, // 10 seconds
} as const;
