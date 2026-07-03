import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ceosApi } from '../services/ceos';
import { ingestApi } from '../services/ingest';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { FileText, Loader2 } from 'lucide-react';

export default function IngestPage() {
  const [text, setText] = useState('');
  const [ceoId, setCeoId] = useState<number | null>(null);
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const queryClient = useQueryClient();

  const { data: ceos } = useQuery({
    queryKey: ['ceos'],
    queryFn: () => ceosApi.getAll(),
  });

  const mutation = useMutation({
    mutationFn: ingestApi.analyze,
    onSuccess: (data) => {
      alert(`Success! ${data.message}`);
      queryClient.invalidateQueries({ queryKey: ['mentions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setText('');
      setTitle('');
      setUrl('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || !ceoId) {
      alert('Please enter text and select a CEO');
      return;
    }
    mutation.mutate({
      text,
      ceo_id: ceoId,
      source_type: 'manual',
      title: title || undefined,
      url: url || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Manual Ingestion</h1>
        <p className="text-muted-foreground">Analyze text for company mentions and sentiment</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Input Text
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">CEO</label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  value={ceoId || ''}
                  onChange={(e) => setCeoId(Number(e.target.value) || null)}
                  required
                >
                  <option value="">Select a CEO</option>
                  {ceos?.map((ceo) => (
                    <option key={ceo.id} value={ceo.id}>
                      {ceo.name} - {ceo.company_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Title (Optional)</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border rounded-md"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Source title..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">URL (Optional)</label>
                <input
                  type="url"
                  className="w-full px-3 py-2 border rounded-md"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Text to Analyze</label>
                <textarea
                  className="w-full px-3 py-2 border rounded-md min-h-[200px]"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste CEO speech, interview, or press release here..."
                  required
                />
              </div>

              <Button type="submit" disabled={mutation.isPending} className="w-full">
                {mutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  'Analyze Text'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>
            {mutation.isPending ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : mutation.data ? (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-green-800 font-medium">{mutation.data.message}</p>
                  <p className="text-sm text-green-600 mt-1">
                    {mutation.data.mentions_created} mentions created
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => window.location.href = '/mentions'}
                  className="w-full"
                >
                  View Mentions
                </Button>
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">
                Submit text to see analysis results
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
