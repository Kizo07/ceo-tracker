import api from './api';
import type { FeedListResponse, FeedStatusListResponse, FeedStatsResponse, TaskResponse } from '../types/api';

export const feedsApi = {
  getConfig: async () => {
    const response = await api.get<FeedListResponse>('/api/feeds/config');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get<FeedStatusListResponse>('/api/feeds/status');
    return response.data;
  },

  trigger: async (feedKey: string) => {
    const response = await api.post<TaskResponse>('/api/feeds/trigger', { feed_key: feedKey });
    return response.data;
  },

  refresh: async () => {
    const response = await api.post<TaskResponse>('/api/feeds/refresh');
    return response.data;
  },

  test: async (feedKey: string) => {
    const response = await api.get(`/api/feeds/test`, { params: { feed_key: feedKey } });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get<FeedStatsResponse>('/api/feeds/stats');
    return response.data;
  },
};
