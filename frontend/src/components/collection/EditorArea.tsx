import React from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import MarkdownEditor from '../MarkdownEditor';

interface EditorAreaProps {
  className?: string;
}

export function EditorArea({ className = '' }: EditorAreaProps) {
  const { 
    state, 
    updateContent, 
    saveCurrentFile, 
    closeFile 
  } = useCollectionOperations();

  const handleSave = async () => {
    if (state.selectedCollection && state.editor.modified) {
      try {
        await saveCurrentFile(state.selectedCollection);
      } catch (error) {
        // Error is already handled in the hook
        console.error('Failed to save file:', error);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  if (!state.editor.filePath) {
    return (
      <div className={`bg-white dark:bg-gray-800 ${className}`}>
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <svg className="mx-auto h-8 w-8 text-gray-400 flex-shrink-0" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No File Selected
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Select a file from the explorer to start editing
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 flex flex-col ${className}`} onKeyDown={handleKeyDown}>
      {/* Editor Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <h2 className="text-sm font-medium text-gray-900 dark:text-white">
              {state.editor.filePath}
            </h2>
            {state.editor.modified && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-200">
                Modified
              </span>
            )}
            {state.editor.saving && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-200">
                Saving...
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleSave}
              disabled={!state.editor.modified || state.editor.saving}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {state.editor.saving ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving
                </>
              ) : (
                <>
                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Save
                </>
              )}
            </button>
            
            <button
              onClick={closeFile}
              className="inline-flex items-center p-1.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded transition-colors"
              title="Close file"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <MarkdownEditor
          content={state.editor.content}
          onChange={updateContent}
          onSave={() => {
            handleSave();
          }}
        />
      </div>
    </div>
  );
}

export default EditorArea;