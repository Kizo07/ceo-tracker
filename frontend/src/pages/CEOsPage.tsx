import { useQuery } from '@tanstack/react-query';
import { ceosApi } from '../services/ceos';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { User } from 'lucide-react';

export default function CEOsPage() {
  const { id } = useParams();

  if (id) {
    return <CEODetailPage id={Number(id)} />;
  }

  return <CEOListPage />;
}

function CEOListPage() {
  const { data: ceos, isLoading } = useQuery({
    queryKey: ['ceos'],
    queryFn: () => ceosApi.getAll(),
  });
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">CEOs</h1>
        <p className="text-muted-foreground">Tracked executives and their activity</p>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">Loading CEOs...</div>
      ) : ceos && ceos.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">No CEOs found</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ceos?.map((ceo) => (
            <CEOCard key={ceo.id} ceo={ceo} onClick={() => navigate(`/mentions?ceo_id=${ceo.id}`)} />
          ))}
        </div>
      )}
    </div>
  );
}

function CEOCard({ ceo, onClick }: { ceo: any; onClick: () => void }) {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={onClick}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-primary" />
          {ceo.name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Title</span>
            <span className="text-sm">{ceo.title || 'CEO'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Company</span>
            <span className="font-medium">{ceo.company_name || 'N/A'}</span>
          </div>
          {ceo.company_ticker && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ticker</span>
              <span className="text-sm">{ceo.company_ticker}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function CEODetailPage({ id }: { id: number }) {
  const { data: ceo, isLoading } = useQuery({
    queryKey: ['ceo', id],
    queryFn: () => ceosApi.getById(id),
  });

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading CEO...</div>;
  }

  if (!ceo) {
    return <div className="text-center py-8 text-destructive">CEO not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{ceo.name}</h1>
          <p className="text-muted-foreground">{ceo.title} at {ceo.company_name}</p>
        </div>
        <Button variant="outline" onClick={() => window.history.back()}>
          Back
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>CEO Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Name</span>
                <span>{ceo.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Title</span>
                <span>{ceo.title || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Company</span>
                <span className="font-medium">{ceo.company_name || 'N/A'}</span>
              </div>
              {ceo.company_ticker && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ticker</span>
                  <span>{ceo.company_ticker}</span>
                </div>
              )}
              {ceo.twitter_handle && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Twitter</span>
                  <a
                    href={`https://twitter.com/${ceo.twitter_handle.replace('@', '')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    {ceo.twitter_handle}
                  </a>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Activity Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Activity data coming soon</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
