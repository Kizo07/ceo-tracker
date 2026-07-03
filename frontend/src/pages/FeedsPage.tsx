import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedsApi } from '../services/feeds';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatRelativeTime } from '../utils/formatters';
import { Rss, RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export default function FeedsPage() {
  const queryClient = useQueryClient();
  const [activeTask, setActiveTask] = useState<string | null>(null);

  const { data: feedsStatus } = useQuery({
    queryKey: ['feeds', 'status'],
    queryFn: () => feedsApi.getStatus(),
    refetchInterval: 10000,
  });

  const { data: stats } = useQuery({
    queryKey: ['feeds', 'stats'],
    queryFn: () => feedsApi.getStats(),
  });

  const triggerMutation = useMutation({
    mutationFn: (feedKey: string) => feedsApi.trigger(feedKey),
    onSuccess: (data) => {
      setActiveTask(data.task_id);
      // Poll for task completion
      const pollInterval = setInterval(async () => {
        // In production, implement actual task status checking
        // For now, just invalidate queries after a delay
        setTimeout(() => {
          queryClient.invalidateQueries({ queryKey: ['feeds', 'status'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard'] });
          setActiveTask(null);
          clearInterval(pollInterval);
        }, 3000);
      }, 2000);
    },
  });

  const refreshMutation = useMutation({
    mutationFn: () => feedsApi.refresh(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const handleTrigger = (feedKey: string) => {
    if (triggerMutation.isPending) return;
    triggerMutation.mutate(feedKey);
  };

  const handleRefreshAll = () => {
    if (refreshMutation.isPending) return;
    refreshMutation.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">RSS Feeds</h1>
          <p className="text-muted-foreground">Manage and monitor RSS feed ingestion</p>
        </div>
        <Button onClick={handleRefreshAll} disabled={refreshMutation.isPending}>
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
          Refresh All
        </Button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Sources</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.sources_by_provider.total}</div>
              <p className="text-xs text-muted-foreground">
                RSS: {stats.sources_by_provider.rss} | Manual: {stats.sources_by_provider.manual}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Mentions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_mentions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Unprocessed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.unprocessed_sources}</div>
              <p className="text-xs text-muted-foreground">Sources awaiting processing</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Feed List */}
      <div className="space-y-3">
        {feedsStatus?.feeds.map((feed) => (
          <FeedCard
            key={feed.feed_key}
            feed={feed}
            onTrigger={() => handleTrigger(feed.feed_key)}
            isPending={triggerMutation.isPending}
          />
        ))}
      </div>

      {activeTask && (
        <Card className="border-primary">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 animate-pulse" />
              <span className="text-sm">Processing feed task...</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function FeedCard({
  feed,
  onTrigger,
  isPending,
}: {
  feed: any;
  onTrigger: () => void;
  isPending: boolean;
}) {
  const isHealthy = feed.entries_count > 0;
  const lastFetched = feed.last_fetched ? formatRelativeTime(feed.last_fetched) : 'Never';

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Rss className="h-5 w-5 text-primary" />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium">{feed.name}</span>
                <span className="text-muted-foreground">({feed.ticker})</span>
                {isHealthy ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                )}
              </div>
              <p className="text-sm text-muted-foreground">{feed.url}</p>
              <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                <span>{feed.entries_count} entries</span>
                <span>Last fetched: {lastFetched}</span>
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onTrigger}
            disabled={isPending}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isPending ? 'animate-spin' : ''}`} />
            Trigger
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
