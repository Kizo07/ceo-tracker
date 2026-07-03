import api from './api';
import type { Mention, MentionListResponse, SentimentSummary } from '../types/api';

export interface MentionQueryParams {
  page?: number;
  page_size?: number;
  ceo_id?: number;
  company_ticker?: string;
  sentiment?: string;
}

export const mentionsApi = {
  getAll: async (params: MentionQueryParams = {}) => {
    const response = await api.get<MentionListResponse>('/api/mentions', { params });
    return response.data;
  },

  getByCEO: async (ceoId: number) => {
    const response = await api.get<Mention[]>(`/api/mentions/ceo/${ceoId}`);
    return response.data;
  },

  getByCompany: async (ticker: string) => {
    const response = await api.get<Mention[]>(`/api/mentions/company/${ticker}`);
    return response.data;
  },

  getSentimentSummary: async (ceoId: number) => {
    const response = await api.get<SentimentSummary>(`/api/sentiment/summary/${ceoId}`);
    return response.data;
  },
};
