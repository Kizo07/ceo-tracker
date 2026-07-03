import { Link } from 'react-router-dom';
import { BarChart3, Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export default function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b bg-background">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/dashboard" className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">CEO Tracker</span>
        </Link>
        <div className="flex items-center gap-4">
          <div className="text-sm text-muted-foreground">
            Tracking CEO Speeches & Sentiment
          </div>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-md hover:bg-muted transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
