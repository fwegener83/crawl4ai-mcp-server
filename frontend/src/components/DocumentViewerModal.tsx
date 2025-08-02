import { useState, useEffect } from 'react';
import MarkdownEditor from './MarkdownEditor';
import SaveToCollectionModal from './SaveToCollectionModal';
import { useNotification } from './ui/NotificationProvider';
import type { CrawlResult } from '../types/api';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Button,
  Chip
} from './ui';
import CloseIcon from '@mui/icons-material/Close';
import SaveIcon from '@mui/icons-material/Save';

interface DocumentViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: CrawlResult | null;
}

export function DocumentViewerModal({ 
  isOpen, 
  onClose, 
  result 
}: DocumentViewerModalProps) {
  const [editedContent, setEditedContent] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const { showSuccess } = useNotification();

  useEffect(() => {
    if (result && isOpen) {
      // Create formatted content with metadata
      const formattedContent = `# ${result.title || 'Untitled Page'}

**URL:** ${result.url}  
**Crawled:** ${new Date(result.metadata.crawl_time).toLocaleString()}  
**Depth:** ${result.depth}  
${result.metadata.score > 0 ? `**Score:** ${result.metadata.score.toFixed(1)}  ` : ''}

---

${result.content}`;
      
      setEditedContent(formattedContent);
      setHasUnsavedChanges(false);
    }
  }, [result, isOpen]);

  const handleContentChange = (content: string) => {
    setEditedContent(content);
    setHasUnsavedChanges(content !== (result?.content || ''));
  };

  const handleSaveClick = () => {
    if (editedContent.trim()) {
      setShowSaveModal(true);
    }
  };

  const handleSaveComplete = (collectionName: string) => {
    setHasUnsavedChanges(false);
    showSuccess(`Successfully saved to collection: ${collectionName}`);
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  if (!result) return null;

  return (
    <>
      <Dialog 
        open={isOpen} 
        onClose={handleClose} 
        maxWidth="lg" 
        fullWidth
        PaperProps={{
          sx: { height: '90vh', display: 'flex', flexDirection: 'column' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h6" noWrap>
                Document Viewer & Editor
              </Typography>
              {hasUnsavedChanges && (
                <Chip 
                  label="Unsaved changes" 
                  size="small" 
                  color="warning" 
                  variant="outlined"
                />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" noWrap>
              {result.title || 'Untitled Page'}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
            <Button
              onClick={handleSaveClick}
              disabled={!editedContent.trim()}
              variant="contained"
              color="success"
              size="small"
              startIcon={<SaveIcon />}
              data-testid="document-save-button"
            >
              Save to Collection
            </Button>
            
            <IconButton
              onClick={handleClose}
              size="small"
              title="Close"
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>

        {/* Document Info */}
        <Box sx={{ 
          px: 3, 
          py: 1.5, 
          bgcolor: 'action.selected', 
          borderBottom: 1, 
          borderColor: 'divider' 
        }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 3, 
            flexWrap: 'wrap' 
          }}>
            <Typography variant="caption" color="text.secondary">
              <Box component="span" fontWeight="medium">URL:</Box> {result.url}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              <Box component="span" fontWeight="medium">Depth:</Box> {result.depth}
            </Typography>
            {result.metadata.score > 0 && (
              <Typography variant="caption" color="text.secondary">
                <Box component="span" fontWeight="medium">Score:</Box> {result.metadata.score.toFixed(1)}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary">
              <Box component="span" fontWeight="medium">Size:</Box> {result.content.length.toLocaleString()} chars
            </Typography>
            <Typography variant="caption" color="text.secondary">
              <Box component="span" fontWeight="medium">Crawled:</Box> {new Date(result.metadata.crawl_time).toLocaleString()}
            </Typography>
          </Box>
        </Box>

        <DialogContent sx={{ flex: 1, overflow: 'hidden', p: 0 }}>
          <MarkdownEditor
            content={editedContent}
            onChange={handleContentChange}
            onSave={handleSaveClick}
          />
        </DialogContent>
      </Dialog>
      
      {/* Save Modal */}
      <SaveToCollectionModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        content={editedContent}
        onSaveComplete={handleSaveComplete}
      />
    </>
  );
}

export default DocumentViewerModal;