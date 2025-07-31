import { useState } from 'react';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SimpleCrawlPage from './pages/SimpleCrawlPage';
import DeepCrawlPage from './pages/DeepCrawlPage';
import CollectionsPage from './pages/CollectionsPage';
import FileCollectionsPage from './pages/FileCollectionsPage';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './components/ToastContainer';
import { AppThemeProvider } from './contexts/ThemeContext';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections' | 'file-collections';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'simple-crawl':
        return <SimpleCrawlPage />;
      case 'deep-crawl':
        return <DeepCrawlPage />;
      case 'collections':
        return <CollectionsPage />;
      case 'file-collections':
        return <FileCollectionsPage />;
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <AppThemeProvider>
      <ErrorBoundary>
        <ToastProvider>
          <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
            {renderCurrentPage()}
          </Layout>
        </ToastProvider>
      </ErrorBoundary>
    </AppThemeProvider>
  );
}

export default App;