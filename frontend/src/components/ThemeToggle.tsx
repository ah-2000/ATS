'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="btn btn-secondary w-full flex items-center justify-center gap-2.5"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
            <span className="text-xs font-semibold">
                {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
            </span>
        </button>
    );
}
