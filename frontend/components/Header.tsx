'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useI18n, languages, languageNames, type Language } from '@/lib/i18n';
import { Sparkles, Github, ChevronDown } from 'lucide-react';

export default function Header() {
  const { language, setLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    setIsOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 glass-nav">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        {/* Logo & Title */}
        <div className="flex-shrink-0">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30 transition-transform group-hover:scale-105">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-white tracking-tight">OmniDoc</span>
              <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-semibold">AI Documentation Suite</span>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex items-center space-x-4">
          <a
            href="https://github.com/yimgao"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 rounded-full px-4 py-2 text-sm font-medium text-gray-400 transition-all hover:bg-white/10 hover:text-white"
          >
            <Github className="h-4 w-4" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
          {/* Language Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="flex items-center space-x-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-gray-300 transition-all hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              <span>{languageNames[language]}</span>
              <ChevronDown className={`h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
            {isOpen && (
              <div className="absolute right-0 mt-2 w-40 glass-panel rounded-xl overflow-hidden shadow-xl animate-in fade-in zoom-in-95 duration-100">
                <div className="py-1">
                  {languages.map((lang) => (
                    <button
                      key={lang}
                      onClick={() => handleLanguageChange(lang)}
                      className={`w-full px-4 py-2.5 text-left text-sm transition-colors ${
                        language === lang
                          ? 'bg-indigo-500/20 text-indigo-300'
                          : 'text-gray-400 hover:bg-white/5 hover:text-white'
                      }`}
                    >
                      {languageNames[lang]}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
