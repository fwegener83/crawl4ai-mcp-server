import { useCollectionOperations } from '../../../hooks/useCollectionOperations';

export function DeleteConfirmationModal() {
  const { state, deleteCollection, deleteFile, closeDeleteConfirmation } = useCollectionOperations();

  if (!state.ui.modals.deleteConfirmation.open) {
    return null;
  }

  const { type, target } = state.ui.modals.deleteConfirmation;

  const handleConfirm = async () => {
    if (!target) return;

    try {
      if (type === 'collection') {
        await deleteCollection(target);
      } else if (type === 'file' && state.selectedCollection) {
        // Parse file path to get filename and folder
        const pathParts = target.split('/');
        const filename = pathParts.pop()!;
        const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
        await deleteFile(state.selectedCollection, filename, folder);
      }
    } catch (error) {
      // Error is handled in the hook
      console.error(`Failed to delete ${type}:`, error);
    }
  };

  const getTitle = () => {
    if (type === 'collection') {
      return 'Delete Collection';
    }
    return 'Delete File';
  };

  const getMessage = () => {
    if (type === 'collection') {
      return `Are you sure you want to delete the collection "${target}"? This will permanently delete all files and folders within this collection. This action cannot be undone.`;
    }
    return `Are you sure you want to delete the file "${target}"? This action cannot be undone.`;
  };

  const getIcon = () => {
    if (type === 'collection') {
      return (
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      );
    }
    return (
      <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    );
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 overflow-y-auto h-full w-full z-[100]">
      <div className="relative top-20 mx-auto p-5 border border-gray-300 dark:border-gray-600 w-96 shadow-2xl rounded-md bg-white dark:bg-gray-800 z-[101]">
        <div className="mt-3">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              {getIcon()}
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {getTitle()}
              </h3>
            </div>
          </div>
          
          <div className="mb-6">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {getMessage()}
            </p>
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              onClick={closeDeleteConfirmation}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
            >
              Delete {type === 'collection' ? 'Collection' : 'File'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DeleteConfirmationModal;