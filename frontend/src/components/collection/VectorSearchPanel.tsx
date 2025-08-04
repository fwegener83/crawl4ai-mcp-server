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
  Collapse,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  InsertDriveFile as FileIcon,
  Code as CodeIcon,
  Article as ArticleIcon,
  List as ListIcon,
  Subject as SubjectIcon
} from '@mui/icons-material';
import { useDebounce } from '../../hooks/useDebounce';
import type { VectorSearchResult, VectorSyncStatus } from '../../types/api';

interface VectorSearchPanelProps {
  collectionName?: string;
  collectionSyncStatus?: VectorSyncStatus;
  searchResults: VectorSearchResult[];
  searchQuery: string;
  searchLoading: boolean;
  onSearch: (query: string, collectionName?: string) => Promise<void>;
  onResultClick: (result: VectorSearchResult) => void;
  onClearSearch: () => void;
  maxHeight?: number;
  showCollectionFilter?: boolean;
}

export const VectorSearchPanel: React.FC<VectorSearchPanelProps> = ({
  collectionName,
  collectionSyncStatus,
  searchResults,
  searchQuery,
  searchLoading,
  onSearch,
  onResultClick,
  onClearSearch,
  maxHeight = 400, // TODO: implement dynamic height
  showCollectionFilter = false // TODO: implement collection filter
}) => {
  const [localQuery, setLocalQuery] = useState(searchQuery);
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());
  const debouncedQuery = useDebounce(localQuery, 300);

  // Perform search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim()) {
      onSearch(debouncedQuery, collectionName);
    } else if (searchQuery) {
      onClearSearch();
    }
  }, [debouncedQuery, collectionName, onSearch, onClearSearch, searchQuery]);

  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(event.target.value);
  };

  const handleClearQuery = () => {
    setLocalQuery('');
    onClearSearch();
  };

  const toggleResultExpansion = (index: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  const getChunkTypeIcon = (chunkType: string) => {
    switch (chunkType.toLowerCase()) {
      case 'code_block':
        return <CodeIcon fontSize="small" />;
      case 'header_section':
        return <ArticleIcon fontSize="small" />;
      case 'list':
        return <ListIcon fontSize="small" />;
      default:
        return <SubjectIcon fontSize="small" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'success';
    if (score >= 0.7) return 'warning';
    return 'default';
  };

  const formatContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  const highlightQuery = (text: string, query: string) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} style={{ backgroundColor: '#ffeb3b', padding: '0 2px' }}>
          {part}
        </mark>
      ) : part
    );
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
        return `${collectionSyncStatus.changed_files_count} files have changed since last sync`;
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
        {collectionName && collectionSyncStatus && !showCollectionFilter && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="textSecondary">
              Collection: {collectionName}
            </Typography>
            <Chip
              size="small"
              label={`${collectionSyncStatus.chunk_count} chunks`}
              variant="outlined"
            />
            {!canUserSearch() && (
              <Tooltip title={getSearchDisabledReason()}>
                <Chip
                  size="small"
                  label="Sync required"
                  color="warning"
                  variant="outlined"
                />
              </Tooltip>
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
          <Box sx={{ height: '100%', maxHeight: maxHeight, overflow: 'auto' }}>
            <List dense>
              {searchResults.map((result, index) => {
                const isExpanded = expandedResults.has(index);
                const { metadata } = result;
                
                return (
                  <React.Fragment key={index}>
                    <ListItem disablePadding>
                      <ListItemButton
                        onClick={() => onResultClick(result)}
                        sx={{ 
                          alignItems: 'flex-start',
                          py: 1,
                          '&:hover': {
                            backgroundColor: 'action.hover'
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                              <FileIcon fontSize="small" color="action" />
                              <Typography variant="body2" component="span" sx={{ fontWeight: 500 }}>
                                {result.file_path.split('/').pop()}
                              </Typography>
                              <Box display="flex" alignItems="center" gap={0.5}>
                                {getChunkTypeIcon(metadata.chunk_type)}
                                <Chip
                                  size="small"
                                  label={`${(result.score * 100).toFixed(0)}%`}
                                  color={getScoreColor(result.score)}
                                  variant="outlined"
                                  sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                              </Box>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                                {highlightQuery(formatContent(result.content), localQuery)}
                              </Typography>
                              
                              {metadata.header_hierarchy && (
                                <Typography variant="caption" color="textSecondary">
                                  {metadata.header_hierarchy}
                                </Typography>
                              )}
                              
                              <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                                {metadata.contains_code && (
                                  <Chip
                                    size="small"
                                    label={metadata.programming_language || "Code"}
                                    color="primary"
                                    variant="outlined"
                                    sx={{ height: 16, fontSize: '0.65rem' }}
                                  />
                                )}
                                <Chip
                                  size="small"
                                  label={`Chunk ${result.chunk_index + 1}`}
                                  variant="outlined"
                                  sx={{ height: 16, fontSize: '0.65rem' }}
                                />
                              </Box>
                            </Box>
                          }
                        />
                        
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleResultExpansion(index);
                          }}
                        >
                          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </ListItemButton>
                    </ListItem>

                    {/* Expanded Content */}
                    <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                      <Box sx={{ px: 2, pb: 2 }}>
                        <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <Typography variant="body2" component="pre" sx={{ 
                            whiteSpace: 'pre-wrap',
                            fontFamily: metadata.contains_code ? 'monospace' : 'inherit',
                            maxHeight: 200,
                            overflow: 'auto'
                          }}>
                            {highlightQuery(result.content, localQuery)}
                          </Typography>
                        </Paper>
                      </Box>
                    </Collapse>

                    {index < searchResults.length - 1 && <Divider />}
                  </React.Fragment>
                );
              })}
            </List>
          </Box>
        )}
      </Box>

      {/* Results Summary */}
      {searchResults.length > 0 && (
        <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
          <Typography variant="caption" color="textSecondary">
            Found {searchResults.length} results for "{localQuery}"
            {collectionName && ` in ${collectionName}`}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default VectorSearchPanel;