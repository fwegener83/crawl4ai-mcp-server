import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Typography
} from '../ui';
import CloseIcon from '@mui/icons-material/Close';
import { SettingsPanel } from '../organisms';
import type { AllSettings } from '../organisms';

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

const defaultSettings: AllSettings = {
  crawl: {
    userAgent: 'Crawl4AI-MCP-Server/1.0',
    timeout: 30,
    maxRetries: 3,
    delay: 1000,
    respectRobots: true,
    followRedirects: true,
    maxDepth: 3,
    maxPages: 100,
    concurrent: 5,
  },
  storage: {
    defaultCollection: 'default',
    autoSave: true,
    compressionEnabled: false,
    maxFileSize: 10,
    allowedFormats: ['.md', '.txt', '.json'],
  },
  ui: {
    theme: 'system',
    language: 'en',
    pageSize: 25,
    showPreview: true,
    enableAnimations: true,
  },
  vectorSync: {
    enableAutoSync: false, // Manual sync only by default
    syncPollingInterval: 10, // 10-second polling
    maxSearchResults: 20,
    similarityThreshold: 0.7,
    enableSearchHighlighting: false, // Simplified UI approach
    defaultChunkingStrategy: 'paragraph',
  },
};

export const SettingsModal: React.FC<SettingsModalProps> = ({ open, onClose }) => {
  const [settings, setSettings] = useState<AllSettings>(defaultSettings);
  const [hasChanges, setHasChanges] = useState(false);

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('crawl4ai-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsed });
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const handleSave = async (newSettings: AllSettings) => {
    setSettings(newSettings);
    setHasChanges(true);
    
    // Auto-save settings to localStorage
    try {
      localStorage.setItem('crawl4ai-settings', JSON.stringify(newSettings));
      setHasChanges(false);
      return Promise.resolve();
    } catch (error) {
      console.error('Failed to save settings:', error);
      return Promise.reject(error);
    }
  };

  const handleClose = () => {
    // You could add unsaved changes warning here if needed
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '70vh',
          maxHeight: '90vh',
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Box>
          <Typography variant="h5" component="div" fontWeight="bold">
            Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure Crawl4AI application preferences
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          size="small"
          sx={{ 
            color: 'text.secondary',
            '&:hover': { bgcolor: 'action.hover' }
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        <SettingsPanel
          settings={settings}
          onSave={handleSave}
        />
        
        {hasChanges && (
          <Box sx={{ 
            mt: 2, 
            p: 1.5, 
            bgcolor: 'success.50', 
            border: 1, 
            borderColor: 'success.200',
            borderRadius: 1
          }}>
            <Typography variant="body2" color="success.main">
              ✓ Settings saved automatically
            </Typography>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default SettingsModal;