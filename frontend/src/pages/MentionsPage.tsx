import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mentionsApi, MentionQueryParams } from '../services/mentions';
import { ceosApi } from '../services/ceos';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatRelativeTime, truncateText, getSentimentBgColor } from '../utils/formatters';
import { SENTIMENT_OPTIONS, PAGE_SIZE_OPTIONS } from '../utils/constants';

export default function MentionsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [filters, setFilters] = useState<MentionQueryParams>({});
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const { data: mentionsData, isLoading } = useQuery({
    queryKey: ['mentions', page, pageSize, filters],
    queryFn: () => mentionsApi.getAll({ page, page_size: pageSize, ...filters }),
  });

  const { data: ceos } = useQuery({
    queryKey: ['ceos'],
    queryFn: () => ceosApi.getAll(),
  });

  const totalPages = mentionsData ? Math.ceil(mentionsData.total / pageSize) : 1;

  const handleFilterChange = (key: keyof MentionQueryParams, value: string | number | undefined) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value === '' || value === 'all' ? undefined : value,
    }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Mentions</h1>
        <p className="text-muted-foreground">Browse and filter all company mentions</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">CEO</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={filters.ceo_id || ''}
                onChange={(e) => handleFilterChange('ceo_id', e.target.value ? Number(e.target.value) : undefined)}
              >
                <option value="">All CEOs</option>
                {ceos?.map((ceo) => (
                  <option key={ceo.id} value={ceo.id}>
                    {ceo.name} ({ceo.company_name})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Company Ticker</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                placeholder="e.g. AAPL"
                value={filters.company_ticker || ''}
                onChange={(e) => handleFilterChange('company_ticker', e.target.value || undefined)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Sentiment</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={filters.sentiment || 'all'}
                onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              >
                {SENTIMENT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Page Size</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
              >
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <option key={size} value={size}>
                    {size} per page
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div>
        {mentionsData && (
          <p className="text-sm text-muted-foreground mb-4">
            Showing {mentionsData.mentions.length} of {mentionsData.total} mentions
          </p>
        )}

        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading mentions...</div>
        ) : mentionsData?.mentions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">No mentions found</div>
        ) : (
          <div className="space-y-3">
            {mentionsData?.mentions.map((mention) => (
              <MentionCard
                key={mention.id}
                mention={mention}
                isExpanded={expandedIds.has(mention.id)}
                onToggle={() => {
                  const newExpanded = new Set(expandedIds);
                  if (newExpanded.has(mention.id)) {
                    newExpanded.delete(mention.id);
                  } else {
                    newExpanded.add(mention.id);
                  }
                  setExpandedIds(newExpanded);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {mentionsData && mentionsData.total > pageSize && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function MentionCard({ mention, isExpanded, onToggle }: { mention: any; isExpanded: boolean; onToggle: () => void }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium">{mention.ceo_name}</span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground">{mention.ceo_company}</span>
              <span className="text-muted-foreground">mentioned</span>
              <span className="font-medium">{mention.mentioned_company}</span>
              {mention.mentioned_ticker && (
                <>
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">{mention.mentioned_ticker}</span>
                </>
              )}
            </div>
            <p
              className="text-sm text-muted-foreground cursor-pointer hover:text-foreground/80 transition-colors"
              onClick={onToggle}
            >
              {isExpanded ? mention.context : truncateText(mention.context, 200)}
              <span className="text-primary text-xs ml-2">
                {isExpanded ? 'Show less' : 'Show more'}
              </span>
            </p>
          </div>
          <div className="flex flex-col items-end gap-2 ml-4">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentBgColor(mention.sentiment)}`}>
              {mention.sentiment}
            </span>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(mention.created_at)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
