import { useState } from 'react';
import type React from 'react';
import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import Icon from '../../ui/Icon';

export function AddPageModal() {
  const { state, addPageToCollection, closeModal } = useCollectionOperations();
  const [url, setUrl] = useState('');
  const [folder, setFolder] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!state.ui.modals.addPage) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !state.selectedCollection) return;

    setIsSubmitting(true);
    try {
      await addPageToCollection(
        state.selectedCollection,
        url.trim(),
        folder.trim() || undefined
      );
      setUrl('');
      setFolder('');
    } catch (error) {
      // Error is handled in the hook
      console.error('Failed to add page:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      closeModal('addPage');
      setUrl('');
      setFolder('');
    }
  };

  const isValidUrl = (urlString: string) => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const isFormValid = url.trim() && isValidUrl(url.trim());

  return (
    <div className="fixed inset-0 !bg-gray-900 !bg-opacity-75 overflow-y-auto h-full w-full !z-[9999]" style={{ backgroundColor: 'rgba(31, 41, 55, 0.75)' }}>
      <div className="relative top-20 mx-auto p-5 border border-gray-300 dark:border-gray-600 w-96 shadow-2xl rounded-md !bg-white dark:!bg-gray-800 !z-[10000]" style={{ backgroundColor: 'white' }}>
        <div className="mt-3">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              <Icon name="external" size="lg" color="green" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Add Page from URL
              </h3>
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="https://example.com/article"
                required
                disabled={isSubmitting}
              />
              {url.trim() && !isValidUrl(url.trim()) && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                  Please enter a valid URL
                </p>
              )}
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Folder (optional)
              </label>
              <input
                type="text"
                value={folder}
                onChange={(e) => setFolder(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., articles/tech"
                disabled={isSubmitting}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Leave empty to save in root directory. Use / to separate nested folders.
              </p>
            </div>

            {state.ui.loading.crawling && (
              <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/50 border border-blue-200 dark:border-blue-800 rounded-md">
                <div className="flex items-center">
                  <Icon name="refresh" size="sm" color="blue" animate="spin" className="mr-2" />
                  <span className="text-sm text-blue-700 dark:text-blue-300">
                    Crawling page content...
                  </span>
                </div>
              </div>
            )}
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors disabled:opacity-50"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!isFormValid || isSubmitting}
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <Icon name="refresh" size="xs" color="white" animate="spin" className="mr-2" />
                    Crawling...
                  </div>
                ) : (
                  'Add Page'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AddPageModal;