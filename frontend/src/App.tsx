import { useState } from 'react';
import { Box, Container } from './components/ui';
import TopNavigation from './components/navigation/TopNavigation';
import { NotificationProvider } from './components/ui/NotificationProvider';
import { CollectionProvider } from './contexts/CollectionContext';
import FileCollectionsPage from './pages/FileCollectionsPage';
import RAGQueryPage from './pages/RAGQueryPage';
import ErrorBoundary from './components/ErrorBoundary';
import { AppThemeProvider } from './contexts/ThemeContext';

type Page = 'file-collections' | 'rag-query';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('file-collections');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'file-collections':
        return <FileCollectionsPage />;
      case 'rag-query':
        return <RAGQueryPage />;
      default:
        return <FileCollectionsPage />;
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