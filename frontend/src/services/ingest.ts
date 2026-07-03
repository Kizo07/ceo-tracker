import api from './api';
import type { IngestRequest, IngestResponse } from '../types/api';

export const ingestApi = {
  analyze: async (data: IngestRequest) => {
    const response = await api.post<IngestResponse>('/api/ingest', data);
    return response.data;
  },

  test: async () => {
    const response = await api.post<IngestResponse>('/api/ingest/test');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/api/ingest/status');
    return response.data;
  },
};
