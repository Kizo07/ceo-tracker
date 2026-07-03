import axios from 'axios';

const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Error in request configuration
      console.error('Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
