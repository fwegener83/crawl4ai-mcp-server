import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import MarkdownEditor from './MarkdownEditor';
import SaveToCollectionModal from './SaveToCollectionModal';
import { useToast } from './ToastContainer';
import type { CrawlResult } from '../types/api';

interface DocumentViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: CrawlResult | null;
}

export function DocumentViewerModal({ 
  isOpen, 
  onClose, 
  result 
}: DocumentViewerModalProps) {
  const [editedContent, setEditedContent] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const { showSuccess } = useToast();

  useEffect(() => {
    if (result && isOpen) {
      // Create formatted content with metadata
      const formattedContent = `# ${result.title || 'Untitled Page'}

**URL:** ${result.url}  
**Crawled:** ${new Date(result.metadata.crawl_time).toLocaleString()}  
**Depth:** ${result.depth}  
${result.metadata.score > 0 ? `**Score:** ${result.metadata.score.toFixed(1)}  ` : ''}

---

${result.content}`;
      
      setEditedContent(formattedContent);
      setHasUnsavedChanges(false);
    }
  }, [result, isOpen]);

  const handleContentChange = (content: string) => {
    setEditedContent(content);
    setHasUnsavedChanges(content !== (result?.content || ''));
  };

  const handleSaveClick = () => {
    if (editedContent.trim()) {
      setShowSaveModal(true);
    }
  };

  const handleSaveComplete = (collectionName: string) => {
    setHasUnsavedChanges(false);
    showSuccess('Document Saved', `Successfully saved to collection: ${collectionName}`);
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  if (!isOpen || !result) return null;

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
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full h-full max-w-6xl max-h-[90vh] mx-4 my-4 flex flex-col"
        style={{
          visibility: 'visible',
          opacity: 1,
          display: 'flex',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb'
        }}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
              Document Viewer & Editor
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {result.title || 'Untitled Page'}
            </p>
          </div>
          
          <div className="flex items-center space-x-3 ml-4">
            <button
              onClick={handleSaveClick}
              disabled={!editedContent.trim()}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-md transition-colors"
              data-testid="document-save-button"
            >
              Save to Collection
              {hasUnsavedChanges && (
                <span className="ml-2 text-xs bg-orange-500 px-1.5 py-0.5 rounded-full">
                  •
                </span>
              )}
            </button>
            
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="h-6 w-6" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Document Info */}
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-750 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-6 text-xs text-gray-600 dark:text-gray-400">
            <span><strong>URL:</strong> {result.url}</span>
            <span><strong>Depth:</strong> {result.depth}</span>
            {result.metadata.score > 0 && (
              <span><strong>Score:</strong> {result.metadata.score.toFixed(1)}</span>
            )}
            <span><strong>Size:</strong> {result.content.length.toLocaleString()} chars</span>
            <span><strong>Crawled:</strong> {new Date(result.metadata.crawl_time).toLocaleString()}</span>
          </div>
        </div>

        {/* Editor Content */}
        <div className="flex-1 overflow-hidden">
          <MarkdownEditor
            content={editedContent}
            onChange={handleContentChange}
            onSave={handleSaveClick}
          />
        </div>
      </div>
    </div>
  );

  // Use portal for proper modal rendering
  const portalRoot = typeof document !== 'undefined' ? document.body : null;
  if (!portalRoot) return null;
  
  return (
    <>
      {createPortal(modalContent, portalRoot)}
      
      {/* Save Modal */}
      <SaveToCollectionModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        content={editedContent}
        onSaveComplete={handleSaveComplete}
      />
    </>
  );
}

export default DocumentViewerModal;