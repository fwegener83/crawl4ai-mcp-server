import React from 'react';
import { useForm } from 'react-hook-form';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '../ui';
import {
  FormContainer,
  TextFieldElement,
  SelectElement,
  CheckboxElement,
  SwitchElement,
  SubmitButton
} from '../forms';
import { useNotification } from '../ui/NotificationProvider';
import SettingsIcon from '@mui/icons-material/Settings';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

export interface CrawlSettings {
  userAgent: string;
  timeout: number;
  maxRetries: number;
  delay: number;
  respectRobots: boolean;
  followRedirects: boolean;
  maxDepth: number;
  maxPages: number;
  concurrent: number;
}

export interface StorageSettings {
  defaultCollection: string;
  autoSave: boolean;
  compressionEnabled: boolean;
  maxFileSize: number;
  allowedFormats: string[];
}

export interface UISettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  pageSize: number;
  showPreview: boolean;
  enableAnimations: boolean;
}

export interface VectorSyncSettings {
  enableAutoSync: boolean;
  syncPollingInterval: number; // in seconds
  maxSearchResults: number;
  similarityThreshold: number; // 0.0 - 1.0
  enableSearchHighlighting: boolean;
  defaultChunkingStrategy: 'fixed' | 'sentence' | 'paragraph';
}

export interface AllSettings {
  crawl: CrawlSettings;
  storage: StorageSettings;
  ui: UISettings;
  vectorSync: VectorSyncSettings;
}

export interface SettingsPanelProps {
  settings: AllSettings;
  onSave: (settings: AllSettings) => void;
  loading?: boolean;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  settings,
  onSave,
  loading = false,
}) => {
  const { showSuccess, showError } = useNotification();
  
  const form = useForm<AllSettings>({
    defaultValues: settings
  });

  const handleSubmit = async (data: AllSettings) => {
    try {
      await onSave(data);
      showSuccess('Settings saved successfully!');
    } catch (error) {
      showError('Failed to save settings');
    }
  };

  const handleReset = () => {
    form.reset(settings);
    showSuccess('Settings reset to defaults');
  };

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto' }}>
      <CardHeader
        avatar={<SettingsIcon color="primary" />}
        title="Application Settings"
        subheader="Configure crawling, storage, and interface preferences"
      />
      
      <CardContent>
        <FormContainer formContext={form as any} onSuccess={handleSubmit as any}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            
            {/* Crawling Settings */}
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Crawling Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextFieldElement
                    name="crawl.userAgent"
                    label="User Agent"
                    helperText="Custom user agent string for requests"
                    fullWidth
                  />
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextFieldElement
                      name="crawl.timeout"
                      label="Timeout (seconds)"
                      type="number"
                      rules={{ min: 1, max: 300 }}
                      sx={{ flex: 1 }}
                    />
                    <TextFieldElement
                      name="crawl.maxRetries"
                      label="Max Retries"
                      type="number"
                      rules={{ min: 0, max: 10 }}
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextFieldElement
                      name="crawl.delay"
                      label="Delay (ms)"
                      type="number"
                      rules={{ min: 0, max: 10000 }}
                      helperText="Delay between requests"
                      sx={{ flex: 1 }}
                    />
                    <TextFieldElement
                      name="crawl.concurrent"
                      label="Concurrent Requests"
                      type="number"
                      rules={{ min: 1, max: 20 }}
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextFieldElement
                      name="crawl.maxDepth"
                      label="Max Depth"
                      type="number"
                      rules={{ min: 1, max: 10 }}
                      helperText="Maximum crawling depth"
                      sx={{ flex: 1 }}
                    />
                    <TextFieldElement
                      name="crawl.maxPages"
                      label="Max Pages"
                      type="number"
                      rules={{ min: 1, max: 10000 }}
                      helperText="Maximum pages to crawl"
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 4 }}>
                    <CheckboxElement
                      name="crawl.respectRobots"
                      label="Respect robots.txt"
                    />
                    <CheckboxElement
                      name="crawl.followRedirects"
                      label="Follow redirects"
                    />
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* Storage Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Storage Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextFieldElement
                    name="storage.defaultCollection"
                    label="Default Collection"
                    helperText="Collection to save content by default"
                    fullWidth
                  />
                  
                  <TextFieldElement
                    name="storage.maxFileSize"
                    label="Max File Size (MB)"
                    type="number"
                    rules={{ min: 1, max: 100 }}
                    helperText="Maximum file size for uploads"
                  />
                  
                  <TextFieldElement
                    name="storage.allowedFormats"
                    label="Allowed File Formats"
                    helperText="Comma-separated list (e.g., .md,.txt,.json)"
                    fullWidth
                  />
                  
                  <Box sx={{ display: 'flex', gap: 4 }}>
                    <SwitchElement
                      name="storage.autoSave"
                      label="Auto-save crawled content"
                    />
                    <SwitchElement
                      name="storage.compressionEnabled"
                      label="Enable compression"
                    />
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* UI Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Interface Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <SelectElement
                      name="ui.theme"
                      label="Theme"
                      options={[
                        { id: 'light', label: 'Light' },
                        { id: 'dark', label: 'Dark' },
                        { id: 'system', label: 'System' }
                      ]}
                      sx={{ flex: 1 }}
                    />
                    <SelectElement
                      name="ui.language"
                      label="Language"
                      options={[
                        { id: 'en', label: 'English' },
                        { id: 'de', label: 'Deutsch' },
                        { id: 'fr', label: 'Français' }
                      ]}
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <TextFieldElement
                    name="ui.pageSize"
                    label="Items per Page"
                    type="number"
                    rules={{ min: 10, max: 100 }}
                    helperText="Default number of items to display per page"
                  />
                  
                  <Box sx={{ display: 'flex', gap: 4 }}>
                    <SwitchElement
                      name="ui.showPreview"
                      label="Show content preview"
                    />
                    <SwitchElement
                      name="ui.enableAnimations"
                      label="Enable animations"
                    />
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* Vector Sync Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Vector Sync Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Configure vector synchronization and semantic search preferences
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextFieldElement
                      name="vectorSync.syncPollingInterval"
                      label="Sync Polling Interval (seconds)"
                      type="number"
                      rules={{ min: 5, max: 60 }}
                      helperText="How often to check sync progress"
                      sx={{ flex: 1 }}
                    />
                    <TextFieldElement
                      name="vectorSync.maxSearchResults"
                      label="Max Search Results"
                      type="number"
                      rules={{ min: 10, max: 100 }}
                      helperText="Maximum results per search"
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextFieldElement
                      name="vectorSync.similarityThreshold"
                      label="Similarity Threshold"
                      type="number"
                      rules={{ min: 0.1, max: 1.0 }}
                      inputProps={{ step: 0.1 }}
                      helperText="Minimum similarity for search results (0.1-1.0)"
                      sx={{ flex: 1 }}
                    />
                    <SelectElement
                      name="vectorSync.defaultChunkingStrategy"
                      label="Default Chunking Strategy"
                      options={[
                        { id: 'paragraph', label: 'Paragraph' },
                        { id: 'sentence', label: 'Sentence' },
                        { id: 'fixed', label: 'Fixed Size' }
                      ]}
                      helperText="How to split content into chunks"
                      sx={{ flex: 1 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 4 }}>
                    <SwitchElement
                      name="vectorSync.enableAutoSync"
                      label="Enable automatic synchronization"
                      disabled
                    />
                    <SwitchElement
                      name="vectorSync.enableSearchHighlighting"
                      label="Enable search highlighting"
                      disabled
                    />
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary">
                    Note: Auto-sync and search highlighting are currently disabled to maintain simple UI
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>

            <Divider />
            
            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <SubmitButton
                variant="outlined"
                onClick={handleReset}
                disabled={loading}
              >
                Reset to Defaults
              </SubmitButton>
              <SubmitButton
                loading={loading}
                submitText="Save Settings"
                loadingText="Saving..."
              />
            </Box>
          </Box>
        </FormContainer>
      </CardContent>
    </Card>
  );
};

export default SettingsPanel;