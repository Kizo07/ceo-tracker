import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import MentionsPage from './pages/MentionsPage';
import TimelinePage from './pages/TimelinePage';
import FeedsPage from './pages/FeedsPage';
import CompaniesPage from './pages/CompaniesPage';
import CEOsPage from './pages/CEOsPage';
import IngestPage from './pages/IngestPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      retry: 2,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="mentions" element={<MentionsPage />} />
              <Route path="timeline" element={<TimelinePage />} />
              <Route path="feeds" element={<FeedsPage />} />
              <Route path="companies" element={<CompaniesPage />} />
              <Route path="companies/:ticker" element={<CompaniesPage />} />
              <Route path="ceos" element={<CEOsPage />} />
              <Route path="ceos/:id" element={<CEOsPage />} />
              <Route path="ingest" element={<IngestPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
export { queryClient };
