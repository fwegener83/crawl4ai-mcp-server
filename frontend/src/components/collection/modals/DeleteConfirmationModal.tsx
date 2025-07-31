import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import Icon from '../../ui/Icon';

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
      return <Icon name="folder" size="lg" color="red" />;
    }
    return <Icon name="document" size="lg" color="red" />;
  };

  return (
    <div className="fixed inset-0 !bg-gray-900 !bg-opacity-75 overflow-y-auto h-full w-full !z-[9999]" style={{ backgroundColor: 'rgba(31, 41, 55, 0.75)' }}>
      <div className="relative top-20 mx-auto p-5 border border-gray-300 dark:border-gray-600 w-96 shadow-2xl rounded-md !bg-white dark:!bg-gray-800 !z-[10000]" style={{ backgroundColor: 'white' }}>
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