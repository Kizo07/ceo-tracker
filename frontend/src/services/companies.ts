import api from './api';
import type { Company } from '../types/api';

export const companiesApi = {
  getAll: async (params?: { is_tracked?: boolean }) => {
    const response = await api.get<Company[]>('/api/companies', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Company>(`/api/companies/${id}`);
    return response.data;
  },

  getByTicker: async (ticker: string) => {
    const response = await api.get<Company>(`/api/companies/ticker/${ticker}`);
    return response.data;
  },
};
