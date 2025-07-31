import React, { useEffect, useState } from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import LoadingSpinner from '../LoadingSpinner';
import Icon from '../ui/Icon';

interface CollectionSidebarProps {
  className?: string;
}

export function CollectionSidebar({ className = '' }: CollectionSidebarProps) {
  const {
    state,
    loadCollections,
    selectCollection,
    openModal,
    openDeleteConfirmation,
    clearError,
  } = useCollectionOperations();

  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    loadCollections();
  }, [loadCollections, refreshKey]);

  // Auto-refresh collections every 30 seconds to keep data fresh
  useEffect(() => {
    const interval = setInterval(() => {
      if (!state.ui.loading.collections) {
        loadCollections();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [loadCollections, state.ui.loading.collections]);

  const handleSelectCollection = (collectionId: string) => {
    if (state.selectedCollection !== collectionId) {
      selectCollection(collectionId);
    }
  };

  const handleDeleteCollection = (collectionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    openDeleteConfirmation('collection', collectionId);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (state.ui.loading.collections) {
    return (
      <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="p-4">
          <div className="flex items-center justify-center">
            <LoadingSpinner size="sm" />
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading collections...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Collections</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              disabled={state.ui.loading.collections}
              className="inline-flex items-center p-1.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded transition-colors disabled:opacity-50"
              title="Refresh collections"
            >
              <Icon 
                name="refresh" 
                size="sm" 
                color="current"
                animate={state.ui.loading.collections ? 'spin' : undefined}
              />
            </button>
            <button
              onClick={() => openModal('newCollection')}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <Icon name="plus" size="sm" color="current" className="mr-1" />
              New
            </button>
          </div>
        </div>
        
        {/* Collection Stats */}
        {state.collections.length > 0 && (
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {state.collections.length} collection{state.collections.length !== 1 ? 's' : ''} • 
            {' '}{state.collections.reduce((sum, c) => sum + c.file_count, 0)} total files
          </div>
        )}
      </div>

      {/* Error Display */}
      {state.ui.error && (
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-md p-3">
            <div className="flex">
              <div className="flex-shrink-0">
                <Icon name="xCircle" size="md" color="red" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700 dark:text-red-200">{state.ui.error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={clearError}
                  className="inline-flex text-red-400 hover:text-red-600 dark:hover:text-red-300"
                >
                  <span className="sr-only">Dismiss</span>
                  <Icon name="x" size="md" color="current" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Collections List */}
      <div className="flex-1 overflow-y-auto">
        {state.collections.length === 0 ? (
          <div className="p-4 text-center">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <Icon name="folder" size="xl" color="gray" className="mx-auto" />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">No collections yet</p>
            <button
              onClick={() => openModal('newCollection')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Create your first collection
            </button>
          </div>
        ) : (
          <div className="p-2">
            {state.collections.map((collection) => (
              <div
                key={collection.name}
                onClick={() => handleSelectCollection(collection.name)}
                className={`group relative p-3 rounded-md cursor-pointer transition-colors ${
                  state.selectedCollection === collection.name
                    ? 'bg-blue-50 dark:bg-blue-900/50 border border-blue-200 dark:border-blue-800'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center">
                      <Icon name="folder" size="sm" color="gray" className="mr-3" />
                      <h3 className={`text-sm font-medium truncate ${
                        state.selectedCollection === collection.name
                          ? 'text-blue-700 dark:text-blue-300'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {collection.name}
                      </h3>
                    </div>
                    {collection.description && (
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 truncate">
                        {collection.description}
                      </p>
                    )}
                    <div className="mt-2 space-y-1">
                      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                        <Icon name="document" size="xs" color="gray" className="mr-1.5" />
                        <span>{collection.file_count} files</span>
                        {collection.folders.length > 0 && (
                          <>
                            <span className="mx-1">•</span>
                            <Icon name="folder" size="xs" color="gray" className="mr-1.5" />
                            <span>{collection.folders.length} folders</span>
                          </>
                        )}
                      </div>
                      
                      {/* Additional metadata */}
                      <div className="flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
                        <span title="Created">
                          <Icon name="info" size="xs" color="gray" className="mr-1" />
                          {formatDate(collection.created_at)}
                        </span>
                        
                        {collection.metadata.total_size > 0 && (
                          <span title="Total size">
                            <Icon name="folder" size="xs" color="gray" className="mr-1" />
                            {formatFileSize(collection.metadata.total_size)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Delete button */}
                  <button
                    onClick={(e) => handleDeleteCollection(collection.name, e)}
                    className="opacity-0 group-hover:opacity-100 ml-2 p-1 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-all"
                    title="Delete collection"
                  >
                    <Icon name="trash" size="sm" color="current" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CollectionSidebar;