import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Chip,
  InputAdornment,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import { useDebounce } from '../../hooks/useDebounce';
import type { VectorSearchResult, VectorSyncStatus } from '../../types/api';

interface VectorSearchPanelProps {
  collectionId?: string;
  collectionSyncStatus?: VectorSyncStatus;
  searchResults: VectorSearchResult[];
  searchQuery: string;
  searchLoading: boolean;
  onSearch: (query: string, collectionId?: string) => Promise<void>;
  onResultClick: (result: VectorSearchResult) => void;
  onClearSearch: () => void;
  maxHeight?: number;
  showCollectionFilter?: boolean;
}

export const VectorSearchPanel: React.FC<VectorSearchPanelProps> = ({
  collectionId,
  collectionSyncStatus,
  searchResults,
  searchQuery,
  searchLoading,
  onSearch,
  onResultClick,
  onClearSearch,
  maxHeight = 400 // TODO: implement dynamic height
}) => {
  const [localQuery, setLocalQuery] = useState(searchQuery);
  const debouncedQuery = useDebounce(localQuery, 300);

  // Perform search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim()) {
      onSearch(debouncedQuery, collectionId);
    } else if (searchQuery) {
      onClearSearch();
    }
  }, [debouncedQuery, collectionId, onSearch, onClearSearch, searchQuery]);

  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(event.target.value);
  };

  const handleClearQuery = () => {
    setLocalQuery('');
    onClearSearch();
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'default';
  };

  const formatContent = (content: string, maxLength: number = 120) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  const canUserSearch = () => {
    if (!collectionSyncStatus) return false;
    return collectionSyncStatus.status === 'in_sync' || 
           collectionSyncStatus.status === 'partial_sync';
  };

  const getSearchDisabledReason = () => {
    if (!collectionSyncStatus) return 'No sync status available';
    
    switch (collectionSyncStatus.status) {
      case 'never_synced':
        return 'Collection has never been synced to vector store';
      case 'out_of_sync':
        return collectionSyncStatus.changed_files_count > 0 
          ? `${collectionSyncStatus.changed_files_count} files have changed since last sync`
          : 'Some files have changed since last sync';
      case 'syncing':
        return 'Collection is currently syncing';
      case 'sync_error':
        return 'Last sync failed with errors';
      default:
        return 'Vector search not available';
    }
  };

  return (
    <Paper elevation={1} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Search Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <TextField
          fullWidth
          placeholder={canUserSearch() ? "Search collection content..." : getSearchDisabledReason()}
          value={localQuery}
          onChange={handleQueryChange}
          disabled={!canUserSearch() || searchLoading}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                {searchLoading ? (
                  <CircularProgress size={20} />
                ) : (
                  <SearchIcon />
                )}
              </InputAdornment>
            ),
            endAdornment: localQuery && (
              <InputAdornment position="end">
                <IconButton onClick={handleClearQuery} size="small">
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
          size="small"
        />

        {/* Collection Info */}
        {collectionId && collectionSyncStatus && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="textSecondary">
              {collectionId} • {collectionSyncStatus.chunk_count} chunks
            </Typography>
            {!canUserSearch() && (
              <Chip size="small" label="Sync required" color="warning" variant="outlined" />
            )}
          </Box>
        )}
      </Box>

      {/* Search Results */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {!canUserSearch() && (
          <Alert severity="info" sx={{ m: 2 }}>
            {getSearchDisabledReason()}
            {collectionSyncStatus?.status === 'out_of_sync' && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Sync the collection to enable vector search.
              </Typography>
            )}
          </Alert>
        )}

        {localQuery && !searchLoading && searchResults.length === 0 && canUserSearch() && (
          <Alert severity="info" sx={{ m: 2 }}>
            No results found for "{localQuery}"
          </Alert>
        )}

        {searchResults.length > 0 && (
          <List dense sx={{ overflow: 'auto', maxHeight: maxHeight }}>
            {searchResults.map((result, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  onClick={() => onResultClick(result)}
                  sx={{ alignItems: 'flex-start', py: 1 }}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                        <FileIcon fontSize="small" color="action" />
                        <Typography variant="body2" sx={{ fontWeight: 500, flex: 1 }}>
                          {result.file_path.split('/').pop()}
                        </Typography>
                        <Chip
                          size="small"
                          label={`${(result.score * 100).toFixed(0)}%`}
                          color={getScoreColor(result.score)}
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="textSecondary">
                        {formatContent(result.content)}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      {/* Results Summary */}
      {searchResults.length > 0 && (
        <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
          <Typography variant="caption" color="textSecondary">
            Found {searchResults.length} results for "{localQuery}"
            {collectionId && ` in ${collectionId}`}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default VectorSearchPanel;