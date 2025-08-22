import React from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import { useVectorSync } from '../../hooks/useVectorSync';
import { EnhancedSyncControls } from './EnhancedSyncControls';
import AddContentMenu from './AddContentMenu';
import FileExplorer from './FileExplorer';
import EditorArea from './EditorArea';
import { Box, Typography, Paper, Button } from '../ui';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';

interface MainContentProps {
  className?: string;
}


export function MainContent({ className = '' }: MainContentProps) {
  const { state, openModal } = useCollectionOperations();
  const { 
    getSyncStatus, 
    syncCollection,
    loadSyncStatuses,
    refreshSyncStatus
  } = useVectorSync();
  
  // Load sync statuses when collection is selected
  React.useEffect(() => {
    if (state.selectedCollection) {
      console.log('🔄 Collection selected, loading sync statuses:', state.selectedCollection);
      loadSyncStatuses();
    }
  }, [state.selectedCollection, loadSyncStatuses]);

  // Vector sync handlers - bind collection name
  const handleSyncCollection = async () => {
    if (state.selectedCollection) {
      await syncCollection(state.selectedCollection);
    }
  };

  // Manual refresh handler
  const handleManualRefresh = async () => {
    if (state.selectedCollection) {
      await refreshSyncStatus(state.selectedCollection);
    }
  };

  // Simplified sync callbacks
  const handleSyncStarted = () => {
    console.log('🚀 Sync started');
  };

  const handleSyncCompleted = () => {
    console.log('✅ Sync completed');
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
              {/* Enhanced Vector Sync Controls */}
              {state.selectedCollection && (
                <EnhancedSyncControls
                  collectionId={state.selectedCollection}
                  collectionName={selectedCollection?.name || state.selectedCollection}
                  syncStatus={getSyncStatus(state.selectedCollection)}
                  onSyncStarted={handleSyncStarted}
                  onSyncCompleted={handleSyncCompleted}
                  onRefresh={handleManualRefresh}
                  size="small"
                />
              )}
              
              {/* Consolidated Add Content Menu */}
              <AddContentMenu
                onAddFile={() => openModal('newFile')}
                onAddPage={() => openModal('addPage')}
                onAddMultiplePages={() => openModal('addMultiplePages')}
              />
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
        
        {/* Editor Area */}
        <Box sx={{ flex: 1, bgcolor: 'background.default' }}>
          <EditorArea />
        </Box>
      </Box>
    </Box>
  );
}

export default MainContent;