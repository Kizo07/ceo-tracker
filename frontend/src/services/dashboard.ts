import api from './api';
import type { DashboardStats, TimelineItem } from '../types/api';

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get<DashboardStats>('/api/dashboard');
    return response.data;
  },

  getTimeline: async (limit = 20) => {
    const response = await api.get<TimelineItem[]>('/api/timeline', { params: { limit } });
    return response.data;
  },

  getSentimentCompanies: async (sentiment: string) => {
    const response = await api.get<Array<{ name: string; ticker: string; count: number }>>(`/api/dashboard/sentiment/${sentiment}`);
    return response.data;
  },
};
