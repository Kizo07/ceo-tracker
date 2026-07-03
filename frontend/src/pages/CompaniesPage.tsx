import { useQuery } from '@tanstack/react-query';
import { companiesApi } from '../services/companies';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Building2 } from 'lucide-react';

export default function CompaniesPage() {
  const { ticker } = useParams();

  if (ticker) {
    return <CompanyDetailPage ticker={ticker} />;
  }

  return <CompanyListPage />;
}

function CompanyListPage() {
  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies', { is_tracked: true }],
    queryFn: () => companiesApi.getAll({ is_tracked: true }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Companies</h1>
        <p className="text-muted-foreground">Tracked companies and their mentions</p>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">Loading companies...</div>
      ) : !companies || companies.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">No companies found</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map((company) => (
            <CompanyCard key={company.id} company={company} />
          ))}
        </div>
      )}
    </div>
  );
}

function CompanyCard({ company }: { company: any }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          {company.name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Ticker</span>
            <span className="font-medium">{company.ticker || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Sector</span>
            <span className="text-sm">{company.sector || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Industry</span>
            <span className="text-sm">{company.industry || 'N/A'}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function CompanyDetailPage({ ticker }: { ticker: string }) {
  const { data: company, isLoading } = useQuery({
    queryKey: ['company', ticker],
    queryFn: () => companiesApi.getByTicker(ticker),
  });

  // Mention data will be fetched separately
  // const { data: mentions } = useQuery({
  //   queryKey: ['mentions', { company_ticker: ticker }],
  //   queryFn: () => mentionsApi.getByCompany(ticker),
  // });

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading company...</div>;
  }

  if (!company) {
    return <div className="text-center py-8 text-destructive">Company not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{company.name}</h1>
          <p className="text-muted-foreground">{company.ticker} • {company.sector}</p>
        </div>
        <Button variant="outline" onClick={() => window.history.back()}>
          Back
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Company Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Name</span>
                <span>{company.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Ticker</span>
                <span className="font-medium">{company.ticker || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Sector</span>
                <span>{company.sector || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Industry</span>
                <span>{company.industry || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tracked</span>
                <span>{company.is_tracked ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mentions Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Mention data coming soon</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
