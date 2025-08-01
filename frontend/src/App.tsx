import { useState } from 'react';
import { Box, Container } from './components/ui';
import { NavigationSidebar } from './components/organisms';
import { NotificationProvider } from './components/ui/NotificationProvider';
import HomePage from './pages/HomePage';
import SimpleCrawlPage from './pages/SimpleCrawlPage';
import DeepCrawlPage from './pages/DeepCrawlPage';
import CollectionsPage from './pages/CollectionsPage';
import FileCollectionsPage from './pages/FileCollectionsPage';
import SettingsPage from './pages/SettingsPage';
import ErrorBoundary from './components/ErrorBoundary';
import { AppThemeProvider } from './contexts/ThemeContext';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections' | 'file-collections' | 'settings';

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
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <NavigationSidebar
              currentPath={`/${currentPage}`}
              onNavigate={(path: string) => {
                const page = path.slice(1) as Page;
                setCurrentPage(page || 'home');
              }}
            />
            <Box component="main" sx={{ flexGrow: 1, overflow: 'hidden' }}>
              <Container
                maxWidth={false}
                sx={{
                  height: '100vh',
                  py: 3,
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                {renderCurrentPage()}
              </Container>
            </Box>
          </Box>
        </NotificationProvider>
      </ErrorBoundary>
    </AppThemeProvider>
  );
}

export default App;