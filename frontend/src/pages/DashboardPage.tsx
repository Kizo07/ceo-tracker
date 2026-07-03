import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../services/dashboard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/Dialog';
import { MessageSquare, Building2, Users, TrendingUp } from 'lucide-react';
import { formatNumber, getSentimentBgColor } from '../utils/formatters';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getStats(),
  });
  const navigate = useNavigate();
  const [sentimentModal, setSentimentModal] = useState<{ sentiment: string; companies: Array<{ name: string; ticker: string; count: number }> } | null>(null);

  const handleSentimentClick = async (sentiment: string) => {
    const companies = await dashboardApi.getSentimentCompanies(sentiment);
    setSentimentModal({ sentiment, companies });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-destructive">Error loading dashboard</div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of CEO tracking data</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Mentions"
          value={formatNumber(stats.total_mentions)}
          icon={MessageSquare}
          description={`${stats.recent_mentions} recent`}
        />
        <StatCard
          title="Tracked CEOs"
          value={formatNumber(stats.total_ceos)}
          icon={Users}
          description="Active profiles"
        />
        <StatCard
          title="Companies"
          value={formatNumber(stats.total_companies)}
          icon={Building2}
          description="Tracked entities"
        />
        <StatCard
          title="Recent Activity"
          value={formatNumber(stats.recent_mentions)}
          icon={TrendingUp}
          description="New mentions"
        />
      </div>

      {/* Sentiment Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SentimentItem
              label="Positive"
              count={stats.sentiment_breakdown.positive}
              sentiment="positive"
              onClick={() => handleSentimentClick('positive')}
            />
            <SentimentItem
              label="Negative"
              count={stats.sentiment_breakdown.negative}
              sentiment="negative"
              onClick={() => handleSentimentClick('negative')}
            />
            <SentimentItem
              label="Neutral"
              count={stats.sentiment_breakdown.neutral}
              sentiment="neutral"
              onClick={() => handleSentimentClick('neutral')}
            />
            <SentimentItem
              label="Unknown"
              count={stats.sentiment_breakdown.unknown}
              sentiment="unknown"
              onClick={() => handleSentimentClick('unknown')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Most Mentioned Companies */}
      <Card>
        <CardHeader>
          <CardTitle>Most Mentioned Companies</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {stats.most_mentioned_companies.slice(0, 5).map((company) => (
              <div
                key={company.ticker}
                className="flex items-center justify-between cursor-pointer hover:bg-muted p-2 rounded transition-colors"
                onClick={() => navigate(`/mentions?company_ticker=${company.ticker}`)}
              >
                <div>
                  <span className="font-medium">{company.name}</span>
                  <span className="text-muted-foreground ml-2">({company.ticker})</span>
                </div>
                <span className="text-muted-foreground">{formatNumber(company.count)} mentions</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Most Active CEOs */}
      <Card>
        <CardHeader>
          <CardTitle>Most Active CEOs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {stats.most_active_ceos.slice(0, 5).map((ceo) => (
              <div key={ceo.name} className="flex items-center justify-between">
                <div>
                  <span className="font-medium">{ceo.name}</span>
                  <span className="text-muted-foreground ml-2">({ceo.company})</span>
                </div>
                <span className="text-muted-foreground">{formatNumber(ceo.speeches)} speeches</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Sentiment Modal */}
      <Dialog open={!!sentimentModal} onOpenChange={() => setSentimentModal(null)}>
        <DialogContent>
          {sentimentModal && (
            <>
              <DialogHeader>
                <DialogTitle className="capitalize">
                  {sentimentModal.sentiment} Sentiment Companies
                </DialogTitle>
                <DialogDescription>
                  Companies mentioned with {sentimentModal.sentiment} sentiment
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {sentimentModal.companies.length === 0 ? (
                  <p className="text-center text-muted-foreground py-4">No companies found</p>
                ) : (
                  sentimentModal.companies.map((company) => (
                    <div
                      key={company.ticker}
                      className="flex items-center justify-between p-2 hover:bg-muted rounded cursor-pointer"
                      onClick={() => {
                        setSentimentModal(null);
                        navigate(`/mentions?company_ticker=${company.ticker}&sentiment=${sentimentModal.sentiment}`);
                      }}
                    >
                      <div>
                        <span className="font-medium">{company.name}</span>
                        <span className="text-muted-foreground ml-2">({company.ticker})</span>
                      </div>
                      <span className="text-muted-foreground">{formatNumber(company.count)} mentions</span>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  description,
}: {
  title: string;
  value: string;
  icon: React.ElementType;
  description: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function SentimentItem({
  label,
  count,
  sentiment,
  onClick,
}: {
  label: string;
  count: number;
  sentiment: 'positive' | 'negative' | 'neutral' | 'unknown';
  onClick: () => void;
}) {
  return (
    <div className="text-center cursor-pointer hover:opacity-80 transition-opacity" onClick={onClick}>
      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSentimentBgColor(sentiment)}`}>
        {formatNumber(count)}
      </span>
      <p className="text-sm text-muted-foreground mt-2">{label}</p>
    </div>
  );
}
