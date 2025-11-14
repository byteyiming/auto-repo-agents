'use client';

import { useI18n } from '@/lib/i18n';

export default function HowItWorks() {
  const { t } = useI18n();

  const steps = [
    {
      number: '1',
      icon: '✍️',
      title: t('howItWorks.step1.title'),
      description: t('howItWorks.step1.description'),
      color: 'bg-blue-100 text-blue-600',
    },
    {
      number: '2',
      icon: '📋',
      title: t('howItWorks.step2.title'),
      description: t('howItWorks.step2.description'),
      color: 'bg-purple-100 text-purple-600',
    },
    {
      number: '3',
      icon: '⚡',
      title: t('howItWorks.step3.title'),
      description: t('howItWorks.step3.description'),
      color: 'bg-green-100 text-green-600',
    },
    {
      number: '4',
      icon: '📥',
      title: t('howItWorks.step4.title'),
      description: t('howItWorks.step4.description'),
      color: 'bg-orange-100 text-orange-600',
    },
  ];

  return (
    <div className="bg-white py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl" suppressHydrationWarning>
            {t('howItWorks.title')}
          </h2>
        </div>
        
        <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className="relative rounded-lg border-2 border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md"
            >
              {/* Step Number Badge */}
              <div className={`absolute -top-4 -left-4 flex h-12 w-12 items-center justify-center rounded-full ${step.color} text-2xl font-bold shadow-lg`}>
                {step.number}
              </div>
              
              {/* Icon */}
              <div className="mb-4 flex justify-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 text-4xl">
                  {step.icon}
                </div>
              </div>
              
              {/* Content */}
              <h3 className="text-xl font-semibold text-gray-900" suppressHydrationWarning>
                {step.title}
              </h3>
              <p className="mt-2 text-gray-600" suppressHydrationWarning>
                {step.description}
              </p>
              
              {/* Connector Arrow (hidden on last item) */}
              {index < steps.length - 1 && (
                <div className="absolute -right-4 top-1/2 hidden -translate-y-1/2 lg:block">
                  <svg
                    className="h-8 w-8 text-gray-300"
                    fill="none"
                    viewBox="0 0 32 32"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M8 16h16M20 10l6 6-6 6"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

