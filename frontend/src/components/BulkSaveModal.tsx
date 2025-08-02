import { useState, useEffect } from 'react';
import { useCollections } from '../hooks/useApi';
import type { CrawlResult } from '../types/api';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Box,
  Typography,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  LinearProgress
} from './ui';
import { LoadingButton } from './ui/LoadingButton';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DescriptionIcon from '@mui/icons-material/Description';

interface BulkSaveModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: CrawlResult[];
  selectedIndices: number[];
  onSaveComplete?: (collectionName: string, savedCount: number) => void;
}

export function BulkSaveModal({ 
  isOpen, 
  onClose, 
  results,
  selectedIndices,
  onSaveComplete 
}: BulkSaveModalProps) {
  const [collectionName, setCollectionName] = useState('default');
  const [isNewCollection, setIsNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [saveProgress, setSaveProgress] = useState<{
    current: number;
    total: number;
    status: string;
  }>({ current: 0, total: 0, status: 'idle' });
  
  const {
    collections,
    refreshCollections,
    storeContent,
    storeError,
  } = useCollections();

  useEffect(() => {
    if (isOpen) {
      refreshCollections();
      setSaveProgress({ current: 0, total: 0, status: 'idle' });
    }
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const selectedResults = selectedIndices.map(index => results[index]).filter(result => result && result.success);

  const handleSave = async () => {
    if (selectedResults.length === 0) return;

    const targetCollection = isNewCollection ? newCollectionName.trim() : collectionName;
    
    if (!targetCollection) {
      return;
    }

    setSaveProgress({
      current: 0,
      total: selectedResults.length,
      status: 'saving'
    });

    let savedCount = 0;
    
    try {
      for (let i = 0; i < selectedResults.length; i++) {
        const result = selectedResults[i];
        
        // Create content with metadata
        const contentWithMetadata = `# ${result.title || 'Untitled Page'}

**URL:** ${result.url}  
**Crawled:** ${new Date(result.metadata.crawl_time).toLocaleString()}  
**Depth:** ${result.depth}  
${result.metadata.score > 0 ? `**Score:** ${result.metadata.score.toFixed(1)}  ` : ''}

---

${result.content}`;

        await storeContent(contentWithMetadata, targetCollection);
        savedCount++;
        
        setSaveProgress({
          current: i + 1,
          total: selectedResults.length,
          status: `saving (${i + 1}/${selectedResults.length})`
        });
      }

      setSaveProgress({
        current: savedCount,
        total: selectedResults.length,
        status: 'completed'
      });

      if (onSaveComplete) {
        onSaveComplete(targetCollection, savedCount);
      }
      
      // Reset form
      setTimeout(() => {
        setNewCollectionName('');
        setIsNewCollection(false);
        setCollectionName('default');
        setSaveProgress({ current: 0, total: 0, status: 'idle' });
        onClose();
      }, 1000);

    } catch (error) {
      console.error('Failed to save results:', error);
      setSaveProgress({
        current: savedCount,
        total: selectedResults.length,
        status: 'failed'
      });
    }
  };

  const handleCollectionChange = (value: string) => {
    if (value === '__new__') {
      setIsNewCollection(true);
      setCollectionName('');
    } else {
      setIsNewCollection(false);
      setCollectionName(value);
    }
  };

  const isSaving = saveProgress.status === 'saving';
  const isCompleted = saveProgress.status === 'completed';

  return (
    <Dialog 
      open={isOpen} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { 
          position: 'fixed',
          zIndex: 9999,
          minHeight: '400px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column'
        }
      }}
    >
      <DialogTitle>Bulk Save to Collection</DialogTitle>
      
      <DialogContent sx={{ flex: 1, overflow: 'auto' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
          {/* Selection Summary */}
          <Alert severity="info" icon={<DescriptionIcon />}>
            <Typography variant="body2" fontWeight="medium">
              {selectedResults.length} successful results selected
            </Typography>
            {selectedIndices.length - selectedResults.length > 0 && (
              <Typography variant="body2" color="text.secondary">
                {selectedIndices.length - selectedResults.length} failed results will be skipped
              </Typography>
            )}
          </Alert>

          {/* Collection Selection */}
          {!isSaving && !isCompleted && (
            <Box>
              {!isNewCollection ? (
                <FormControl fullWidth>
                  <InputLabel>Select Collection</InputLabel>
                  <Select
                    value={collectionName}
                    onChange={(e) => handleCollectionChange(e.target.value as string)}
                    label="Select Collection"
                    data-testid="bulk-collection-select"
                  >
                    <MenuItem value="default">Default Collection</MenuItem>
                    {collections.map((collection) => (
                      <MenuItem key={collection.name} value={collection.name}>
                        {collection.name} ({collection.count} items)
                      </MenuItem>
                    ))}
                    <MenuItem value="__new__">+ Create New Collection</MenuItem>
                  </Select>
                </FormControl>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <TextField
                    fullWidth
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                    label="Collection Name"
                    placeholder="Enter collection name"
                    data-testid="bulk-collection-name"
                    autoFocus
                  />
                  <Button
                    variant="text"
                    size="small"
                    onClick={() => setIsNewCollection(false)}
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    ← Back to existing collections
                  </Button>
                </Box>
              )}
            </Box>
          )}

          {/* Progress Display */}
          {isSaving && (
            <Alert severity="info">
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                Saving Results...
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={(saveProgress.current / saveProgress.total) * 100}
                  sx={{ flex: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {saveProgress.current}/{saveProgress.total}
                </Typography>
              </Box>
            </Alert>
          )}

          {/* Completion Display */}
          {isCompleted && (
            <Alert severity="success" icon={<CheckCircleIcon />}>
              <Typography variant="body2" fontWeight="medium">
                Successfully saved {saveProgress.current} results!
              </Typography>
            </Alert>
          )}

          {/* Error Display */}
          {storeError && (
            <Alert severity="error">
              {storeError}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button
          onClick={onClose}
          disabled={isSaving}
        >
          {isCompleted ? 'Close' : 'Cancel'}
        </Button>
        
        {!isSaving && !isCompleted && (
          <LoadingButton
            onClick={handleSave}
            disabled={
              selectedResults.length === 0 ||
              (isNewCollection && !newCollectionName.trim()) ||
              (!isNewCollection && !collectionName)
            }
            variant="contained"
            color="success"
            data-testid="bulk-save-confirm"
          >
            Save {selectedResults.length} Results
          </LoadingButton>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default BulkSaveModal;