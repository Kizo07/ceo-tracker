import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../utils/cn';
import {
  BarChart3,
  MessageSquare,
  Clock,
  Rss,
  Building2,
  Users,
  FileText,
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { href: '/mentions', label: 'Mentions', icon: MessageSquare },
  { href: '/timeline', label: 'Timeline', icon: Clock },
  { href: '/feeds', label: 'RSS Feeds', icon: Rss },
  { href: '/companies', label: 'Companies', icon: Building2 },
  { href: '/ceos', label: 'CEOs', icon: Users },
  { href: '/ingest', label: 'Manual Ingest', icon: FileText },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r bg-card">
      <nav className="space-y-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href ||
            (item.href !== '/dashboard' && location.pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
