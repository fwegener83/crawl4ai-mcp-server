import { useState } from 'react';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SimpleCrawlPage from './pages/SimpleCrawlPage';
import DeepCrawlPage from './pages/DeepCrawlPage';
import CollectionsPage from './pages/CollectionsPage';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './components/ToastContainer';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections';

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
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <ErrorBoundary>
      <ToastProvider>
        <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
          {renderCurrentPage()}
        </Layout>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;