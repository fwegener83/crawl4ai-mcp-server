import React from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import LoadingSpinner from '../LoadingSpinner';

interface FileExplorerProps {
  className?: string;
}

export function FileExplorer({ className = '' }: FileExplorerProps) {
  const { state, openFile, openDeleteConfirmation } = useCollectionOperations();

  const handleFileClick = (filename: string, folder?: string) => {
    if (state.selectedCollection) {
      openFile(state.selectedCollection, filename, folder);
    }
  };

  const handleFileDelete = (filename: string, e: React.MouseEvent, folder?: string) => {
    e.stopPropagation();
    const filePath = folder ? `${folder}/${filename}` : filename;
    openDeleteConfirmation('file', filePath);
  };

  if (state.ui.loading.files) {
    return (
      <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="p-4">
          <div className="flex items-center justify-center">
            <LoadingSpinner size="sm" />
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading files...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Files & Folders</h3>
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto">
        {state.files.length === 0 && state.folders.length === 0 ? (
          <div className="p-4 text-center">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">No files in this collection</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Add pages by crawling URLs or create new files manually
            </p>
          </div>
        ) : (
          <div className="p-2">
            {/* Folders */}
            {state.folders.map((folder) => (
              <div
                key={folder.path}
                className="group p-2 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              >
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-4 w-4 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  <span className="text-sm text-gray-900 dark:text-white">{folder.name}</span>
                </div>
              </div>
            ))}

            {/* Files */}
            {state.files.map((file) => (
              <div
                key={file.path}
                onClick={() => handleFileClick(file.name, file.metadata.folder_path || undefined)}
                className={`group p-2 rounded-md cursor-pointer transition-colors ${
                  state.editor.filePath === file.path
                    ? 'bg-blue-50 dark:bg-blue-900/50 border border-blue-200 dark:border-blue-800'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <svg className="flex-shrink-0 h-4 w-4 text-gray-400 dark:text-gray-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div className="min-w-0 flex-1">
                      <p className={`text-sm truncate ${
                        state.editor.filePath === file.path
                          ? 'text-blue-700 dark:text-blue-300 font-medium'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {file.name}
                      </p>
                      {file.metadata.source_url && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          from {new URL(file.metadata.source_url).hostname}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Delete button */}
                  <button
                    onClick={(e) => handleFileDelete(file.name, e, file.metadata.folder_path || undefined)}
                    className="opacity-0 group-hover:opacity-100 ml-2 p-1 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-all"
                    title="Delete file"
                  >
                    <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
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

export default FileExplorer;