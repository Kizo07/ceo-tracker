import api from './api';
import type { CEO } from '../types/api';

export const ceosApi = {
  getAll: async () => {
    const response = await api.get<CEO[]>('/api/ceos');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<CEO>(`/api/ceos/${id}`);
    return response.data;
  },
};
