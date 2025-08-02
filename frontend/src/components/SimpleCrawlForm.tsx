import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { APIService } from '../services/api';
import { useNotification } from './ui/NotificationProvider';
import { parseAPIError } from '../utils/errorHandling';
import { Paper, Box, Typography, TextField, Avatar } from './ui';
import { LoadingButton } from './ui/LoadingButton';
import LanguageIcon from '@mui/icons-material/Language';

interface SimpleCrawlFormProps {
  onCrawlComplete?: (content: string) => void;
}

export function SimpleCrawlForm({ onCrawlComplete }: SimpleCrawlFormProps) {
  const [url, setUrl] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);
  const crawlApi = useApi<string>();
  const { showError } = useNotification();

  const validateUrl = (inputUrl: string): boolean => {
    try {
      new URL(inputUrl);
      return true;
    } catch {
      return inputUrl === ''; // Empty is valid (not submitted yet)
    }
  };

  const handleUrlChange = (value: string) => {
    setUrl(value);
    setIsValidUrl(validateUrl(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim() || !isValidUrl) {
      setIsValidUrl(false);
      return;
    }

    try {
      const content = await crawlApi.execute(() => 
        APIService.extractWebContent(url.trim())
      );
      
      if (onCrawlComplete) {
        onCrawlComplete(content);
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      const parsedError = parseAPIError(error);
      showError(parsedError.message);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Avatar 
          sx={{ 
            bgcolor: 'primary.light',
            color: 'primary.contrastText',
            mr: 2 
          }}
        >
          <LanguageIcon />
        </Avatar>
        <Typography variant="h6" component="h3">
          Simple Website Crawling
        </Typography>
      </Box>

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <TextField
          id="url"
          inputProps={{ 'data-testid': 'url-input' }}
          label="Website URL"
          type="url"
          value={url}
          onChange={(e) => handleUrlChange(e.target.value)}
          placeholder="https://example.com"
          fullWidth
          error={!isValidUrl}
          helperText={!isValidUrl ? 'Please enter a valid URL (e.g., https://example.com)' : ''}
          disabled={crawlApi.loading}
        />

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="body2" color="text.secondary">
            Extract clean content from any webpage
          </Typography>
          <LoadingButton
            type="submit"
            data-testid="crawl-button"
            loading={crawlApi.loading}
            disabled={!url.trim() || !isValidUrl}
            variant="contained"
            loadingPosition="start"
          >
            {crawlApi.loading ? 'Crawling...' : 'Start Crawl'}
          </LoadingButton>
        </Box>
      </Box>
    </Paper>
  );
}

export default SimpleCrawlForm;