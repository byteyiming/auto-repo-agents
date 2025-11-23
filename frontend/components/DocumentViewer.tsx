'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { GeneratedDocument, getDocumentDownloadUrl } from '../lib/api';

interface DocumentViewerProps {
  documents: GeneratedDocument[];
  projectId: string;
}

export default function DocumentViewer({
  documents,
  projectId,
}: DocumentViewerProps) {
  const [selectedDocId, setSelectedDocId] = useState<string | null>(
    documents.length > 0 ? documents[0].id : null
  );
  const [copySuccess, setCopySuccess] = useState(false);
  const contentScrollRef = useRef<HTMLDivElement>(null);
  const copyTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const selectedDoc = documents.find((doc) => doc.id === selectedDocId);

  // Reset scroll position when document changes
  useEffect(() => {
    if (contentScrollRef.current) {
      contentScrollRef.current.scrollTop = 0;
    }
  }, [selectedDocId]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (copyTimeoutRef.current) {
        clearTimeout(copyTimeoutRef.current);
      }
    };
  }, []);

  const handleDownload = (docId: string) => {
    const url = getDocumentDownloadUrl(projectId, docId);
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = ''; // Let the server set the filename via Content-Disposition
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyToClipboard = async (text: string) => {
    try {
      // Check if clipboard API is available
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            showCopySuccess();
          } else {
            console.error('Failed to copy text');
            alert('Failed to copy to clipboard. Please copy manually.');
          }
        } catch (err) {
          console.error('Fallback copy failed:', err);
          alert('Failed to copy to clipboard. Please copy manually.');
        } finally {
          document.body.removeChild(textArea);
        }
        return;
      }

      // Use modern clipboard API
      await navigator.clipboard.writeText(text);
      showCopySuccess();
    } catch (err) {
      console.error('Failed to copy text:', err);
      alert('Failed to copy to clipboard. Please copy manually.');
    }
  };

  const showCopySuccess = () => {
    setCopySuccess(true);
    if (copyTimeoutRef.current) {
      clearTimeout(copyTimeoutRef.current);
    }
    copyTimeoutRef.current = setTimeout(() => {
      setCopySuccess(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col h-full w-full md:flex-row" style={{ height: '100%', overflow: 'hidden' }}>
      {/* Document List Sidebar - Scrollable */}
      {/* Mobile: Full width with max height, Desktop: Fixed width sidebar */}
      <aside
        aria-label="Document list"
        className="w-full md:w-64 flex-shrink-0 border-b md:border-b-0 md:border-r border-gray-200 bg-gray-50 flex flex-col h-auto max-h-[40vh] md:h-full md:max-h-none overflow-hidden"
      >
        <div className="p-3 md:p-4 flex-shrink-0 border-b border-gray-200">
          <h2 className="text-base md:text-lg font-semibold text-gray-900">Documents</h2>
          <div className="mt-1 md:mt-2 text-xs md:text-sm text-gray-500" aria-live="polite">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div 
          className="flex-1"
          style={{ 
            overflowY: 'auto',
            overflowX: 'hidden',
            minHeight: 0,
            height: 0 // Force flex child to respect parent height
          }}
        >
          <nav aria-label="Document navigation" className="space-y-1 p-2">
            {documents.map((doc, index) => (
              <button
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                aria-label={`View ${doc.name} document, ${doc.status}`}
                aria-current={selectedDocId === doc.id ? 'page' : undefined}
                className={`w-full rounded-lg p-2 md:p-3 text-left transition-colors focus:outline-none focus:ring-2 focus:ring-[#007BFF] focus:ring-offset-1 ${
                  selectedDocId === doc.id
                    ? 'bg-blue-50 text-gray-900'
                    : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex-1 truncate text-sm md:text-base font-medium text-gray-900">{doc.name}</div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs flex-shrink-0 ${
                      doc.status === 'complete'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                    aria-label={`Status: ${doc.status}`}
                  >
                    {doc.status}
                  </span>
                </div>
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Document Content */}
      <div 
        className="flex-1 flex-shrink-0 flex flex-col bg-white"
        style={{ height: '100%', overflow: 'hidden' }}
      >
        {selectedDoc ? (
          <>
            {/* Header - Sticky */}
            <div className="flex-shrink-0 border-b border-gray-200 bg-white p-3 md:p-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h2 className="text-lg md:text-xl font-semibold text-gray-900 truncate">{selectedDoc.name}</h2>
                </div>
                <div className="flex flex-wrap gap-2 items-center" role="group" aria-label="Document actions">
                  {selectedDoc.content && (
                    <button
                      onClick={() => copyToClipboard(selectedDoc.content!)}
                      aria-label={copySuccess ? 'Content copied to clipboard' : 'Copy document content to clipboard'}
                      aria-live="polite"
                      className={`rounded-lg border px-3 md:px-4 py-1.5 md:py-2 text-xs md:text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#007BFF] focus:ring-offset-1 ${
                        copySuccess
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {copySuccess ? '✓ Copied!' : 'Copy'}
                    </button>
                  )}
                  {selectedDoc.file_path && (
                    <button
                      onClick={() => handleDownload(selectedDoc.id)}
                      aria-label={`Download ${selectedDoc.name} document`}
                      className="rounded-lg bg-blue-600 px-3 md:px-4 py-1.5 md:py-2 text-xs md:text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-[#007BFF] focus:ring-offset-1"
                    >
                      Download
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Content - Scrollable */}
            <article
              ref={contentScrollRef}
              className="flex-1"
              aria-label={`Content of ${selectedDoc.name}`}
              style={{ 
                overflowY: 'auto',
                overflowX: 'hidden',
                minHeight: 0,
                height: 0 // Force flex child to respect parent height
              }}
            >
              <div className="p-4 md:p-6">
                {selectedDoc.content ? (
                  <div className="prose prose-sm md:prose-base max-w-none text-gray-900">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {selectedDoc.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="flex items-center justify-center p-8 md:p-12 text-gray-500" role="status" aria-live="polite">
                    <div className="text-center">
                      <div className="text-base md:text-lg font-medium">No content available</div>
                      <div className="mt-2 text-xs md:text-sm">
                        {selectedDoc.status === 'pending'
                          ? 'Document is still being generated...'
                          : 'Document content is not available'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </article>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">
            <div className="text-center">
              <div className="text-lg font-medium">No document selected</div>
              <div className="mt-2 text-sm">
                Select a document from the list to view its content
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
