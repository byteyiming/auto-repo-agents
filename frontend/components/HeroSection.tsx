'use client';

import { useI18n } from '@/lib/i18n';

export default function HeroSection() {
  const { t } = useI18n();

  return (
    <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl md:text-7xl" suppressHydrationWarning>
            {t('hero.title')}
          </h1>
          <p className="mt-6 text-xl leading-8 text-gray-600 sm:text-2xl" suppressHydrationWarning>
            {t('hero.subtitle')}
          </p>
          <p className="mt-4 text-lg text-gray-500" suppressHydrationWarning>
            {t('hero.description')}
          </p>
          
          {/* Visual Flow Diagram */}
          <div className="mt-12 flex items-center justify-center">
            <div className="flex items-center space-x-4 sm:space-x-8">
              {/* Idea */}
              <div className="flex flex-col items-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-100 text-4xl shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl sm:h-24 sm:w-24 animate-pulse" style={{ animationDuration: '2s' }}>
                  💡
                </div>
                <span className="mt-3 text-sm font-medium text-gray-700 sm:text-base" suppressHydrationWarning>
                  {t('hero.flow.idea')}
                </span>
              </div>
              
              {/* Arrow */}
              <div className="hidden items-center sm:flex">
                <svg
                  className="h-8 w-16 text-blue-400 animate-pulse"
                  fill="none"
                  viewBox="0 0 64 32"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ animationDuration: '1.5s' }}
                >
                  <path
                    d="M0 16h60M50 6l10 10-10 10"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="flex items-center sm:hidden">
                <svg
                  className="h-6 w-12 text-blue-400 animate-pulse"
                  fill="none"
                  viewBox="0 0 48 24"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ animationDuration: '1.5s' }}
                >
                  <path
                    d="M0 12h44M36 4l8 8-8 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              
              {/* Customized Agents */}
              <div className="flex flex-col items-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-purple-100 text-4xl shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl sm:h-24 sm:w-24 animate-pulse" style={{ animationDuration: '2s', animationDelay: '0.3s' }}>
                  🤖
                </div>
                <span className="mt-3 text-sm font-medium text-gray-700 sm:text-base" suppressHydrationWarning>
                  {t('hero.flow.agents')}
                </span>
              </div>
              
              {/* Arrow */}
              <div className="hidden items-center sm:flex">
                <svg
                  className="h-8 w-16 text-purple-400 animate-pulse"
                  fill="none"
                  viewBox="0 0 64 32"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ animationDuration: '1.5s', animationDelay: '0.3s' }}
                >
                  <path
                    d="M0 16h60M50 6l10 10-10 10"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="flex items-center sm:hidden">
                <svg
                  className="h-6 w-12 text-purple-400 animate-pulse"
                  fill="none"
                  viewBox="0 0 48 24"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ animationDuration: '1.5s', animationDelay: '0.3s' }}
                >
                  <path
                    d="M0 12h44M36 4l8 8-8 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              
              {/* Documents */}
              <div className="flex flex-col items-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-green-100 text-4xl shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl sm:h-24 sm:w-24 animate-pulse" style={{ animationDuration: '2s', animationDelay: '0.6s' }}>
                  📚
                </div>
                <span className="mt-3 text-sm font-medium text-gray-700 sm:text-base" suppressHydrationWarning>
                  {t('hero.flow.documents')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

