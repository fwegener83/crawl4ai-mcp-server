import { useState } from 'react';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SimpleCrawlPage from './pages/SimpleCrawlPage';
import DeepCrawlPage from './pages/DeepCrawlPage';

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
        return <div>Collections Page (Coming Soon)</div>;
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderCurrentPage()}
    </Layout>
  );
}

export default App;