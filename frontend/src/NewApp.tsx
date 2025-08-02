import { Box } from './components/ui';
import { NotificationProvider } from './components/ui/NotificationProvider';
import { CollectionProvider } from './contexts/CollectionContext';
import { AppThemeProvider } from './contexts/ThemeContext';
import ErrorBoundary from './components/ErrorBoundary';
import TopNavigation from './components/navigation/TopNavigation';
import CollectionFileManager from './components/collection/CollectionFileManager';

function NewApp() {
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
              <TopNavigation />
              
              {/* Main File Manager Area */}
              <Box sx={{ flex: 1, overflow: 'hidden' }}>
                <CollectionFileManager />
              </Box>
            </Box>
          </CollectionProvider>
        </NotificationProvider>
      </ErrorBoundary>
    </AppThemeProvider>
  );
}

export default NewApp;