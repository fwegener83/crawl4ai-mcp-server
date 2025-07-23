import { useState, useEffect } from 'react';
import { useCollections } from '../hooks/useApi';

interface SaveToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onSaveComplete?: (collectionName: string) => void;
}

export function SaveToCollectionModal({ 
  isOpen, 
  onClose, 
  content, 
  onSaveComplete 
}: SaveToCollectionModalProps) {
  const [collectionName, setCollectionName] = useState('default');
  const [isNewCollection, setIsNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  
  const {
    collections,
    refreshCollections,
    storeContent,
    storeLoading,
    storeError,
  } = useCollections();

  useEffect(() => {
    if (isOpen) {
      refreshCollections();
    }
  }, [isOpen, refreshCollections]);

  const handleSave = async () => {
    if (!content.trim()) return;

    const targetCollection = isNewCollection ? newCollectionName.trim() : collectionName;
    
    if (!targetCollection) {
      return;
    }

    try {
      await storeContent(content, targetCollection);
      
      if (onSaveComplete) {
        onSaveComplete(targetCollection);
      }
      
      // Reset form
      setNewCollectionName('');
      setIsNewCollection(false);
      setCollectionName('default');
      
      onClose();
    } catch (error) {
      console.error('Failed to save to collection:', error);
    }
  };

  const handleCollectionChange = (value: string) => {
    if (value === '__new__') {
      setIsNewCollection(true);
      setCollectionName('');
    } else {
      setIsNewCollection(false);
      setCollectionName(value);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Save to Collection
          </h3>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* Collection Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Collection
            </label>
            
            {!isNewCollection ? (
              <select
                value={collectionName}
                onChange={(e) => handleCollectionChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                data-testid="collection-select"
              >
                <option value="default">Default Collection</option>
                {collections.map((collection) => (
                  <option key={collection.name} value={collection.name}>
                    {collection.name} ({collection.count} items)
                  </option>
                ))}
                <option value="__new__">+ Create New Collection</option>
              </select>
            ) : (
              <div className="space-y-2">
                <input
                  type="text"
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  placeholder="Enter collection name"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  data-testid="collection-name"
                  autoFocus
                />
                <button
                  onClick={() => setIsNewCollection(false)}
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                >
                  ← Back to existing collections
                </button>
              </div>
            )}
          </div>

          {/* Content Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Content to Save
            </label>
            <div className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md p-3 max-h-32 overflow-y-auto">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {content.length > 200 ? `${content.substring(0, 200)}...` : content}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {content.length} characters
              </p>
            </div>
          </div>

          {/* Error Display */}
          {storeError && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-sm text-red-600 dark:text-red-400">
                {storeError}
              </p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={storeLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={
              storeLoading || 
              !content.trim() ||
              (isNewCollection && !newCollectionName.trim()) ||
              (!isNewCollection && !collectionName)
            }
            data-testid="save-confirm"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md transition-colors flex items-center space-x-2"
          >
            {storeLoading ? (
              <>
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Saving...</span>
              </>
            ) : (
              <span>Save to Collection</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SaveToCollectionModal;