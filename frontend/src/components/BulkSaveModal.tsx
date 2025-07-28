import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useCollections } from '../hooks/useApi';
import type { CrawlResult } from '../types/api';

interface BulkSaveModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: CrawlResult[];
  selectedIndices: number[];
  onSaveComplete?: (collectionName: string, savedCount: number) => void;
}

export function BulkSaveModal({ 
  isOpen, 
  onClose, 
  results,
  selectedIndices,
  onSaveComplete 
}: BulkSaveModalProps) {
  const [collectionName, setCollectionName] = useState('default');
  const [isNewCollection, setIsNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [saveProgress, setSaveProgress] = useState<{
    current: number;
    total: number;
    status: string;
  }>({ current: 0, total: 0, status: 'idle' });
  
  const {
    collections,
    refreshCollections,
    storeContent,
    storeError,
  } = useCollections();

  useEffect(() => {
    if (isOpen) {
      refreshCollections();
      setSaveProgress({ current: 0, total: 0, status: 'idle' });
    }
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const selectedResults = selectedIndices.map(index => results[index]).filter(result => result && result.success);

  const handleSave = async () => {
    if (selectedResults.length === 0) return;

    const targetCollection = isNewCollection ? newCollectionName.trim() : collectionName;
    
    if (!targetCollection) {
      return;
    }

    setSaveProgress({
      current: 0,
      total: selectedResults.length,
      status: 'saving'
    });

    let savedCount = 0;
    
    try {
      for (let i = 0; i < selectedResults.length; i++) {
        const result = selectedResults[i];
        
        // Create content with metadata
        const contentWithMetadata = `# ${result.title || 'Untitled Page'}

**URL:** ${result.url}  
**Crawled:** ${new Date(result.metadata.crawl_time).toLocaleString()}  
**Depth:** ${result.depth}  
${result.metadata.score > 0 ? `**Score:** ${result.metadata.score.toFixed(1)}  ` : ''}

---

${result.content}`;

        await storeContent(contentWithMetadata, targetCollection);
        savedCount++;
        
        setSaveProgress({
          current: i + 1,
          total: selectedResults.length,
          status: `saving (${i + 1}/${selectedResults.length})`
        });
      }

      setSaveProgress({
        current: savedCount,
        total: selectedResults.length,
        status: 'completed'
      });

      if (onSaveComplete) {
        onSaveComplete(targetCollection, savedCount);
      }
      
      // Reset form
      setTimeout(() => {
        setNewCollectionName('');
        setIsNewCollection(false);
        setCollectionName('default');
        setSaveProgress({ current: 0, total: 0, status: 'idle' });
        onClose();
      }, 1000);

    } catch (error) {
      console.error('Failed to save results:', error);
      setSaveProgress({
        current: savedCount,
        total: selectedResults.length,
        status: 'failed'
      });
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

  const isSaving = saveProgress.status === 'saving';
  const isCompleted = saveProgress.status === 'completed';

  const modalContent = (
    <div 
      className="fixed inset-0 flex items-center justify-center" 
      style={{ 
        zIndex: 999999,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        display: 'flex !important',
        visibility: 'visible' as any,
        opacity: '1 !important',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4"
        style={{
          visibility: 'visible',
          opacity: 1,
          display: 'block',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb'
        }}
      >
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Bulk Save to Collection
          </h3>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* Selection Summary */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-blue-600 dark:text-blue-400" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  {selectedResults.length} successful results selected
                </p>
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  {selectedIndices.length - selectedResults.length > 0 && 
                    `${selectedIndices.length - selectedResults.length} failed results will be skipped`
                  }
                </p>
              </div>
            </div>
          </div>

          {/* Collection Selection */}
          {!isSaving && !isCompleted && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Collection
              </label>
              
              {!isNewCollection ? (
                <select
                  value={collectionName}
                  onChange={(e) => handleCollectionChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                  data-testid="bulk-collection-select"
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
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                    data-testid="bulk-collection-name"
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
          )}

          {/* Progress Display */}
          {isSaving && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
              <div className="flex items-center">
                <svg className="animate-spin h-5 w-5 text-green-600" width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-green-800 dark:text-green-200">
                    Saving Results...
                  </p>
                  <div className="flex items-center mt-1">
                    <div className="flex-1 bg-green-200 dark:bg-green-800 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(saveProgress.current / saveProgress.total) * 100}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm text-green-700 dark:text-green-300">
                      {saveProgress.current}/{saveProgress.total}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Completion Display */}
          {isCompleted && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-green-600" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <div className="ml-3">
                  <p className="text-sm font-medium text-green-800 dark:text-green-200">
                    Successfully saved {saveProgress.current} results!
                  </p>
                </div>
              </div>
            </div>
          )}

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
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors disabled:opacity-50"
          >
            {isCompleted ? 'Close' : 'Cancel'}
          </button>
          
          {!isSaving && !isCompleted && (
            <button
              onClick={handleSave}
              disabled={
                selectedResults.length === 0 ||
                (isNewCollection && !newCollectionName.trim()) ||
                (!isNewCollection && !collectionName)
              }
              data-testid="bulk-save-confirm"
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md transition-colors"
            >
              Save {selectedResults.length} Results
            </button>
          )}
        </div>
      </div>
    </div>
  );

  // Use portal but with better error handling
  const portalRoot = typeof document !== 'undefined' ? document.body : null;
  if (!portalRoot) return null;
  
  return createPortal(modalContent, portalRoot);
}

export default BulkSaveModal;