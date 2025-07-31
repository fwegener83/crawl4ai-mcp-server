import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import FileExplorer from './FileExplorer';
import EditorArea from './EditorArea';
import Icon from '../ui/Icon';

interface MainContentProps {
  className?: string;
}

export function MainContent({ className = '' }: MainContentProps) {
  const { state, openModal } = useCollectionOperations();

  if (!state.selectedCollection) {
    return (
      <div className={`flex-1 flex items-center justify-center ${className}`}>
        <div className="text-center">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <Icon name="folder" size="xl" className="mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Select a Collection
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
            Choose a collection from the sidebar to start managing your files, or create a new collection to get started.
          </p>
          <button
            onClick={() => openModal('newCollection')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <Icon name="plus" size="sm" className="mr-2" />
            Create New Collection
          </button>
        </div>
      </div>
    );
  }

  // Find the selected collection
  const selectedCollection = state.collections.find(c => c.name === state.selectedCollection);

  return (
    <div className={`flex-1 flex flex-col ${className}`}>
      {/* Collection Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                {selectedCollection?.name || state.selectedCollection}
              </h1>
              {selectedCollection?.description && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {selectedCollection.description}
                </p>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => openModal('addPage')}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
              >
                <Icon name="document" size="sm" className="mr-2" />
                Add Page
              </button>
              <button
                onClick={() => openModal('newFile')}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <Icon name="document" size="sm" className="mr-2" />
                New File
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Explorer */}
        <FileExplorer className="w-80 flex-shrink-0" />
        
        {/* Editor Area */}
        <EditorArea className="flex-1" />
      </div>
    </div>
  );
}

export default MainContent;