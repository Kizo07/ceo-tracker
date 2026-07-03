// API Response Types

export interface Company {
  id: number;
  ticker: string | null;
  name: string;
  is_tracked: boolean;
  sector: string | null;
  industry: string | null;
  created_at: string;
  updated_at: string;
}

export interface CEO {
  id: number;
  name: string;
  company_id: number;
  company_name?: string;
  company_ticker?: string;
  title: string | null;
  twitter_handle: string | null;
  created_at: string;
  updated_at: string;
}

export interface Mention {
  id: number;
  ceo_id: number;
  ceo_name: string;
  ceo_company: string;
  mentioned_company: string;
  mentioned_ticker: string | null;
  context: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'unknown';
  confidence: number;
  relationship_type: string | null;
  created_at: string;
}

export interface MentionListResponse {
  mentions: Mention[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardStats {
  total_mentions: number;
  total_ceos: number;
  total_companies: number;
  sentiment_breakdown: {
    positive: number;
    negative: number;
    neutral: number;
    unknown: number;
  };
  recent_mentions: number;
  most_mentioned_companies: Array<{
    name: string;
    ticker: string;
    count: number;
  }>;
  most_active_ceos: Array<{
    name: string;
    company: string;
    speeches: number;
  }>;
}

export interface SentimentSummary {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
  unknown: number;
}

export interface Feed {
  feed_key: string;
  name: string;
  ticker: string;
  url: string;
  provider: string;
}

export interface FeedStatus extends Feed {
  entries_count?: number;
  last_fetched?: string;
}

export interface FeedListResponse {
  feeds: Feed[];
  total_feeds: number;
}

export interface FeedStatusListResponse {
  feeds: FeedStatus[];
  total_feeds: number;
}

export interface IngestRequest {
  text: string;
  ceo_id: number;
  source_type?: string;
  title?: string;
  url?: string;
}

export interface IngestResponse {
  success: boolean;
  message: string;
  mentions_created: number;
  speech_id: number;
}

export interface TaskResponse {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY';
  result?: any;
}

export interface FeedStatsResponse {
  sources_by_provider: {
    rss: number;
    finnhub: number;
    manual: number;
    total: number;
  };
  total_mentions: number;
  unprocessed_sources: number;
}

export interface TimelineItem {
  id: number;
  ceo_name: string;
  mentioned_company: string;
  ticker: string | null;
  context: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'unknown';
  created_at: string;
}
