import { useState } from 'react';
import { Box, Container } from './components/ui';
import TopNavigation from './components/navigation/TopNavigation';
import { NotificationProvider } from './components/ui/NotificationProvider';
import { CollectionProvider } from './contexts/CollectionContext';
import HomePage from './pages/HomePage';
import SimpleCrawlPage from './pages/SimpleCrawlPage';
import DeepCrawlPage from './pages/DeepCrawlPage';
// CollectionsPage removed - RAG Knowledge Base replaced by File Collections
import FileCollectionsPage from './pages/FileCollectionsPage';
import SettingsPage from './pages/SettingsPage';
import ErrorBoundary from './components/ErrorBoundary';
import { AppThemeProvider } from './contexts/ThemeContext';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections' | 'file-collections' | 'settings';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('file-collections');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'simple-crawl':
        return <SimpleCrawlPage />;
      case 'deep-crawl':
        return <DeepCrawlPage />;
      case 'collections':
        return <FileCollectionsPage />; // Redirect RAG collections to File Collections
      case 'file-collections':
        return <FileCollectionsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <AppThemeProvider>
      <ErrorBoundary>
        <NotificationProvider>
          <CollectionProvider>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              minHeight: '100vh',
              bgcolor: 'background.default'
            }}>
              {/* Top Navigation Bar */}
              <TopNavigation
                currentPage={currentPage}
                onNavigate={(page: string) => {
                  setCurrentPage(page as Page);
                }}
                onSettingsClick={() => setCurrentPage('settings')}
              />
              
              {/* Main Content Area */}
              <Box component="main" sx={{ flex: 1, overflow: 'hidden' }}>
                <Container
                  maxWidth={false}
                  sx={{
                    height: 'calc(100vh - 64px)',
                    py: 3,
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  {renderCurrentPage()}
                </Container>
              </Box>
            </Box>
          </CollectionProvider>
        </NotificationProvider>
      </ErrorBoundary>
    </AppThemeProvider>
  );
}

export default App;