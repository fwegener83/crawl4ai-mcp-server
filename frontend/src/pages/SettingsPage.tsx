import React, { useState, useEffect } from 'react';
import { Box, Typography } from '../components/ui';
import { SettingsPanel } from '../components/organisms';
import type { AllSettings } from '../components/organisms';
import { useNotification } from '../components/ui/NotificationProvider';

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
    enableAutoSync: false,
    syncPollingInterval: 10,
    maxSearchResults: 20,
    similarityThreshold: 0.7,
    enableSearchHighlighting: true,
    defaultChunkingStrategy: 'sentence',
  },
};

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AllSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const { showSuccess, showError } = useNotification();

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('crawl4ai-settings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsed });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      showError('Failed to load saved settings');
    }
  }, [showError]);

  const handleSaveSettings = async (newSettings: AllSettings) => {
    setLoading(true);
    try {
      // Save to localStorage
      localStorage.setItem('crawl4ai-settings', JSON.stringify(newSettings));
      setSettings(newSettings);
      
      // In a real application, this would also sync with the backend
      // await api.updateSettings(newSettings);
      
      showSuccess('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      showError('Failed to save settings');
      throw error; // Re-throw to let the form handle it
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      gap: 3,
    }}>
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your Crawl4AI application preferences and crawling behavior.
        </Typography>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <SettingsPanel
          settings={settings}
          onSave={handleSaveSettings}
          loading={loading}
        />
      </Box>
    </Box>
  );
};

export default SettingsPage;