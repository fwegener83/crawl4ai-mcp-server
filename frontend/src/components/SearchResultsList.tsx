import { useState } from 'react';
import type { SearchResult } from '../types/api';

interface SearchResultsListProps {
  results: SearchResult[];
  query: string;
  onSelectResult?: (result: SearchResult, index: number) => void;
}

export function SearchResultsList({ 
  results, 
  query,
  onSelectResult 
}: SearchResultsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleResultClick = (result: SearchResult, index: number) => {
    if (onSelectResult) {
      onSelectResult(result, index);
    }
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const getScoreBadge = (score: number | undefined) => {
    if (score === undefined || score === null) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
          No Score
        </span>
      );
    }
    
    if (score >= 0.8) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          Excellent ({score.toFixed(3)})
        </span>
      );
    } else if (score >= 0.6) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
          Good ({score.toFixed(3)})
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
          Fair ({score.toFixed(3)})
        </span>
      );
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-900 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  if (results.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
          <svg className="mx-auto h-8 w-8 text-gray-400" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            {query ? 'No results found' : 'No search performed'}
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {query 
              ? `No content found matching "${query}". Try a different search term.`
              : 'Enter a search query above to find relevant content.'
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Search Results ({results.length})
          </h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Query: "{query}"
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {results.map((result, index) => (
          <div key={index} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
            <div className="flex items-start justify-between">
              <button
                onClick={() => handleResultClick(result, index)}
                className="text-left flex-1 focus:outline-none"
              >
                <div className="flex items-center space-x-3 mb-2">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {result.metadata.source_url && (
                        <p className="text-sm text-blue-600 dark:text-blue-400 truncate hover:underline">
                          {result.metadata.source_url}
                        </p>
                      )}
                      {getScoreBadge(result.metadata.score)}
                    </div>
                    
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">Chunk {result.metadata.chunk_index + 1}</span>
                      {' '} • Distance: {result.distance ? result.distance.toFixed(4) : 'N/A'}
                    </div>
                  </div>
                </div>

                {/* Content Preview */}
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  <div className="line-clamp-3">
                    {highlightText(
                      result.content.length > 200 
                        ? `${result.content.substring(0, 200)}...`
                        : result.content,
                      query
                    )}
                  </div>
                </div>
              </button>

              {/* Expand Button */}
              <button
                onClick={() => handleResultClick(result, index)}
                className="ml-4 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 flex-shrink-0"
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

            {/* Expanded Content */}
            {expandedIndex === index && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
                <div className="space-y-3">
                  {/* Metadata */}
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-600 pb-2">
                    <div className="flex items-center space-x-4">
                      <span>Chunk: {result.metadata.chunk_index + 1}</span>
                      <span>Score: {result.metadata.score ? result.metadata.score.toFixed(4) : 'N/A'}</span>
                      <span>Distance: {result.distance ? result.distance.toFixed(4) : 'N/A'}</span>
                    </div>
                    {result.metadata.source_url && (
                      <a 
                        href={result.metadata.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        View Source
                      </a>
                    )}
                  </div>

                  {/* Full Content */}
                  <div className="text-sm text-gray-700 dark:text-gray-300 max-h-64 overflow-y-auto">
                    <div className="whitespace-pre-wrap">
                      {highlightText(result.content, query)}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="px-6 py-3 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>
              Avg Score: {(results.reduce((sum, r) => sum + (r.metadata.score || 0), 0) / results.length).toFixed(3)}
            </span>
            <span>
              Total Characters: {results.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()}
            </span>
          </div>
          <div>
            Click to expand • Highlighted matches
          </div>
        </div>
      </div>
    </div>
  );
}

export default SearchResultsList;