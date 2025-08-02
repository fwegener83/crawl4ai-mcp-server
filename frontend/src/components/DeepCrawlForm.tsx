import { useState } from 'react';
import { useCrawling } from '../hooks/useApi';
import { APIService } from '../services/api';
import type { DeepCrawlConfig, CrawlResult } from '../types/api';
import { 
  Paper, 
  Box, 
  Typography, 
  TextField, 
  Select, 
  Checkbox, 
  Avatar,
  Alert,
  LinearProgress
} from './ui';
import { MenuItem, FormControl, InputLabel, FormControlLabel } from '@mui/material';
import { LoadingButton } from './ui/LoadingButton';
import StorageIcon from '@mui/icons-material/Storage';
import { CircularProgress } from './ui';

interface DeepCrawlFormProps {
  onCrawlComplete?: (results: CrawlResult[]) => void;
}

export function DeepCrawlForm({ onCrawlComplete }: DeepCrawlFormProps) {
  const [config, setConfig] = useState<DeepCrawlConfig>({
    domain_url: '',
    max_depth: 2,
    crawl_strategy: 'bfs',
    max_pages: 10,
    include_external: false,
    url_patterns: [],
    exclude_patterns: [],
    keywords: [],
    stream_results: false,
  });

  const [urlPatternsText, setUrlPatternsText] = useState('');
  const [excludePatternsText, setExcludePatternsText] = useState('');
  const [keywordsText, setKeywordsText] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);

  const { startCrawl, loading, error, progress } = useCrawling();

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return url === '';
    }
  };

  const handleUrlChange = (url: string) => {
    setConfig(prev => ({ ...prev, domain_url: url }));
    setIsValidUrl(validateUrl(url));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!config.domain_url.trim() || !isValidUrl) {
      setIsValidUrl(false);
      return;
    }

    // Parse text inputs into arrays
    const finalConfig: DeepCrawlConfig = {
      ...config,
      url_patterns: urlPatternsText.trim() 
        ? urlPatternsText.split('\n').map(p => p.trim()).filter(p => p)
        : undefined,
      exclude_patterns: excludePatternsText.trim()
        ? excludePatternsText.split('\n').map(p => p.trim()).filter(p => p)
        : undefined,
      keywords: keywordsText.trim()
        ? keywordsText.split(',').map(k => k.trim()).filter(k => k)
        : undefined,
    };

    try {
      const results = await startCrawl(() => 
        APIService.deepCrawlDomain(finalConfig)
      );
      
      if (onCrawlComplete) {
        onCrawlComplete(results);
      }
    } catch (error) {
      console.error('Deep crawl failed:', error);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Avatar 
          sx={{ 
            bgcolor: 'success.light',
            color: 'success.contrastText',
            mr: 2 
          }}
        >
          <StorageIcon />
        </Avatar>
        <Typography variant="h6" component="h3">
          Deep Website Crawling
        </Typography>
      </Box>

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Domain URL */}
        <TextField
          id="domain_url"
          inputProps={{ 'data-testid': 'domain-url-input' }}
          label="Domain URL"
          type="url"
          value={config.domain_url}
          onChange={(e) => handleUrlChange(e.target.value)}
          placeholder="https://example.com"
          fullWidth
          required
          error={!isValidUrl}
          helperText={!isValidUrl ? 'Please enter a valid domain URL' : ''}
          disabled={loading}
        />

        {/* Strategy and Depth */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel id="crawl_strategy-label">Crawl Strategy</InputLabel>
            <Select
              labelId="crawl_strategy-label"
              id="crawl_strategy"
              value={config.crawl_strategy}
              label="Crawl Strategy"
              onChange={(e) => setConfig(prev => ({ 
                ...prev, 
                crawl_strategy: e.target.value as 'bfs' | 'dfs' | 'best_first' 
              }))}
              disabled={loading}
            >
              <MenuItem value="bfs">Breadth-First (BFS)</MenuItem>
              <MenuItem value="dfs">Depth-First (DFS)</MenuItem>
              <MenuItem value="best_first">Best-First (Keyword-based)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            id="max_depth"
            label="Max Depth"
            type="number"
            inputProps={{ min: 1, max: 10 }}
            value={config.max_depth}
            onChange={(e) => setConfig(prev => ({ ...prev, max_depth: parseInt(e.target.value) || 1 }))}
            disabled={loading}
          />

          <TextField
            id="max_pages"
            label="Max Pages"
            type="number"
            inputProps={{ min: 1, max: 1000 }}
            value={config.max_pages}
            onChange={(e) => setConfig(prev => ({ ...prev, max_pages: parseInt(e.target.value) || 1 }))}
            disabled={loading}
          />
        </Box>

        {/* Include External Links */}
        <FormControlLabel
          control={
            <Checkbox
              id="include_external"
              checked={config.include_external}
              onChange={(e) => setConfig(prev => ({ ...prev, include_external: e.target.checked }))}
              disabled={loading}
              color="success"
            />
          }
          label="Include external links (links outside the domain)"
        />

        {/* URL Patterns */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
          <TextField
            id="url_patterns"
            label="Include URL Patterns"
            multiline
            rows={3}
            value={urlPatternsText}
            onChange={(e) => setUrlPatternsText(e.target.value)}
            placeholder="*/blog/*\n*/news/*\n*/articles/*"
            helperText="One per line, glob patterns"
            disabled={loading}
          />

          <TextField
            id="exclude_patterns"
            label="Exclude URL Patterns"
            multiline
            rows={3}
            value={excludePatternsText}
            onChange={(e) => setExcludePatternsText(e.target.value)}
            placeholder="*/admin/*\n*/login/*\n*.pdf"
            helperText="One per line, glob patterns"
            disabled={loading}
          />
        </Box>

        {/* Keywords for Best-First Strategy */}
        {config.crawl_strategy === 'best_first' && (
          <TextField
            id="keywords"
            label="Keywords for Scoring"
            value={keywordsText}
            onChange={(e) => setKeywordsText(e.target.value)}
            placeholder="react, javascript, tutorial, guide"
            helperText="Comma-separated. Pages containing these keywords will be prioritized"
            disabled={loading}
            fullWidth
          />
        )}

        {/* Progress Display */}
        {loading && (
          <Alert 
            severity="info" 
            icon={<CircularProgress size={20} />}
            sx={{ alignItems: 'center' }}
          >
            <Box>
              <Typography variant="body2" fontWeight="medium">
                Deep Crawling in Progress
              </Typography>
              <Typography variant="body2">
                Status: {progress.status} ({progress.current}/{progress.total})
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(progress.current / progress.total) * 100} 
                sx={{ mt: 1 }}
              />
            </Box>
          </Alert>
        )}

        {/* Submit Button */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Crawl multiple pages with advanced filtering and strategies
          </Typography>
          <LoadingButton
            type="submit"
            data-testid="deep-crawl-button"
            loading={loading}
            disabled={!config.domain_url.trim() || !isValidUrl}
            variant="contained"
            color="success"
            loadingPosition="start"
          >
            {loading ? 'Crawling...' : 'Start Deep Crawl'}
          </LoadingButton>
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            Deep Crawling Failed
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      )}
    </Paper>
  );
}

export default DeepCrawlForm;