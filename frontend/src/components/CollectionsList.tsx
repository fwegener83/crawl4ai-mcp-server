import { useState } from 'react';
import type { Collection } from '../types/api';

interface CollectionsListProps {
  collections: Collection[];
  selectedCollection?: string;
  onSelectCollection?: (collection: string) => void;
  onDeleteCollection?: (collection: string) => void;
  isDeleting?: boolean;
  deleteError?: string;
}

export function CollectionsList({
  collections,
  selectedCollection,
  onSelectCollection,
  onDeleteCollection,
  isDeleting = false,
  deleteError
}: CollectionsListProps) {
  const [deletingCollection, setDeletingCollection] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  const handleDeleteClick = (collectionName: string) => {
    setShowDeleteConfirm(collectionName);
  };

  const handleDeleteConfirm = async (collectionName: string) => {
    if (onDeleteCollection) {
      setDeletingCollection(collectionName);
      try {
        await onDeleteCollection(collectionName);
        setShowDeleteConfirm(null);
      } catch (error) {
        console.error('Delete failed:', error);
      } finally {
        setDeletingCollection(null);
      }
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(null);
  };

  const getCollectionIcon = (collection: Collection) => {
    if (collection.name === 'default') {
      return (
        <svg className="w-5 h-5 text-blue-500" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-purple-500" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    );
  };

  if (collections.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
          <svg className="mx-auto h-8 w-8 text-gray-400" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            No collections found
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Start crawling and saving content to create your first collection.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Collections ({collections.length})
        </h3>
      </div>

      {/* Error Display */}
      {deleteError && (
        <div className="px-6 py-3 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <p className="text-sm text-red-600 dark:text-red-400">
            {deleteError}
          </p>
        </div>
      )}

      {/* Collections List */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {collections.map((collection) => (
          <div key={collection.name} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
            <div className="flex items-center justify-between">
              <button
                onClick={() => onSelectCollection?.(selectedCollection === collection.name ? '' : collection.name)}
                className={`flex items-center space-x-3 flex-1 text-left p-2 rounded-md transition-colors ${
                  selectedCollection === collection.name
                    ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {getCollectionIcon(collection)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {collection.name}
                    </h4>
                    {collection.name === 'default' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        Default
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 mt-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {collection.count} items
                    </p>
                    {collection.metadata?.created_at && typeof collection.metadata.created_at === 'string' ? (
                      <p className="text-xs text-gray-500 dark:text-gray-500">
                        Created: {new Date(collection.metadata.created_at as string).toLocaleDateString()}
                      </p>
                    ) : null}
                  </div>
                </div>
              </button>

              {/* Actions */}
              <div className="flex items-center space-x-2 ml-4">
                {selectedCollection === collection.name && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    Selected
                  </span>
                )}
                
                {collection.name !== 'default' && (
                  <div className="relative">
                    {showDeleteConfirm === collection.name ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-600 dark:text-gray-400">Delete?</span>
                        <button
                          onClick={() => handleDeleteConfirm(collection.name)}
                          disabled={deletingCollection === collection.name}
                          className="text-red-600 hover:text-red-700 disabled:opacity-50 text-xs font-medium"
                        >
                          {deletingCollection === collection.name ? 'Deleting...' : 'Yes'}
                        </button>
                        <button
                          onClick={handleDeleteCancel}
                          disabled={deletingCollection === collection.name}
                          className="text-gray-600 hover:text-gray-700 disabled:opacity-50 text-xs font-medium"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleDeleteClick(collection.name)}
                        disabled={isDeleting || deletingCollection === collection.name}
                        className="p-1 text-gray-400 hover:text-red-600 disabled:opacity-50 transition-colors"
                        title="Delete collection"
                      >
                        <svg className="w-4 h-4" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="px-6 py-3 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>
              Total Items: {collections.reduce((sum, c) => sum + c.count, 0)}
            </span>
            <span>
              Active: {collections.length}
            </span>
          </div>
          <div>
            Click to select • Delete to remove (except default)
          </div>
        </div>
      </div>
    </div>
  );
}

export default CollectionsList;