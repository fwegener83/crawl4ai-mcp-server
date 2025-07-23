import { useState, useEffect } from 'react';
import { useCollections } from '../hooks/useApi';
import CollectionsList from '../components/CollectionsList';
import SemanticSearch from '../components/SemanticSearch';
import SearchResultsList from '../components/SearchResultsList';
import type { SearchResult } from '../types/api';

export function CollectionsPage() {
  const [selectedCollection, setSelectedCollection] = useState<string>('default');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [lastQuery, setLastQuery] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);

  const {
    collections,
    refreshCollections,
    deleteCollection,
    listLoading,
    listError,
    deleteLoading,
    deleteError,
  } = useCollections();

  // Load collections on mount
  useEffect(() => {
    refreshCollections();
  }, [refreshCollections]);

  // Update selected collection if current one is deleted
  useEffect(() => {
    if (selectedCollection !== 'default' && collections.length > 0) {
      const exists = collections.some(c => c.name === selectedCollection);
      if (!exists) {
        setSelectedCollection('default');
      }
    }
  }, [collections, selectedCollection]);

  const handleCollectionSelect = (collectionName: string) => {
    setSelectedCollection(collectionName);
    // Clear search results when switching collections
    setSearchResults([]);
    setLastQuery('');
  };

  const handleDeleteCollection = async (collectionName: string) => {
    try {
      await deleteCollection(collectionName);
      setDeleteSuccess(`Successfully deleted collection: ${collectionName}`);
      setTimeout(() => setDeleteSuccess(null), 5000);
      
      // Clear search results if we deleted the selected collection
      if (selectedCollection === collectionName) {
        setSearchResults([]);
        setLastQuery('');
      }
    } catch (error) {
      console.error('Delete collection failed:', error);
    }
  };

  const handleSearchResults = (results: SearchResult[], query: string) => {
    setSearchResults(results);
    setLastQuery(query);
  };

  const handleSearchResultSelect = (result: SearchResult, index: number) => {
    // Could implement additional actions here, like viewing in detail
    console.log('Selected search result:', result, index);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Collection Management
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Manage your saved content collections and search with RAG-powered semantic search.
        </p>
      </div>

      {/* Success Message */}
      {deleteSuccess && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md" data-testid="delete-success-message">
          <div className="flex">
            <svg className="flex-shrink-0 h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800 dark:text-green-200">
                {deleteSuccess}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {listLoading && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <div className="flex items-center justify-center">
            <svg className="animate-spin h-8 w-8 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="ml-3 text-gray-600 dark:text-gray-300">Loading collections...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {listError && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex">
            <svg className="flex-shrink-0 h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Failed to load collections
              </h3>
              <div className="mt-1 text-sm text-red-700 dark:text-red-300">
                {listError}
              </div>
              <div className="mt-2">
                <button
                  onClick={refreshCollections}
                  className="text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-500 dark:hover:text-red-300"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!listLoading && !listError && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Collections Management */}
          <div className="space-y-6">
            <CollectionsList
              collections={collections}
              selectedCollection={selectedCollection}
              onSelectCollection={handleCollectionSelect}
              onDeleteCollection={handleDeleteCollection}
              isDeleting={deleteLoading}
              deleteError={deleteError}
            />

            {/* Collection Statistics */}
            {collections.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Statistics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {collections.length}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Collections</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {collections.reduce((sum, c) => sum + c.count, 0)}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Total Items</div>
                  </div>
                </div>
                
                {/* Selected Collection Info */}
                {selectedCollection && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">Selected:</span> {selectedCollection}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium">Items:</span>{' '}
                      {collections.find(c => c.name === selectedCollection)?.count || 0}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Search Interface */}
          <div className="space-y-6">
            <SemanticSearch
              selectedCollection={selectedCollection}
              onSearchResults={handleSearchResults}
            />

            {/* Search Results */}
            <SearchResultsList
              results={searchResults}
              query={lastQuery}
              onSelectResult={handleSearchResultSelect}
            />
          </div>
        </div>
      )}

      {/* Empty State */}
      {!listLoading && !listError && collections.length === 0 && (
        <div className="text-center py-12">
          <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
            No collections found
          </h3>
          <p className="mt-2 text-gray-600 dark:text-gray-300 max-w-md mx-auto">
            Start by crawling some websites and saving the content to collections. 
            Then you can search and manage your saved content here.
          </p>
          <div className="mt-6 flex justify-center space-x-4">
            <button
              onClick={() => window.location.hash = 'simple-crawl'}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-md transition-colors"
            >
              Start Simple Crawl
            </button>
            <button
              onClick={() => window.location.hash = 'deep-crawl'}
              className="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-md transition-colors"
            >
              Start Deep Crawl
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CollectionsPage;