import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import FileExplorer from './FileExplorer';
import EditorArea from './EditorArea';
import { Box, Typography, Button, Paper } from '../ui';
import AddIcon from '@mui/icons-material/Add';
import DescriptionIcon from '@mui/icons-material/Description';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';

interface MainContentProps {
  className?: string;
}

export function MainContent({ className = '' }: MainContentProps) {
  const { state, openModal } = useCollectionOperations();

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
  const selectedCollection = state.collections.find(c => c.name === state.selectedCollection);

  return (
    <Box 
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
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Button
                onClick={() => openModal('addPage')}
                variant="contained"
                color="success"
                size="medium"
                startIcon={<WebIcon />}
              >
                Add Page
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
        
        {/* Editor Area */}
        <Box sx={{ flex: 1, bgcolor: 'background.default' }}>
          <EditorArea />
        </Box>
      </Box>
    </Box>
  );
}

export default MainContent;