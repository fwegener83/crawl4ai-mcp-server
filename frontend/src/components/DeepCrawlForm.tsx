import { useState } from 'react';
import { useCrawling } from '../hooks/useApi';
import { APIService } from '../services/api';
import type { DeepCrawlConfig, CrawlResult } from '../types/api';

interface DeepCrawlFormProps {
  onCrawlComplete?: (results: CrawlResult[]) => void;
}

export function DeepCrawlForm({ onCrawlComplete }: DeepCrawlFormProps) {
  const [config, setConfig] = useState<DeepCrawlConfig>({
    domain_url: '',
    max_depth: 2,
    crawl_strategy: 'bfs',
    max_pages: 10,
    include_external: false,
    url_patterns: [],
    exclude_patterns: [],
    keywords: [],
    stream_results: false,
  });

  const [urlPatternsText, setUrlPatternsText] = useState('');
  const [excludePatternsText, setExcludePatternsText] = useState('');
  const [keywordsText, setKeywordsText] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);

  const { startCrawl, loading, error, progress } = useCrawling();

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return url === '';
    }
  };

  const handleUrlChange = (url: string) => {
    setConfig(prev => ({ ...prev, domain_url: url }));
    setIsValidUrl(validateUrl(url));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!config.domain_url.trim() || !isValidUrl) {
      setIsValidUrl(false);
      return;
    }

    // Parse text inputs into arrays
    const finalConfig: DeepCrawlConfig = {
      ...config,
      url_patterns: urlPatternsText.trim() 
        ? urlPatternsText.split('\n').map(p => p.trim()).filter(p => p)
        : undefined,
      exclude_patterns: excludePatternsText.trim()
        ? excludePatternsText.split('\n').map(p => p.trim()).filter(p => p)
        : undefined,
      keywords: keywordsText.trim()
        ? keywordsText.split(',').map(k => k.trim()).filter(k => k)
        : undefined,
    };

    try {
      const results = await startCrawl(() => 
        APIService.deepCrawlDomain(finalConfig)
      );
      
      if (onCrawlComplete) {
        onCrawlComplete(results);
      }
    } catch (error) {
      console.error('Deep crawl failed:', error);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
        </div>
        <h3 className="ml-3 text-lg font-semibold text-gray-900 dark:text-white">
          Deep Website Crawling
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Domain URL */}
        <div>
          <label htmlFor="domain_url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Domain URL *
          </label>
          <input
            type="url"
            id="domain_url"
            data-testid="domain-url-input"
            value={config.domain_url}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder="https://example.com"
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white ${
              !isValidUrl 
                ? 'border-red-300 dark:border-red-600 focus:border-red-500' 
                : 'border-gray-300 dark:border-gray-600 focus:border-green-500'
            }`}
            disabled={loading}
          />
          {!isValidUrl && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              Please enter a valid domain URL
            </p>
          )}
        </div>

        {/* Strategy and Depth */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="crawl_strategy" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Crawl Strategy
            </label>
            <select
              id="crawl_strategy"
              value={config.crawl_strategy}
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                crawl_strategy: e.target.value as 'bfs' | 'dfs' | 'best_first' 
              }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            >
              <option value="bfs">Breadth-First (BFS)</option>
              <option value="dfs">Depth-First (DFS)</option>
              <option value="best_first">Best-First (Keyword-based)</option>
            </select>
          </div>

          <div>
            <label htmlFor="max_depth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Depth
            </label>
            <input
              type="number"
              id="max_depth"
              min="1"
              max="10"
              value={config.max_depth}
              onChange={(e) => setConfig(prev => ({ ...prev, max_depth: parseInt(e.target.value) || 1 }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="max_pages" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Pages
            </label>
            <input
              type="number"
              id="max_pages"
              min="1"
              max="1000"
              value={config.max_pages}
              onChange={(e) => setConfig(prev => ({ ...prev, max_pages: parseInt(e.target.value) || 1 }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>
        </div>

        {/* Include External Links */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="include_external"
            checked={config.include_external}
            onChange={(e) => setConfig(prev => ({ ...prev, include_external: e.target.checked }))}
            className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            disabled={loading}
          />
          <label htmlFor="include_external" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Include external links (links outside the domain)
          </label>
        </div>

        {/* URL Patterns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="url_patterns" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Include URL Patterns
              <span className="text-xs text-gray-500 ml-1">(one per line, glob patterns)</span>
            </label>
            <textarea
              id="url_patterns"
              rows={3}
              value={urlPatternsText}
              onChange={(e) => setUrlPatternsText(e.target.value)}
              placeholder="*/blog/*&#10;*/news/*&#10;*/articles/*"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="exclude_patterns" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Exclude URL Patterns
              <span className="text-xs text-gray-500 ml-1">(one per line, glob patterns)</span>
            </label>
            <textarea
              id="exclude_patterns"
              rows={3}
              value={excludePatternsText}
              onChange={(e) => setExcludePatternsText(e.target.value)}
              placeholder="*/admin/*&#10;*/login/*&#10;*.pdf"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>
        </div>

        {/* Keywords for Best-First Strategy */}
        {config.crawl_strategy === 'best_first' && (
          <div>
            <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Keywords for Scoring
              <span className="text-xs text-gray-500 ml-1">(comma-separated)</span>
            </label>
            <input
              type="text"
              id="keywords"
              value={keywordsText}
              onChange={(e) => setKeywordsText(e.target.value)}
              placeholder="react, javascript, tutorial, guide"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Pages containing these keywords will be prioritized
            </p>
          </div>
        )}

        {/* Progress Display */}
        {loading && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <div className="flex items-center">
              <svg className="animate-spin h-5 w-5 text-blue-600" width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Deep Crawling in Progress
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Status: {progress.status} ({progress.current}/{progress.total})
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Crawl multiple pages with advanced filtering and strategies
          </div>
          <button
            type="submit"
            data-testid="deep-crawl-button"
            disabled={loading || !config.domain_url.trim() || !isValidUrl}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded-md transition-colors flex items-center space-x-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" width="16" height="16" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Crawling...</span>
              </>
            ) : (
              <span>Start Deep Crawl</span>
            )}
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex">
            <svg className="flex-shrink-0 h-5 w-5 text-red-400" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Deep Crawling Failed
              </h3>
              <div className="mt-1 text-sm text-red-700 dark:text-red-300">
                {error}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DeepCrawlForm;