import React from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import { useVectorSync } from '../../hooks/useVectorSync';
import { CollectionSyncButton } from './CollectionSyncButton';
import { VectorSyncIndicator } from './VectorSyncIndicator';
import { VectorSearchPanel } from './VectorSearchPanel';
import FileExplorer from './FileExplorer';
import EditorArea from './EditorArea';
import { Box, Typography, Button, Paper, IconButton, Collapse } from '../ui';
import DescriptionIcon from '@mui/icons-material/Description';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import SearchIcon from '@mui/icons-material/Search';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

interface MainContentProps {
  className?: string;
}

export function MainContent({ className = '' }: MainContentProps) {
  const { state, openModal } = useCollectionOperations();
  const { 
    getSyncStatus, 
    syncCollection, 
    searchVectors,
    searchResults: vectorSearchResults,
    searchQuery: vectorSearchQuery,
    searchLoading: vectorSearchLoading,
    clearSearch: clearVectorSearch
  } = useVectorSync();
  
  const [searchPanelOpen, setSearchPanelOpen] = React.useState(false);

  // Vector search handlers
  const handleVectorSearch = async (query: string, collectionId?: string) => {
    if (state.selectedCollection) {
      await searchVectors(query, collectionId || state.selectedCollection);
    }
  };

  const handleSearchResultClick = (result: unknown) => {
    // TODO: Navigate to file and highlight the chunk
    console.log('Navigate to:', result);
  };

  // Vector sync handlers - bind collection name
  const handleSyncCollection = async () => {
    if (state.selectedCollection) {
      await syncCollection(state.selectedCollection);
    }
  };


  const toggleSearchPanel = () => {
    setSearchPanelOpen(!searchPanelOpen);
  };

  if (!state.selectedCollection) {
    return (
      <Box 
        sx={{ 
          flex: 1, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bgcolor: 'background.default',
          p: 4
        }} 
        className={className}
      >
        <Box sx={{ textAlign: 'center', maxWidth: 500 }}>
          <WebIcon 
            sx={{ 
              fontSize: 80, 
              color: 'primary.main', 
              mb: 3,
              display: 'block',
              mx: 'auto'
            }} 
          />
          <Typography variant="h4" fontWeight="bold" sx={{ mb: 2, color: 'primary.main' }}>
            Welcome to Crawl4AI File Manager
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ mb: 4, lineHeight: 1.6 }}
          >
            Organize your web content in collections. Create a collection to start crawling and managing your documents, or select an existing collection from the sidebar.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              onClick={() => openModal('newCollection')}
              variant="contained"
              startIcon={<CreateNewFolderIcon />}
              size="large"
            >
              Create New Collection
            </Button>
            <Button
              variant="outlined"
              size="large"
              disabled
            >
              Import Collection (Coming Soon)
            </Button>
          </Box>
        </Box>
      </Box>
    );
  }

  // Find the selected collection
  const selectedCollection = state.collections.find(c => c.id === state.selectedCollection);

  return (
    <Box 
      data-testid="collection-details"
      sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        bgcolor: 'background.default'
      }} 
      className={className}
    >
      {/* Collection Header */}
      <Paper 
        elevation={0}
        sx={{ 
          borderBottom: 1, 
          borderColor: 'divider',
          borderRadius: 0,
          bgcolor: 'background.paper'
        }}
      >
        <Box sx={{ px: 3, py: 2.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CreateNewFolderIcon sx={{ color: 'primary.main', mr: 1.5 }} />
              <Box>
                <Typography variant="h5" fontWeight="bold" color="primary.main">
                  {selectedCollection?.name || state.selectedCollection}
                </Typography>
                {selectedCollection?.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    {selectedCollection.description}
                  </Typography>
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
              {/* Vector Sync Status & Controls */}
              {state.selectedCollection && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <VectorSyncIndicator
                    data-testid="vector-sync-indicator"
                    collectionId={state.selectedCollection}
                    syncStatus={getSyncStatus(state.selectedCollection)}
                    showText={true}
                    size="medium"
                  />
                  <CollectionSyncButton
                    data-testid="vector-sync-btn"
                    collectionId={state.selectedCollection}
                    syncStatus={getSyncStatus(state.selectedCollection)}
                    onSync={handleSyncCollection}
                    size="medium"
                  />
                </Box>
              )}

              
              <IconButton
                onClick={toggleSearchPanel}
                color={searchPanelOpen ? 'primary' : 'default'}
                size="medium"
                sx={{ 
                  mr: 1,
                  bgcolor: searchPanelOpen ? 'primary.50' : 'transparent',
                  '&:hover': {
                    bgcolor: searchPanelOpen ? 'primary.100' : 'action.hover'
                  }
                }}
              >
                <SearchIcon />
              </IconButton>
              
              <Button
                data-testid="add-page-btn"
                onClick={() => openModal('addPage')}
                variant="contained"
                color="success"
                size="medium"
                startIcon={<WebIcon />}
              >
                Add Page
              </Button>
              <Button
                onClick={() => openModal('addMultiplePages')}
                variant="contained"
                color="primary"
                size="medium"
                startIcon={<TravelExploreIcon />}
              >
                Add Multiple Pages
              </Button>
              <Button
                onClick={() => openModal('newFile')}
                variant="outlined"
                size="medium"
                startIcon={<DescriptionIcon />}
              >
                New File
              </Button>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Content Area */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* File Explorer */}
        <Box sx={{ 
          width: 320, 
          flexShrink: 0,
          borderRight: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper'
        }}>
          <FileExplorer />
        </Box>
        
        {/* Vector Search Panel */}
        <Collapse 
          in={searchPanelOpen} 
          orientation="horizontal" 
          sx={{ display: searchPanelOpen ? 'flex' : 'none' }}
        >
          <Box sx={{ 
            width: 350, 
            flexShrink: 0,
            borderRight: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            position: 'relative'
          }}>
            {/* Toggle Button */}
            <IconButton
              onClick={toggleSearchPanel}
              size="small"
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                zIndex: 1,
                bgcolor: 'background.paper',
                border: 1,
                borderColor: 'divider',
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              <ChevronLeftIcon />
            </IconButton>

            <VectorSearchPanel
              collectionId={state.selectedCollection}
              collectionSyncStatus={getSyncStatus(state.selectedCollection)}
              searchResults={vectorSearchResults}
              searchQuery={vectorSearchQuery}
              searchLoading={vectorSearchLoading}
              onSearch={handleVectorSearch}
              onResultClick={handleSearchResultClick}
              onClearSearch={clearVectorSearch}
            />
          </Box>
        </Collapse>
        
        {/* Editor Area */}
        <Box sx={{ flex: 1, bgcolor: 'background.default' }}>
          <EditorArea />
        </Box>
      </Box>
    </Box>
  );
}

export default MainContent;