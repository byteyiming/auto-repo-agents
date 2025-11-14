'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DocumentSelector from '@/components/DocumentSelector';
import HeroSection from '@/components/HeroSection';
import HowItWorks from '@/components/HowItWorks';
import { createProject } from '@/lib/api';
import { useI18n } from '@/lib/i18n';

export default function Home() {
  const router = useRouter();
  const { t } = useI18n();
  const [userIdea, setUserIdea] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Start with empty selection - users must explicitly select documents
  // Don't load from localStorage - always start fresh

  // Save selections to localStorage (for potential future use, but don't auto-load)
  useEffect(() => {
    if (typeof window !== 'undefined' && selectedDocuments.length > 0) {
      localStorage.setItem(
        'omniDoc_selectedDocuments',
        JSON.stringify(selectedDocuments)
      );
    } else if (typeof window !== 'undefined' && selectedDocuments.length === 0) {
      // Clear localStorage when no documents are selected
      localStorage.removeItem('omniDoc_selectedDocuments');
    }
  }, [selectedDocuments]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!userIdea.trim()) {
      setError(t('project.idea.placeholder'));
      return;
    }

    if (selectedDocuments.length === 0) {
      setError(t('documents.select'));
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await createProject({
        user_idea: userIdea.trim(),
        selected_documents: selectedDocuments,
      });

      // Navigate to project status page
      router.push(`/project/${response.project_id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t('error.createProject');
      console.error('Error creating project:', err);
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <HeroSection />

      {/* Main Form Section - Two Column Layout */}
      <div className="mx-auto max-w-7xl px-4 py-12">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 lg:items-stretch">
            {/* Left Column: Project Idea Input */}
            <div className="flex flex-col">
              <div className="flex-1 rounded-lg bg-white p-6 shadow-sm relative flex flex-col">
                {/* Label with Help Icon */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="group relative">
                    <svg
                      className="h-5 w-5 text-gray-400 hover:text-blue-500 cursor-help transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                    {/* Tooltip */}
                    <div className="absolute left-0 top-8 z-50 hidden group-hover:block w-80 rounded-lg bg-gray-900 p-4 text-sm text-white shadow-xl">
                      <div className="font-semibold mb-2" suppressHydrationWarning>{t('project.idea.tips.title')}</div>
                      <ul className="space-y-1.5 text-gray-300">
                        <li suppressHydrationWarning>• {t('project.idea.tips.1')}</li>
                        <li suppressHydrationWarning>• {t('project.idea.tips.2')}</li>
                        <li suppressHydrationWarning>• {t('project.idea.tips.3')}</li>
                        <li suppressHydrationWarning>• {t('project.idea.tips.4')}</li>
                      </ul>
                    </div>
                  </div>
                  <label
                    htmlFor="userIdea"
                    className="text-sm font-medium text-gray-700"
                    suppressHydrationWarning
                  >
                    {t('project.idea')}
                  </label>
                </div>
                
                {/* Textarea - Takes up available space */}
                <textarea
                  id="userIdea"
                  value={userIdea}
                  onChange={(e) => setUserIdea(e.target.value)}
                  placeholder={t('project.idea.placeholder')}
                  className="flex-1 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[400px]"
                  required
                  suppressHydrationWarning
                />
                
                {/* Error Message */}
                {error && (
                  <div className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800" suppressHydrationWarning>
                    {error}
                  </div>
                )}
                
                {/* Generate Button - Centered at Bottom */}
                <div className="mt-4 flex justify-center">
                  <button
                    type="submit"
                    disabled={isSubmitting || selectedDocuments.length === 0}
                    className="rounded-lg bg-blue-600 px-8 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-blue-600"
                    suppressHydrationWarning
                  >
                    {isSubmitting ? t('button.creating') : t('button.generate')}
                  </button>
                </div>
              </div>
            </div>

            {/* Right Column: Document Selector */}
            <div className="flex flex-col">
              <div className="flex-1 rounded-lg bg-white shadow-sm flex flex-col overflow-hidden min-h-0">
                <div className="flex-1 overflow-y-auto p-6 min-h-0">
                  <DocumentSelector
                    selectedDocuments={selectedDocuments}
                    onSelectionChange={setSelectedDocuments}
                  />
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      {/* How It Works Section */}
      <HowItWorks />
    </div>
  );
}
