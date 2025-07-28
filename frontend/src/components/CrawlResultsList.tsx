import { useState } from 'react';
import DocumentViewerModal from './DocumentViewerModal';
import type { CrawlResult } from '../types/api';

interface CrawlResultsListProps {
  results: CrawlResult[];
  onSelectResult?: (result: CrawlResult, index: number) => void;
  onSelectMultiple?: (results: CrawlResult[], indices: number[]) => void;
  selectedIndices?: number[];
}

export function CrawlResultsList({ 
  results, 
  onSelectResult, 
  onSelectMultiple,
  selectedIndices = [] 
}: CrawlResultsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [localSelectedIndices, setLocalSelectedIndices] = useState<number[]>(selectedIndices);
  const [showDocumentViewer, setShowDocumentViewer] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<CrawlResult | null>(null);

  const handleResultClick = (result: CrawlResult, index: number) => {
    if (onSelectResult) {
      onSelectResult(result, index);
    }
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const handleOpenDocumentViewer = (result: CrawlResult) => {
    setSelectedDocument(result);
    setShowDocumentViewer(true);
  };

  const handleCheckboxChange = (index: number, checked: boolean) => {
    const newSelected = checked 
      ? [...localSelectedIndices, index]
      : localSelectedIndices.filter(i => i !== index);
    
    setLocalSelectedIndices(newSelected);
    
    if (onSelectMultiple) {
      const selectedResults = newSelected.map(i => results[i]);
      onSelectMultiple(selectedResults, newSelected);
    }
  };

  const handleSelectAll = () => {
    const allIndices = results.map((_, index) => index);
    const isAllSelected = localSelectedIndices.length === results.length;
    const newSelected = isAllSelected ? [] : allIndices;
    
    setLocalSelectedIndices(newSelected);
    
    if (onSelectMultiple) {
      const selectedResults = newSelected.map(i => results[i]);
      onSelectMultiple(selectedResults, newSelected);
    }
  };

  const getStatusBadge = (result: CrawlResult) => {
    if (result.success) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          Success
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
          Failed
        </span>
      );
    }
  };

  const getDepthBadge = (depth: number) => {
    const colors = [
      'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    ];
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[depth % colors.length]}`}>
        Depth {depth}
      </span>
    );
  };

  if (results.length === 0) {
    return (
      <div className="text-center py-8">
        <svg className="mx-auto h-8 w-8 text-gray-400" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          No crawl results
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Start a deep crawl to see results here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Crawl Results ({results.length})
          </h3>
          <div className="flex items-center space-x-4">
            <label className="flex items-center text-sm text-gray-600 dark:text-gray-300">
              <input
                type="checkbox"
                checked={localSelectedIndices.length === results.length && results.length > 0}
                onChange={handleSelectAll}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded mr-2"
              />
              Select All
            </label>
            {localSelectedIndices.length > 0 && (
              <span className="text-sm text-green-600 dark:text-green-400">
                {localSelectedIndices.length} selected
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {results.map((result, index) => (
          <div key={index} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={localSelectedIndices.includes(index)}
                onChange={(e) => handleCheckboxChange(index, e.target.checked)}
                className="mt-1 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <button
                    onClick={() => handleResultClick(result, index)}
                    className="text-left flex-1 focus:outline-none"
                  >
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {result.title || 'Untitled Page'}
                    </h4>
                    <p className="text-sm text-blue-600 dark:text-blue-400 truncate hover:underline">
                      {result.url}
                    </p>
                  </button>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    {getStatusBadge(result)}
                    {getDepthBadge(result.depth)}
                    {result.metadata.score > 0 && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                        Score: {result.metadata.score.toFixed(1)}
                      </span>
                    )}
                    {result.success && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDocumentViewer(result);
                        }}
                        className="inline-flex items-center px-2.5 py-1 text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
                        data-testid="view-edit-button"
                      >
                        <svg className="h-3 w-3 mr-1" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                        View & Edit
                      </button>
                    )}
                  </div>
                </div>

                {/* Expandable Content */}
                {expandedIndex === index && result.success && (
                  <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                    <div className="text-sm text-gray-700 dark:text-gray-300">
                      <div className="mb-2">
                        <span className="font-medium">Content Preview:</span>
                      </div>
                      <div className="max-h-32 overflow-y-auto">
                        <p className="whitespace-pre-wrap">
                          {result.content.length > 300 
                            ? `${result.content.substring(0, 300)}...`
                            : result.content
                          }
                        </p>
                      </div>
                      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600 text-xs text-gray-500 dark:text-gray-400">
                        <div className="flex justify-between">
                          <span>Crawled: {new Date(result.metadata.crawl_time).toLocaleString()}</span>
                          <span>{result.content.length} characters</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Failed Result */}
                {expandedIndex === index && !result.success && (
                  <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-md">
                    <div className="text-sm text-red-700 dark:text-red-300">
                      <span className="font-medium">Crawl failed for this URL</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Expand/Collapse Button */}
              <button
                onClick={() => handleResultClick(result, index)}
                className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg 
                  className={`h-5 w-5 transform transition-transform ${expandedIndex === index ? 'rotate-180' : ''}`}
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="px-6 py-3 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>
              Successful: {results.filter(r => r.success).length}
            </span>
            <span>
              Failed: {results.filter(r => !r.success).length}
            </span>
            <span>
              Total Content: {results.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()} chars
            </span>
          </div>
          <div>
            Click to expand • Select for bulk actions
          </div>
        </div>
      </div>

      {/* Document Viewer Modal */}
      <DocumentViewerModal
        isOpen={showDocumentViewer}
        onClose={() => setShowDocumentViewer(false)}
        result={selectedDocument}
      />
    </div>
  );
}

export default CrawlResultsList;