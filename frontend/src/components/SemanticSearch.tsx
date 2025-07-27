import { useState } from 'react';
import { useCollections } from '../hooks/useApi';
import type { SearchResult } from '../types/api';

interface SemanticSearchProps {
  selectedCollection?: string;
  onSearchResults?: (results: SearchResult[], query: string) => void;
}

export function SemanticSearch({ 
  selectedCollection = 'default',
  onSearchResults 
}: SemanticSearchProps) {
  const [query, setQuery] = useState('');
  const [resultsLimit, setResultsLimit] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState<number | undefined>(undefined);
  const [lastQuery, setLastQuery] = useState('');

  const {
    searchInCollection,
    searchLoading,
    searchError,
    searchResults,
  } = useCollections();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;

    try {
      const results = await searchInCollection(
        query.trim(),
        selectedCollection,
        resultsLimit,
        similarityThreshold
      );
      
      setLastQuery(query.trim());
      
      if (onSearchResults) {
        onSearchResults(results || [], query.trim());
      }
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    setLastQuery('');
    if (onSearchResults) {
      onSearchResults([], '');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Semantic Search
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <svg className="w-4 h-4" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span>Vector Search Powered</span>
          </div>
        </div>
      </div>

      {/* Search Form */}
      <div className="p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          {/* Search Input */}
          <div>
            <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Query
            </label>
            <div className="relative">
              <input
                type="text"
                id="search-query"
                data-testid="search-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                disabled={searchLoading}
              />
              <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {query && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <svg className="h-5 w-5" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="results-limit" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Results
              </label>
              <select
                id="results-limit"
                value={resultsLimit}
                onChange={(e) => setResultsLimit(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                disabled={searchLoading}
              >
                <option value={3}>3 results</option>
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
              </select>
            </div>

            <div>
              <label htmlFor="similarity-threshold" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Similarity Threshold
                <span className="text-xs text-gray-500 ml-1">(optional)</span>
              </label>
              <input
                type="number"
                id="similarity-threshold"
                min="0"
                max="1"
                step="0.1"
                value={similarityThreshold || ''}
                onChange={(e) => setSimilarityThreshold(e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="0.7"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                disabled={searchLoading}
              />
            </div>
          </div>

          {/* Collection Info */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-blue-600 dark:text-blue-400" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Searching in: {selectedCollection}
                </p>
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  Uses vector embeddings for semantic similarity matching
                </p>
              </div>
            </div>
          </div>

          {/* Search Button */}
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Find semantically similar content
            </div>
            <button
              type="submit"
              data-testid="search-button"
              disabled={searchLoading || !query.trim()}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded-md transition-colors flex items-center space-x-2"
            >
              {searchLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" width="16" height="16" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Search</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Error Display */}
        {searchError && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <div className="flex">
              <svg className="flex-shrink-0 h-5 w-5 text-red-400" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Search Failed
                </h3>
                <div className="mt-1 text-sm text-red-700 dark:text-red-300">
                  {searchError}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Search Results Summary */}
        {lastQuery && searchResults && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-green-600 dark:text-green-400" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800 dark:text-green-200">
                  Found {searchResults.length} results for "{lastQuery}"
                </p>
                {searchResults.length > 0 && (
                  <p className="text-xs text-green-700 dark:text-green-300">
                    Best match score: {Math.max(...searchResults.map(r => r.metadata.score || 0)).toFixed(3)}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SemanticSearch;