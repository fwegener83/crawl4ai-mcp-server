import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useCollection } from '../../../contexts/CollectionContext';
import { useVectorSync } from '../../../hooks/useVectorSync';
import { EnhancedSettingsPanel } from '../EnhancedSettingsPanel';

export interface EnhancedSettingsModalProps {
  collectionId?: string;
}

export function EnhancedSettingsModal({ collectionId }: EnhancedSettingsModalProps) {
  const { state, dispatch } = useCollection();
  const { getSyncStatus } = useVectorSync();
  
  const handleClose = () => {
    dispatch({ type: 'CLOSE_MODAL', payload: 'enhancedSettings' });
  };

  const handleSettingsChange = (settings: any) => {
    // Settings are automatically persisted by the EnhancedSettingsPanel
    console.log('Enhanced settings updated:', settings);
  };

  const handleApplySettings = (settings: any) => {
    // Apply settings to the collection
    console.log('Apply enhanced settings:', settings);
  };

  const handleResetToDefaults = () => {
    // Reset settings to defaults
    console.log('Reset enhanced settings to defaults');
  };

  const selectedCollectionId = collectionId || state.selectedCollection;
  const syncStatus = selectedCollectionId ? getSyncStatus(selectedCollectionId) : undefined;

  return (
    <Dialog
      open={state.ui.modals.enhancedSettings}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      data-testid="enhanced-settings-modal"
    >
      <DialogTitle
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          pb: 2
        }}
      >
        Enhanced RAG Settings
        <IconButton
          onClick={handleClose}
          size="small"
          aria-label="close"
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0 }}>
        {selectedCollectionId && syncStatus && (
          <EnhancedSettingsPanel
            collectionName={selectedCollectionId}
            syncStatus={syncStatus}
            open={state.ui.modals.enhancedSettings}
            onClose={handleClose}
            onSettingsChange={handleSettingsChange}
            onApplySettings={handleApplySettings}
            onResetToDefaults={handleResetToDefaults}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}

export default EnhancedSettingsModal;