'use client';

import { useEffect, useState } from 'react';
import { DocumentTemplate, getDocumentTemplates } from '../lib/api';

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
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set()
  );

  useEffect(() => {
    async function loadTemplates() {
      try {
        const response = await getDocumentTemplates();
        setTemplates(response.documents);
        setLoading(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load documents';
        console.error('Error loading document templates:', err);
        setError(errorMessage);
        setLoading(false);
      }
    }
    loadTemplates();
  }, []);

  // Group documents by category
  const documentsByCategory = templates.reduce(
    (acc, doc) => {
      const category = doc.category || 'Uncategorized';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(doc);
      return acc;
    },
    {} as Record<string, DocumentTemplate[]>
  );

  const toggleDocument = (docId: string) => {
    if (selectedDocuments.includes(docId)) {
      onSelectionChange(selectedDocuments.filter((id) => id !== docId));
    } else {
      onSelectionChange([...selectedDocuments, docId]);
    }
  };

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const selectAllInCategory = (category: string) => {
    const categoryDocs = documentsByCategory[category] || [];
    const categoryIds = categoryDocs.map((doc) => doc.id);
    const allSelected = categoryIds.every((id) =>
      selectedDocuments.includes(id)
    );

    if (allSelected) {
      // Deselect all in category
      onSelectionChange(
        selectedDocuments.filter((id) => !categoryIds.includes(id))
      );
    } else {
      // Select all in category
      const newSelected = [
        ...selectedDocuments.filter((id) => !categoryIds.includes(id)),
        ...categoryIds,
      ];
      onSelectionChange(newSelected);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading document templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-800">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Select Documents</h3>
        <span className="text-sm text-gray-500">
          {selectedDocuments.length} selected
        </span>
      </div>

      <div className="space-y-2">
        {Object.entries(documentsByCategory).map(([category, docs]) => {
          const isExpanded = expandedCategories.has(category);
          const categorySelected = docs.filter((doc) =>
            selectedDocuments.includes(doc.id)
          ).length;
          const allSelected = categorySelected === docs.length;

          return (
            <div
              key={category}
              className="rounded-lg border border-gray-200 bg-white"
            >
              <div className="flex items-center justify-between p-3">
                <button
                  onClick={() => toggleCategory(category)}
                  className="flex flex-1 items-center justify-between text-left"
                >
                  <span className="font-medium">{category}</span>
                  <span className="text-sm text-gray-500">
                    {categorySelected}/{docs.length} selected
                  </span>
                </button>
                <button
                  onClick={() => selectAllInCategory(category)}
                  className="ml-4 rounded px-2 py-1 text-sm text-blue-600 hover:bg-blue-50"
                >
                  {allSelected ? 'Deselect All' : 'Select All'}
                </button>
              </div>

              {isExpanded && (
                <div className="border-t border-gray-200 p-3">
                  <div className="space-y-2">
                    {docs.map((doc) => (
                      <label
                        key={doc.id}
                        className="flex items-start space-x-3 rounded p-2 hover:bg-gray-50"
                      >
                        <input
                          type="checkbox"
                          checked={selectedDocuments.includes(doc.id)}
                          onChange={() => toggleDocument(doc.id)}
                          className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <div className="flex-1">
                          <div className="font-medium">{doc.name}</div>
                          {doc.description && (
                            <div className="text-sm text-gray-500">
                              {doc.description}
                            </div>
                          )}
                          {doc.dependencies && doc.dependencies.length > 0 && (
                            <div className="mt-1 text-xs text-gray-400">
                              Requires:{' '}
                              {doc.dependencies
                                .map((depId) => {
                                  const depDoc = templates.find(
                                    (t) => t.id === depId
                                  );
                                  return depDoc?.name || depId;
                                })
                                .join(', ')}
                            </div>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

