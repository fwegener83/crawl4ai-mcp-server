import { useState } from 'react';
import DeepCrawlForm from '../components/DeepCrawlForm';
import CrawlResultsList from '../components/CrawlResultsList';
import BulkSaveModal from '../components/BulkSaveModal';
import type { CrawlResult } from '../types/api';

export function DeepCrawlPage() {
  const [crawlResults, setCrawlResults] = useState<CrawlResult[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [showBulkSaveModal, setShowBulkSaveModal] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const handleCrawlComplete = (results: CrawlResult[]) => {
    setCrawlResults(results);
    setSelectedIndices([]);
    setSaveSuccess(null);
  };

  const handleSelectMultiple = (_results: CrawlResult[], indices: number[]) => {
    setSelectedIndices(indices);
  };

  const handleBulkSaveClick = () => {
    if (selectedIndices.length > 0) {
      setShowBulkSaveModal(true);
    }
  };

  const handleBulkSaveComplete = (collectionName: string, savedCount: number) => {
    setSaveSuccess(`Successfully saved ${savedCount} results to collection: ${collectionName}`);
    setTimeout(() => setSaveSuccess(null), 5000);
  };

  const successfulResults = crawlResults.filter(r => r.success);
  const failedResults = crawlResults.filter(r => r.success === false);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Deep Website Crawling
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Crawl entire domains with advanced strategies, filtering, and bulk operations.
        </p>
      </div>

      {/* Success Message */}
      {saveSuccess && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md" data-testid="bulk-success-message">
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

      {/* Deep Crawl Form */}
      <DeepCrawlForm onCrawlComplete={handleCrawlComplete} />

      {/* Results Summary and Actions */}
      {crawlResults.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium text-green-600 dark:text-green-400">
                  {successfulResults.length}
                </span>
                {' '}successful
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium text-red-600 dark:text-red-400">
                  {failedResults.length}
                </span>
                {' '}failed
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium">
                  {crawlResults.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()}
                </span>
                {' '}total characters
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {selectedIndices.length} selected
              </span>
              <button
                onClick={handleBulkSaveClick}
                disabled={selectedIndices.length === 0}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-md transition-colors"
              >
                Bulk Save to Collection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results List */}
      {crawlResults.length > 0 ? (
        <CrawlResultsList
          results={crawlResults}
          onSelectMultiple={handleSelectMultiple}
          selectedIndices={selectedIndices}
        />
      ) : (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            No crawl results yet
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Configure your deep crawl settings above and start crawling to see results here.
          </p>
        </div>
      )}

      {/* Bulk Save Modal */}
      <BulkSaveModal
        isOpen={showBulkSaveModal}
        onClose={() => setShowBulkSaveModal(false)}
        results={crawlResults}
        selectedIndices={selectedIndices}
        onSaveComplete={handleBulkSaveComplete}
      />
    </div>
  );
}

export default DeepCrawlPage;