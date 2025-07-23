import { useState } from 'react';
import SimpleCrawlForm from '../components/SimpleCrawlForm';
import MarkdownEditor from '../components/MarkdownEditor';
import SaveToCollectionModal from '../components/SaveToCollectionModal';
import { useToast } from '../components/ToastContainer';

export function SimpleCrawlPage() {
  const [crawledContent, setCrawledContent] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const { showSuccess } = useToast();

  const handleCrawlComplete = (content: string) => {
    setCrawledContent(content);
    setEditedContent(content);
    showSuccess('Content Extracted', 'Website content has been successfully crawled and is ready for editing.');
  };

  const handleContentChange = (content: string) => {
    setEditedContent(content);
  };

  const handleSaveClick = () => {
    if (editedContent.trim()) {
      setShowSaveModal(true);
    }
  };

  const handleSaveComplete = (collectionName: string) => {
    showSuccess('Content Saved', `Successfully saved to collection: ${collectionName}`);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Simple Website Crawling
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Extract clean content from any webpage and edit it with our markdown editor.
        </p>
      </div>


      {/* Crawl Form */}
      <SimpleCrawlForm onCrawlComplete={handleCrawlComplete} />

      {/* Content Editor */}
      {crawledContent && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Extracted Content
            </h2>
            <button
              onClick={handleSaveClick}
              disabled={!editedContent.trim()}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-md transition-colors"
            >
              Save to Collection
            </button>
          </div>
          
          <MarkdownEditor
            content={crawledContent}
            onChange={handleContentChange}
            onSave={handleSaveClick}
          />
        </div>
      )}

      {/* Empty State */}
      {!crawledContent && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            No content yet
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Enter a URL above to start crawling and see the extracted content here.
          </p>
        </div>
      )}

      {/* Save Modal */}
      <SaveToCollectionModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        content={editedContent}
        onSaveComplete={handleSaveComplete}
      />
    </div>
  );
}

export default SimpleCrawlPage;