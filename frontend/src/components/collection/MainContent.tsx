import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import { useVectorSync } from '../../hooks/useVectorSync';
import CompactSyncStatus from './CompactSyncStatus';
import AddContentMenu from './AddContentMenu';
import FileExplorer from './FileExplorer';
import EditorArea from './EditorArea';
import { Box, Typography, Paper, Button } from '../ui';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';

interface MainContentProps {
  className?: string;
}

// Helper function to map backend status to compact status format
const mapSyncStatus = (status: string): 'synced' | 'syncing' | 'error' | 'never_synced' => {
  switch (status) {
    case 'in_sync':
    case 'synced':
      return 'synced';
    case 'syncing':
      return 'syncing';
    case 'sync_error':
    case 'partial_sync':
      return 'error';
    case 'never_synced':
    case 'out_of_sync':
      return 'never_synced';
    default:
      return 'never_synced';
  }
};

// Helper function to format relative time
const formatRelativeTime = (lastSync: string | null): string | undefined => {
  if (!lastSync) return undefined;
  
  try {
    const syncDate = new Date(lastSync);
    const now = new Date();
    const diffMs = now.getTime() - syncDate.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMinutes < 1) return 'just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  } catch {
    return 'unknown';
  }
};

export function MainContent({ className = '' }: MainContentProps) {
  const { state, openModal } = useCollectionOperations();
  const { 
    getSyncStatus, 
    syncCollection
  } = useVectorSync();
  

  // Vector sync handlers - bind collection name
  const handleSyncCollection = async () => {
    if (state.selectedCollection) {
      await syncCollection(state.selectedCollection);
    }
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
              {/* Compact Vector Sync Status */}
              {state.selectedCollection && getSyncStatus(state.selectedCollection) && (
                <CompactSyncStatus
                  data-testid="compact-sync-status"
                  status={mapSyncStatus(getSyncStatus(state.selectedCollection)!.status)}
                  fileCount={getSyncStatus(state.selectedCollection)!.total_files}
                  chunkCount={getSyncStatus(state.selectedCollection)!.chunk_count}
                  lastSync={formatRelativeTime(getSyncStatus(state.selectedCollection)!.last_sync)}
                  onClick={handleSyncCollection}
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