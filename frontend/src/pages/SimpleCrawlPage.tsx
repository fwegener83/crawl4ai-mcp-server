import { useState } from 'react';
import SimpleCrawlForm from '../components/SimpleCrawlForm';
import MarkdownEditor from '../components/MarkdownEditor';
import SaveToCollectionModal from '../components/SaveToCollectionModal';

export function SimpleCrawlPage() {
  const [crawledContent, setCrawledContent] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const handleCrawlComplete = (content: string) => {
    setCrawledContent(content);
    setEditedContent(content);
    setSaveSuccess(null);
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
    setSaveSuccess(`Successfully saved to collection: ${collectionName}`);
    setTimeout(() => setSaveSuccess(null), 5000);
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

      {/* Success Message */}
      {saveSuccess && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md" data-testid="success-message">
          <div className="flex">
            <svg className="flex-shrink-0 h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800 dark:text-green-200">
                {saveSuccess}
              </p>
            </div>
          </div>
        </div>
      )}

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