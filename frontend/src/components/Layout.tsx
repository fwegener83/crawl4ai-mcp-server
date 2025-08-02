import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box } from './ui';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections' | 'file-collections';

interface LayoutProps {
  children: React.ReactNode;
  currentPage?: Page;
  onNavigate?: (page: Page) => void;
}

export function Layout({ children, currentPage = 'home', onNavigate }: LayoutProps) {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
      {/* Header */}
      <AppBar position="static" elevation={1} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="xl">
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Button 
              onClick={() => onNavigate?.('home')}
              sx={{ 
                fontSize: '1.25rem',
                fontWeight: 600,
                textTransform: 'none',
                color: 'inherit',
                '&:hover': {
                  color: 'primary.main'
                }
              }}
            >
              Crawl4AI Web Interface
            </Button>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button 
                onClick={() => onNavigate?.('simple-crawl')}
                variant={currentPage === 'simple-crawl' ? 'contained' : 'text'}
                color={currentPage === 'simple-crawl' ? 'primary' : 'inherit'}
                sx={{ textTransform: 'none' }}
              >
                Simple Crawl
              </Button>
              <Button 
                onClick={() => onNavigate?.('deep-crawl')}
                variant={currentPage === 'deep-crawl' ? 'contained' : 'text'}
                color={currentPage === 'deep-crawl' ? 'primary' : 'inherit'}
                sx={{ textTransform: 'none' }}
              >
                Deep Crawl
              </Button>
              <Button 
                onClick={() => onNavigate?.('collections')}
                variant={currentPage === 'collections' ? 'contained' : 'text'}
                color={currentPage === 'collections' ? 'primary' : 'inherit'}
                sx={{ textTransform: 'none' }}
              >
                Collections
              </Button>
              <Button 
                onClick={() => onNavigate?.('file-collections')}
                variant={currentPage === 'file-collections' ? 'contained' : 'text'}
                color={currentPage === 'file-collections' ? 'primary' : 'inherit'}
                sx={{ textTransform: 'none' }}
              >
                File Manager
              </Button>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Main Content */}
      <Container 
        component="main" 
        maxWidth="xl" 
        sx={{ 
          flex: 1,
          py: 3,
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {children}
      </Container>

      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          bgcolor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
          mt: 'auto'
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ py: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Powered by Crawl4AI MCP Server
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}

export default Layout;