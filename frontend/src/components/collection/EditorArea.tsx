import React from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import MarkdownEditor from '../MarkdownEditor';
import {
  Box,
  Typography,
  Chip,
  IconButton
} from '../ui';
import { LoadingButton } from '../ui/LoadingButton';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import { CircularProgress } from '../ui';

interface EditorAreaProps {}

export function EditorArea({}: EditorAreaProps = {}) {
  const { 
    state, 
    updateContent, 
    saveCurrentFile, 
    closeFile 
  } = useCollectionOperations();

  const handleSave = async () => {
    if (state.selectedCollection && state.editor.modified) {
      try {
        await saveCurrentFile(state.selectedCollection);
      } catch (error) {
        // Error is already handled in the hook
        console.error('Failed to save file:', error);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  if (!state.editor.filePath) {
    return (
      <Box 
        sx={{ 
          bgcolor: 'background.paper',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <EditIcon 
            sx={{ 
              fontSize: 64, 
              color: 'text.secondary', 
              mb: 2 
            }} 
          />
          <Typography variant="h6" gutterBottom>
            No File Selected
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a file from the explorer to start editing
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box 
      sx={{ 
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }} 
      onKeyDown={handleKeyDown}
    >
      {/* Editor Header */}
      <Box sx={{ 
        borderBottom: 1, 
        borderColor: 'divider', 
        p: 2 
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              {state.editor.filePath}
            </Typography>
            {state.editor.modified && (
              <Chip 
                label="Modified" 
                size="small" 
                color="warning" 
                variant="outlined"
              />
            )}
            {state.editor.saving && (
              <Chip 
                label="Saving..." 
                size="small" 
                color="info" 
                variant="outlined"
                icon={<CircularProgress size={12} />}
              />
            )}
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LoadingButton
              onClick={handleSave}
              disabled={!state.editor.modified}
              loading={state.editor.saving}
              size="small"
              variant="contained"
              startIcon={<SaveIcon />}
              loadingPosition="start"
            >
              {state.editor.saving ? 'Saving' : 'Save'}
            </LoadingButton>
            
            <IconButton
              onClick={closeFile}
              size="small"
              title="Close file"
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* Editor */}
      <Box sx={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        {state.ui.loading.files && !state.editor.content ? (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%',
            flexDirection: 'column',
            gap: 2
          }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">
              Loading file content...
            </Typography>
          </Box>
        ) : (
          <MarkdownEditor
            content={state.editor.content}
            onChange={updateContent}
            onSave={() => {
              handleSave();
            }}
          />
        )}
      </Box>
    </Box>
  );
}

export default EditorArea;