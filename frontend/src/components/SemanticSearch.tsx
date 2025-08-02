import { useState } from 'react';
import { useCollections } from '../hooks/useApi';
import type { SearchResult } from '../types/api';
import {
  Paper,
  Box,
  Typography,
  TextField,
  Alert,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment
} from './ui';
import { LoadingButton } from './ui/LoadingButton';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import ScienceIcon from '@mui/icons-material/Science';
import StorageIcon from '@mui/icons-material/Storage';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface SemanticSearchProps {
  selectedCollection?: string;
  onSearchResults?: (results: SearchResult[], query: string) => void;
}

export function SemanticSearch({ 
  selectedCollection = 'default',
  onSearchResults 
}: SemanticSearchProps) {
  const [query, setQuery] = useState('');
  const [resultsLimit, setResultsLimit] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState<number | undefined>(undefined);
  const [lastQuery, setLastQuery] = useState('');

  const {
    searchInCollection,
    searchLoading,
    searchError,
    searchResults,
  } = useCollections();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;

    try {
      const results = await searchInCollection(
        query.trim(),
        selectedCollection,
        resultsLimit,
        similarityThreshold
      );
      
      setLastQuery(query.trim());
      
      if (onSearchResults) {
        onSearchResults(results || [], query.trim());
      }
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    setLastQuery('');
    if (onSearchResults) {
      onSearchResults([], '');
    }
  };

  return (
    <Paper>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" fontWeight="medium">
            Semantic Search
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ScienceIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              Vector Search Powered
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Search Form */}
      <Box component="form" onSubmit={handleSearch} sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Search Input */}
          <TextField
            fullWidth
            label="Search Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query..."
            disabled={searchLoading}
            data-testid="search-input"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: query && (
                <InputAdornment position="end">
                  <IconButton
                    onClick={handleClearSearch}
                    size="small"
                    edge="end"
                  >
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Advanced Options */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Max Results</InputLabel>
              <Select
                value={resultsLimit}
                onChange={(e) => setResultsLimit(parseInt(e.target.value as string))}
                label="Max Results"
                disabled={searchLoading}
              >
                <MenuItem value={3}>3 results</MenuItem>
                <MenuItem value={5}>5 results</MenuItem>
                <MenuItem value={10}>10 results</MenuItem>
                <MenuItem value={20}>20 results</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="number"
              label="Similarity Threshold"
              helperText="Optional (0.0 - 1.0)"
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              value={similarityThreshold || ''}
              onChange={(e) => setSimilarityThreshold(e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="0.7"
              disabled={searchLoading}
            />
          </Box>

          {/* Collection Info */}
          <Alert severity="info" icon={<StorageIcon />}>
            <Typography variant="body2" fontWeight="medium">
              Searching in: {selectedCollection}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uses vector embeddings for semantic similarity matching
            </Typography>
          </Alert>

          {/* Search Button */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Find semantically similar content
            </Typography>
            <LoadingButton
              type="submit"
              variant="contained"
              color="secondary"
              disabled={!query.trim()}
              loading={searchLoading}
              startIcon={<SearchIcon />}
              data-testid="search-button"
            >
              {searchLoading ? 'Searching...' : 'Search'}
            </LoadingButton>
          </Box>
        </Box>

        {/* Error Display */}
        {searchError && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="error">
              <Typography variant="body2" fontWeight="medium">
                Search Failed
              </Typography>
              <Typography variant="body2">
                {searchError}
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Search Results Summary */}
        {lastQuery && searchResults && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="success" icon={<CheckCircleIcon />}>
              <Typography variant="body2" fontWeight="medium">
                Found {searchResults.length} results for "{lastQuery}"
              </Typography>
              {searchResults.length > 0 && (
                <Typography variant="body2" color="text.secondary">
                  Best match score: {Math.max(...searchResults.map(r => r.metadata.score || 0)).toFixed(3)}
                </Typography>
              )}
            </Alert>
          </Box>
        )}
      </Box>
    </Paper>
  );
}

export default SemanticSearch;