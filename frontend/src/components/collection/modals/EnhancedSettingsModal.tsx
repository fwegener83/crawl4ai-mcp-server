import React from 'react';
import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useCollection } from '../../../contexts/CollectionContext';
import { EnhancedSettingsPanel } from '../EnhancedSettingsPanel';

export interface EnhancedSettingsModalProps {
  collectionId?: string;
}

export function EnhancedSettingsModal({ collectionId }: EnhancedSettingsModalProps) {
  const { state, dispatch } = useCollection();
  
  const handleClose = () => {
    dispatch({ type: 'CLOSE_MODAL', payload: 'enhancedSettings' });
  };

  const handleSettingsChange = (settings: any) => {
    // Settings are automatically persisted by the EnhancedSettingsPanel
    console.log('Enhanced settings updated:', settings);
  };

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
        <EnhancedSettingsPanel
          collectionId={collectionId || state.selectedCollection || ''}
          onSettingsChange={handleSettingsChange}
          showAdvancedSettings={true}
        />
      </DialogContent>
    </Dialog>
  );
}

export default EnhancedSettingsModal;