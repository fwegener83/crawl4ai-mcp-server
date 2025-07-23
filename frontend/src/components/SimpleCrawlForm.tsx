import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { APIService } from '../services/api';
import { useToast } from './ToastContainer';
import { parseAPIError } from '../utils/errorHandling';

interface SimpleCrawlFormProps {
  onCrawlComplete?: (content: string) => void;
}

export function SimpleCrawlForm({ onCrawlComplete }: SimpleCrawlFormProps) {
  const [url, setUrl] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);
  const crawlApi = useApi<string>();
  const { showError } = useToast();

  const validateUrl = (inputUrl: string): boolean => {
    try {
      new URL(inputUrl);
      return true;
    } catch {
      return inputUrl === ''; // Empty is valid (not submitted yet)
    }
  };

  const handleUrlChange = (value: string) => {
    setUrl(value);
    setIsValidUrl(validateUrl(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim() || !isValidUrl) {
      setIsValidUrl(false);
      return;
    }

    try {
      const content = await crawlApi.execute(() => 
        APIService.extractWebContent(url.trim())
      );
      
      if (onCrawlComplete) {
        onCrawlComplete(content);
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      const parsedError = parseAPIError(error);
      showError(parsedError.title, parsedError.message);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9"></path>
          </svg>
        </div>
        <h3 className="ml-3 text-lg font-semibold text-gray-900 dark:text-white">
          Simple Website Crawling
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Website URL
          </label>
          <input
            type="url"
            id="url"
            data-testid="url-input"
            value={url}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder="https://example.com"
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
              !isValidUrl 
                ? 'border-red-300 dark:border-red-600 focus:border-red-500' 
                : 'border-gray-300 dark:border-gray-600 focus:border-blue-500'
            }`}
            disabled={crawlApi.loading}
          />
          {!isValidUrl && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              Please enter a valid URL (e.g., https://example.com)
            </p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Extract clean content from any webpage
          </div>
          <button
            type="submit"
            data-testid="crawl-button"
            disabled={crawlApi.loading || !url.trim() || !isValidUrl}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded-md transition-colors flex items-center space-x-2"
          >
            {crawlApi.loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Crawling...</span>
              </>
            ) : (
              <span>Start Crawl</span>
            )}
          </button>
        </div>
      </form>

    </div>
  );
}

export default SimpleCrawlForm;