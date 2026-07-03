import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../services/dashboard';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatRelativeTime, truncateText, getSentimentBgColor } from '../utils/formatters';

export default function TimelinePage() {
  const [limit, setLimit] = useState(20);
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const { data: items, isLoading } = useQuery({
    queryKey: ['timeline', limit],
    queryFn: () => dashboardApi.getTimeline(limit),
  });

  const toggleExpanded = (id: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Timeline</h1>
        <p className="text-muted-foreground">Chronological feed of all mentions</p>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">Loading timeline...</div>
      ) : items && items.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">No mentions found</div>
      ) : (
        <>
          <div className="space-y-3">
            {items?.map((item) => (
              <TimelineItem
                key={item.id}
                item={item}
                isExpanded={expandedIds.has(item.id)}
                onToggle={() => toggleExpanded(item.id)}
              />
            ))}
          </div>

          {items && items.length >= limit && (
            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={() => setLimit((prev) => prev + 20)}
              >
                Load More
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function TimelineItem({ item, isExpanded, onToggle }: { item: any; isExpanded: boolean; onToggle: () => void }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium">{item.ceo_name}</span>
              <span className="text-muted-foreground">mentioned</span>
              <span className="font-medium">{item.mentioned_company}</span>
              {item.ticker && (
                <>
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">{item.ticker}</span>
                </>
              )}
            </div>
            <p
              className="text-sm text-muted-foreground cursor-pointer hover:text-foreground/80 transition-colors"
              onClick={onToggle}
            >
              {isExpanded ? item.context : truncateText(item.context, 200)}
              <span className="text-primary text-xs ml-2">
                {isExpanded ? 'Show less' : 'Show more'}
              </span>
            </p>
          </div>
          <div className="flex flex-col items-end gap-2 ml-4">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentBgColor(item.sentiment)}`}>
              {item.sentiment}
            </span>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(item.created_at)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
