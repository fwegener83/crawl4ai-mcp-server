import { useState } from 'react';
import type React from 'react';
import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import Icon from '../../ui/Icon';

export function NewFileModal() {
  const { state, createNewFile, closeModal } = useCollectionOperations();
  const [filename, setFilename] = useState('');
  const [folder, setFolder] = useState('');
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!state.ui.modals.newFile) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filename.trim() || !state.selectedCollection) return;

    setIsSubmitting(true);
    try {
      await createNewFile(
        state.selectedCollection,
        processedFilename,
        content.trim(),
        folder.trim() || undefined
      );
      setFilename('');
      setFolder('');
      setContent('');
    } catch (error) {
      // Error is handled in the hook
      console.error('Failed to create file:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      closeModal('newFile');
      setFilename('');
      setFolder('');
      setContent('');
    }
  };

  const isValidFilename = (name: string) => {
    // Check for valid filename (no invalid characters)
    const invalidChars = /[<>:"/\\|?*]/;
    return name.trim() && !invalidChars.test(name) && name !== '.' && name !== '..';
  };

  const addMarkdownExtension = (name: string) => {
    if (!name.includes('.')) {
      return name + '.md';
    }
    return name;
  };

  const processedFilename = filename.trim() ? addMarkdownExtension(filename.trim()) : '';
  const isFormValid = filename.trim() && isValidFilename(filename.trim());

  return (
    <div className="fixed inset-0 !bg-gray-900 !bg-opacity-75 overflow-y-auto h-full w-full !z-[9999]" style={{ backgroundColor: 'rgba(31, 41, 55, 0.75)' }}>
      <div className="relative top-12 mx-auto p-5 border border-gray-300 dark:border-gray-600 max-w-md shadow-2xl rounded-md !bg-white dark:!bg-gray-800 !z-[10000]" style={{ backgroundColor: 'white' }}>
        <div className="mt-3">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              <Icon name="document" size="lg" color="blue" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Create New File
              </h3>
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Filename <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="my-document"
                required
                disabled={isSubmitting}
              />
              {filename.trim() && (
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Will be saved as: <span className="font-mono">{processedFilename}</span>
                </p>
              )}
              {filename.trim() && !isValidFilename(filename.trim()) && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                  Invalid filename. Avoid special characters: &lt; &gt; : " / \ | ? *
                </p>
              )}
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Folder (optional)
              </label>
              <input
                type="text"
                value={folder}
                onChange={(e) => setFolder(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., drafts/ideas"
                disabled={isSubmitting}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Leave empty to save in root directory. Use / to separate nested folders.
              </p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Initial Content (optional)
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-vertical"
                placeholder="# My New Document

Start writing your content here..."
                rows={6}
                disabled={isSubmitting}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Markdown formatting supported
              </p>
            </div>
            
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
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!isFormValid || isSubmitting}
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <Icon name="refresh" size="xs" color="white" animate="spin" className="mr-2" />
                    Creating...
                  </div>
                ) : (
                  'Create File'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default NewFileModal;