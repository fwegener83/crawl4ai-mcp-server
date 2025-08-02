import { useState } from 'react';
import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import { useNotification } from '../../ui/NotificationProvider';
import DeepCrawlForm from '../../DeepCrawlForm';
import CrawlResultsSelectionList from '../../CrawlResultsSelectionList';
import type { CrawlResult } from '../../../types/api';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '../../ui';
import { LoadingButton } from '../../ui/LoadingButton';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import SaveIcon from '@mui/icons-material/Save';
import FolderIcon from '@mui/icons-material/Folder';

export function AddMultiplePagesModal() {
  const { state, addMultiplePagesToCollection, closeModal } = useCollectionOperations();
  const { showSuccess, showError } = useNotification();
  
  const [crawlResults, setCrawlResults] = useState<CrawlResult[]>([]);
  const [selectedResults, setSelectedResults] = useState<CrawlResult[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [folder, setFolder] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [crawlCompleted, setCrawlCompleted] = useState(false);

  if (!state.ui.modals.addMultiplePages) {
    return null;
  }

  const handleCrawlComplete = (results: CrawlResult[]) => {
    setCrawlResults(results);
    setSelectedResults([]);
    setSelectedIndices([]);
    setCrawlCompleted(true);
  };

  const handleSelectMultiple = (results: CrawlResult[], indices: number[]) => {
    setSelectedResults(results);
    setSelectedIndices(indices);
  };

  const handleSave = async () => {
    if (selectedResults.length === 0 || !state.selectedCollection) return;

    setIsSaving(true);
    try {
      const result = await addMultiplePagesToCollection(
        state.selectedCollection,
        selectedResults,
        folder.trim() || undefined
      );
      
      showSuccess(`Successfully added ${result.savedCount} pages to collection: ${state.selectedCollection}`);
      
      // Reset state and close modal
      setCrawlResults([]);
      setSelectedResults([]);
      setSelectedIndices([]);
      setFolder('');
      setCrawlCompleted(false);
      closeModal('addMultiplePages');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to add pages to collection';
      showError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    if (!isSaving) {
      // Reset all state when closing
      setCrawlResults([]);
      setSelectedResults([]);
      setSelectedIndices([]);
      setFolder('');
      setCrawlCompleted(false);
      closeModal('addMultiplePages');
    }
  };

  const successfulResults = selectedResults.filter(r => r.success);

  return (
    <Dialog
      open={state.ui.modals.addMultiplePages}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { 
          height: { xs: '95vh', sm: '90vh' },
          minHeight: { xs: '500px', sm: '600px' },
          display: 'flex', 
          flexDirection: 'column',
          maxHeight: '95vh',
          m: { xs: 1, sm: 2 }
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        flexShrink: 0,
        borderBottom: 1, 
        borderColor: 'divider'
      }}>
        <TravelExploreIcon color="primary" fontSize="large" />
        <Box>
          <Typography variant="h6">
            Add Multiple Pages from Deep Crawl
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure deep crawl, select pages, and add them to: <strong>{state.selectedCollection}</strong>
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 0,
        display: 'flex',
        flexDirection: 'column'
      }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          minHeight: 'fit-content'
        }}>
          {/* Deep Crawl Form Section */}
          <Box sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            bgcolor: 'background.paper',
            flexShrink: 0
          }}>
            <Box sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  fontSize: { xs: '1rem', sm: '1.25rem' }
                }}
              >
                <TravelExploreIcon color="primary" />
                Deep Crawl Configuration
              </Typography>
              <DeepCrawlForm onCrawlComplete={handleCrawlComplete} />
            </Box>
          </Box>

          {/* Results Section */}
          {crawlCompleted && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              minHeight: 0,
              flex: 1
            }}>
              <Box sx={{ 
                p: { xs: 2, sm: 3 }, 
                borderBottom: 1, 
                borderColor: 'divider', 
                bgcolor: 'background.paper',
                flexShrink: 0
              }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between', 
                  mb: 2,
                  flexWrap: 'wrap',
                  gap: 1
                }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 1,
                      fontSize: { xs: '1rem', sm: '1.25rem' }
                    }}
                  >
                    <SaveIcon color="success" />
                    Select Pages to Add
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedResults.length} of {crawlResults.length} pages selected
                  </Typography>
                </Box>

                {/* Folder Input */}
                <TextField
                  label="Folder (optional)"
                  value={folder}
                  onChange={(e) => setFolder(e.target.value)}
                  placeholder="e.g., deep-crawl/domain-name"
                  disabled={isSaving}
                  fullWidth
                  size="small"
                  InputProps={{
                    startAdornment: <FolderIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  }}
                  helperText="Leave empty to save in root directory. Use / to separate nested folders."
                />
              </Box>

              {/* Results List */}
              <Box sx={{ 
                flex: 1, 
                overflow: 'auto', 
                p: { xs: 2, sm: 3 },
                minHeight: { xs: '200px', sm: '300px' }
              }}>
                <CrawlResultsSelectionList
                  results={crawlResults}
                  onSelectMultiple={handleSelectMultiple}
                  selectedIndices={selectedIndices}
                />
              </Box>
            </Box>
          )}

          {/* No Results State */}
          {!crawlCompleted && (
            <Box sx={{ 
              flex: 1, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              p: { xs: 3, sm: 4 },
              bgcolor: 'background.default',
              minHeight: { xs: '200px', sm: '300px' }
            }}>
              <Box sx={{ textAlign: 'center' }}>
                <TravelExploreIcon sx={{ 
                  fontSize: { xs: 48, sm: 64 }, 
                  color: 'text.secondary', 
                  mb: 2 
                }} />
                <Typography variant="h6" gutterBottom sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
                  Ready to Start Deep Crawl
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Configure your deep crawl settings above and start crawling to see results here.
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ 
        px: { xs: 2, sm: 3 }, 
        py: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        flexShrink: 0,
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 1 },
        alignItems: { xs: 'stretch', sm: 'center' }
      }}>
        {crawlCompleted && selectedResults.length > 0 && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2, 
            mr: { xs: 0, sm: 'auto' },
            order: { xs: 2, sm: 1 }
          }}>
            <Alert severity="info" sx={{ py: 0, flexGrow: 1 }}>
              <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                {successfulResults.length} successful pages will be added
                {selectedResults.length - successfulResults.length > 0 && 
                  ` (${selectedResults.length - successfulResults.length} failed pages will be skipped)`
                }
              </Typography>
            </Alert>
          </Box>
        )}
        
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          justifyContent: { xs: 'stretch', sm: 'flex-end' },
          order: { xs: 1, sm: 2 },
          width: { xs: '100%', sm: 'auto' }
        }}>
          <Button
            onClick={handleClose}
            disabled={isSaving}
            variant="outlined"
            sx={{ flex: { xs: 1, sm: 'none' } }}
          >
            Cancel
          </Button>
          
          {crawlCompleted && (
            <LoadingButton
              onClick={handleSave}
              loading={isSaving}
              disabled={selectedResults.length === 0 || !state.selectedCollection}
              variant="contained"
              color="success"
              startIcon={isSaving ? <CircularProgress size={16} /> : <SaveIcon />}
              sx={{ 
                flex: { xs: 1, sm: 'none' },
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                whiteSpace: 'nowrap'
              }}
            >
              {isSaving 
                ? `Adding ${successfulResults.length} Pages...` 
                : `Add ${successfulResults.length} Pages`
              }
            </LoadingButton>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
}

export default AddMultiplePagesModal;