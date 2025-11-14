'use client';

import { useEffect, useState } from 'react';
import { DocumentTemplate, getDocumentTemplates } from '../lib/api';
import { useI18n, getDocumentName, getLevelName } from '../lib/i18n';
import { rankDocuments, filterDocumentsByView, organizeByLevel, DocumentLevel, LEVEL_ICONS, type ViewMode } from '../lib/documentRanking';

interface DocumentSelectorProps {
  selectedDocuments: string[];
  onSelectionChange: (selected: string[]) => void;
}

export default function DocumentSelector({
  selectedDocuments,
  onSelectionChange,
}: DocumentSelectorProps) {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [expandedLevels, setExpandedLevels] = useState<Set<DocumentLevel>>(new Set());
  const { t, language } = useI18n();

  useEffect(() => {
    async function loadTemplates() {
      try {
        const response = await getDocumentTemplates();
        setTemplates(response.documents);
        setLoading(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : t('error.loadDocuments');
        console.error('Error loading document templates:', err);
        setError(errorMessage);
        setLoading(false);
      }
    }
    loadTemplates();
  }, []);

  // Filter and rank documents
  const filteredDocs = filterDocumentsByView(templates, viewMode);
  const rankedDocs = rankDocuments(filteredDocs);
  const organizedDocs = organizeByLevel(rankedDocs);

  const toggleDocument = (docId: string) => {
    if (selectedDocuments.includes(docId)) {
      onSelectionChange(selectedDocuments.filter((id) => id !== docId));
    } else {
      onSelectionChange([...selectedDocuments, docId]);
    }
  };

  const toggleLevel = (level: DocumentLevel) => {
    const newExpanded = new Set(expandedLevels);
    if (newExpanded.has(level)) {
      newExpanded.delete(level);
    } else {
      newExpanded.add(level);
    }
    setExpandedLevels(newExpanded);
  };

  const renderDocumentList = (docs: DocumentTemplate[], level: DocumentLevel) => {
    if (docs.length === 0) return null;

    return (
      <div key={level} className="space-y-2">
        {docs.map((doc) => (
          <label
            key={doc.id}
            className="flex items-start space-x-3 rounded-lg border border-gray-200 bg-white p-3 hover:bg-gray-50 transition-colors"
          >
            <input
              type="checkbox"
              checked={selectedDocuments.includes(doc.id)}
              onChange={() => toggleDocument(doc.id)}
              className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">{getDocumentName(doc.id) || doc.name}</span>
                {doc.priority && (
                  <span className={`rounded px-2 py-0.5 text-xs font-medium ${
                    doc.priority.includes('高') || doc.priority.includes('High')
                      ? 'bg-red-100 text-red-800'
                      : doc.priority.includes('中') || doc.priority.includes('Medium')
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {doc.priority}
                  </span>
                )}
              </div>
              {doc.description && (
                <div className="mt-1 text-sm text-gray-600">
                  {doc.description}
                </div>
              )}
              {doc.dependencies && doc.dependencies.length > 0 && (
                <div className="mt-1 text-xs text-gray-500">
                  {t('documents.dependencies')}:{' '}
                  {doc.dependencies
                    .map((depId) => {
                      const depDoc = templates.find((t) => t.id === depId);
                      return getDocumentName(depId) || depDoc?.name || depId;
                    })
                    .join(', ')}
                </div>
              )}
            </div>
          </label>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">{t('documents.select')}...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-800">
        {t('error.loadDocuments')}: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4 min-h-0">
      {/* View Mode Selector */}
      <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3">
        <span className="text-sm font-medium text-gray-700">{t('documents.title')}:</span>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('all')}
            className={`rounded px-3 py-1 text-sm transition-colors ${
              viewMode === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('documents.all')}
          </button>
          <button
            onClick={() => setViewMode('team')}
            className={`rounded px-3 py-1 text-sm transition-colors ${
              viewMode === 'team'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('documents.team')}
          </button>
          <button
            onClick={() => setViewMode('solo')}
            className={`rounded px-3 py-1 text-sm transition-colors ${
              viewMode === 'solo'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('documents.solo')}
          </button>
        </div>
      </div>

      {/* Document Count Summary */}
      <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3">
        <h3 className="text-lg font-semibold">{t('documents.select')}</h3>
        <span className="text-sm text-gray-500">
          {selectedDocuments.length} {t('documents.selected')} ({rankedDocs.length} {t('documents.all')})
        </span>
      </div>

      {/* Documents organized by Strategic Levels */}
      <div className="space-y-6">
        {/* Level 1: Strategic */}
        {organizedDocs.strategic.length > 0 && (
          <div className="rounded-lg border-2 border-purple-200 bg-purple-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.STRATEGIC)}
              className="w-full border-b border-purple-200 bg-purple-100 p-4 text-left transition-colors hover:bg-purple-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-purple-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.STRATEGIC]}</span>
                <span>{getLevelName(DocumentLevel.STRATEGIC)}</span>
                <span className="ml-auto text-sm font-normal text-purple-700">
                  ({organizedDocs.strategic.length} documents)
                </span>
                <span className="text-purple-600">
                  {expandedLevels.has(DocumentLevel.STRATEGIC) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.STRATEGIC) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.strategic, DocumentLevel.STRATEGIC)}
              </div>
            )}
          </div>
        )}

        {/* Level 2: Product Manager */}
        {organizedDocs.product.length > 0 && (
          <div className="rounded-lg border-2 border-blue-200 bg-blue-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.PRODUCT)}
              className="w-full border-b border-blue-200 bg-blue-100 p-4 text-left transition-colors hover:bg-blue-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-blue-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.PRODUCT]}</span>
                <span>{getLevelName(DocumentLevel.PRODUCT)}</span>
                <span className="ml-auto text-sm font-normal text-blue-700">
                  ({organizedDocs.product.length} documents)
                </span>
                <span className="text-blue-600">
                  {expandedLevels.has(DocumentLevel.PRODUCT) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.PRODUCT) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.product, DocumentLevel.PRODUCT)}
              </div>
            )}
          </div>
        )}

        {/* Level 3: Developer/Technical */}
        {organizedDocs.developer.length > 0 && (
          <div className="rounded-lg border-2 border-green-200 bg-green-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.DEVELOPER)}
              className="w-full border-b border-green-200 bg-green-100 p-4 text-left transition-colors hover:bg-green-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-green-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.DEVELOPER]}</span>
                <span>{getLevelName(DocumentLevel.DEVELOPER)}</span>
                <span className="ml-auto text-sm font-normal text-green-700">
                  ({organizedDocs.developer.length} documents)
                </span>
                <span className="text-green-600">
                  {expandedLevels.has(DocumentLevel.DEVELOPER) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.DEVELOPER) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.developer, DocumentLevel.DEVELOPER)}
              </div>
            )}
          </div>
        )}

        {/* Level 4: User/End-user */}
        {organizedDocs.user.length > 0 && (
          <div className="rounded-lg border-2 border-yellow-200 bg-yellow-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.USER)}
              className="w-full border-b border-yellow-200 bg-yellow-100 p-4 text-left transition-colors hover:bg-yellow-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-yellow-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.USER]}</span>
                <span>{getLevelName(DocumentLevel.USER)}</span>
                <span className="ml-auto text-sm font-normal text-yellow-700">
                  ({organizedDocs.user.length} documents)
                </span>
                <span className="text-yellow-600">
                  {expandedLevels.has(DocumentLevel.USER) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.USER) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.user, DocumentLevel.USER)}
              </div>
            )}
          </div>
        )}

        {/* Level 5: Operations/Maintenance */}
        {organizedDocs.operations.length > 0 && (
          <div className="rounded-lg border-2 border-orange-200 bg-orange-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.OPERATIONS)}
              className="w-full border-b border-orange-200 bg-orange-100 p-4 text-left transition-colors hover:bg-orange-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-orange-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.OPERATIONS]}</span>
                <span>{getLevelName(DocumentLevel.OPERATIONS)}</span>
                <span className="ml-auto text-sm font-normal text-orange-700">
                  ({organizedDocs.operations.length} documents)
                </span>
                <span className="text-orange-600">
                  {expandedLevels.has(DocumentLevel.OPERATIONS) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.OPERATIONS) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.operations, DocumentLevel.OPERATIONS)}
              </div>
            )}
          </div>
        )}

        {/* Cross-Level (Everyone) */}
        {organizedDocs.crossLevel.length > 0 && (
          <div className="rounded-lg border-2 border-gray-200 bg-gray-50">
            <button
              onClick={() => toggleLevel(DocumentLevel.CROSS_LEVEL)}
              className="w-full border-b border-gray-200 bg-gray-100 p-4 text-left transition-colors hover:bg-gray-200"
            >
              <h4 className="flex items-center gap-2 font-semibold text-gray-900">
                <span className="text-xl">{LEVEL_ICONS[DocumentLevel.CROSS_LEVEL]}</span>
                <span>{getLevelName(DocumentLevel.CROSS_LEVEL)}</span>
                <span className="ml-auto text-sm font-normal text-gray-700">
                  ({organizedDocs.crossLevel.length} documents)
                </span>
                <span className="text-gray-600">
                  {expandedLevels.has(DocumentLevel.CROSS_LEVEL) ? '▼' : '▶'}
                </span>
              </h4>
            </button>
            {expandedLevels.has(DocumentLevel.CROSS_LEVEL) && (
              <div className="p-4">
                {renderDocumentList(organizedDocs.crossLevel, DocumentLevel.CROSS_LEVEL)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
