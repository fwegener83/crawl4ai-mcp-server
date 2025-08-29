import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
  Switch,
  FormControlLabel,
  Collapse,
  Slider,
  Tooltip,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  InsertDriveFile as FileIcon,
  ChevronRight as ChevronRightIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useDebounce } from '../../hooks/useDebounce';
import type { 
  EnhancedVectorSearchResult, 
  VectorSyncStatus
} from '../../types/api';

interface EnhancedSearchOptions {
  enableContextExpansion: boolean;
  relationshipFilter: Record<string, any> | null;
  similarityThreshold: number;
}

interface EnhancedVectorSearchPanelProps {
  collectionId?: string;
  collectionSyncStatus?: VectorSyncStatus;
  searchResults: EnhancedVectorSearchResult[];
  searchQuery: string;
  searchLoading: boolean;
  onSearch: (query: string, collectionId?: string) => Promise<void>;
  onEnhancedSearch?: (query: string, collectionId?: string, options?: Partial<EnhancedSearchOptions>) => Promise<void>;
  onResultClick: (result: EnhancedVectorSearchResult) => void;
  onClearSearch: () => void;
  maxHeight?: number;
  showEnhancedFeatures?: boolean;
  enhancedSearchError?: string;
}

export const EnhancedVectorSearchPanel: React.FC<EnhancedVectorSearchPanelProps> = ({
  collectionId,
  collectionSyncStatus,
  searchResults,
  searchQuery,
  searchLoading,
  onSearch,
  onEnhancedSearch,
  onResultClick,
  onClearSearch,
  maxHeight = 400,
  showEnhancedFeatures = true,
  enhancedSearchError
}) => {
  const [localQuery, setLocalQuery] = useState(searchQuery);
  const [contextExpansion, setContextExpansion] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.2);
  const [enhancedFeaturesError, setEnhancedFeaturesError] = useState<string | null>(null);
  
  const debouncedQuery = useDebounce(localQuery, 300);

  // Enhanced search options
  const searchOptions = useMemo((): Partial<EnhancedSearchOptions> => ({
    enableContextExpansion: contextExpansion,
    relationshipFilter: null, // Could be extended for complex relationship filtering
    similarityThreshold
  }), [contextExpansion, similarityThreshold]);

  // Handle search execution with enhanced features
  const executeSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      onClearSearch();
      return;
    }

    try {
      setEnhancedFeaturesError(null);
      
      if (showEnhancedFeatures && onEnhancedSearch && (contextExpansion || similarityThreshold !== 0.2)) {
        await onEnhancedSearch(query, collectionId, searchOptions);
      } else {
        await onSearch(query, collectionId);
      }
    } catch (error) {
      console.error('Enhanced search failed:', error);
      setEnhancedFeaturesError('Enhanced features temporarily unavailable');
      
      // Fallback to standard search
      try {
        await onSearch(query, collectionId);
      } catch (fallbackError) {
        console.error('Fallback search also failed:', fallbackError);
      }
    }
  }, [
    onSearch, 
    onEnhancedSearch, 
    collectionId, 
    searchOptions, 
    contextExpansion, 
    similarityThreshold, 
    showEnhancedFeatures,
    onClearSearch
  ]);

  // Perform search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim()) {
      executeSearch(debouncedQuery);
    } else if (searchQuery) {
      onClearSearch();
    }
  }, [debouncedQuery, searchQuery, executeSearch, onClearSearch]);

  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(event.target.value);
  };

  const handleClearQuery = () => {
    setLocalQuery('');
    setEnhancedFeaturesError(null);
    onClearSearch();
  };

  const handleContextExpansionChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    setContextExpansion(newValue);
    
    if (localQuery.trim()) {
      // Trigger search with new context expansion setting
      await executeSearch(localQuery);
    }
  };

  const handleSimilarityThresholdChange = (_event: Event, newValue: number | number[]) => {
    setSimilarityThreshold(newValue as number);
  };

  const handleRelatedChunkClick = useCallback((chunkId: string) => {
    // Create a mock result for the related chunk - in real implementation, 
    // this would fetch the actual chunk data
    const mockRelatedResult: EnhancedVectorSearchResult = {
      chunk_id: chunkId,
      content: `Content for chunk ${chunkId}`,
      score: 0.0, // Placeholder - would be actual similarity score
      collection_name: collectionId || '',
      file_path: 'related-chunk',
      chunk_index: 0,
      metadata: {
        chunk_type: 'related',
        header_hierarchy: '',
        contains_code: false,
        created_at: new Date().toISOString()
      }
    };
    
    onResultClick(mockRelatedResult);
  }, [collectionId, onResultClick]);

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

  // Render enhanced result indicators
  const renderEnhancedIndicators = (result: EnhancedVectorSearchResult) => {
    const indicators = [];
    
    // Overlap indicator
    if (result.relationship_data?.overlap_percentage) {
      const overlapPercent = Math.round(result.relationship_data.overlap_percentage * 100);
      indicators.push(
        <Tooltip key="overlap" title={`This chunk overlaps ${overlapPercent}% with adjacent chunks for better context`}>
          <Chip
            size="small"
            icon={<TimelineIcon />}
            label={`${overlapPercent}% Overlap`}
            color="info"
            variant="outlined"
            sx={{ fontSize: '0.7rem', height: 18 }}
          />
        </Tooltip>
      );
    }
    
    // Expansion indicator
    if (result.expansion_source) {
      indicators.push(
        <Tooltip key="expansion" title={`Result expanded through ${result.expansion_type} relationship`}>
          <Chip
            size="small"
            label="Expanded"
            color="secondary"
            variant="outlined"
            sx={{ fontSize: '0.7rem', height: 18 }}
          />
        </Tooltip>
      );
    }
    
    return indicators;
  };

  // Render chunk navigation
  const renderChunkNavigation = (result: EnhancedVectorSearchResult) => {
    if (!result.relationship_data) return null;
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
        {result.relationship_data.previous_chunk_id && (
          <Tooltip title="Previous chunk">
            <IconButton
              size="small"
              onClick={() => handleRelatedChunkClick(result.relationship_data!.previous_chunk_id!)}
              aria-label="Previous chunk"
              sx={{ width: 24, height: 24 }}
            >
              <ChevronRightIcon sx={{ transform: 'rotate(180deg)', fontSize: 16 }} />
            </IconButton>
          </Tooltip>
        )}
        
        {result.relationship_data.next_chunk_id && (
          <Tooltip title="Next chunk">
            <IconButton
              size="small"
              onClick={() => handleRelatedChunkClick(result.relationship_data!.next_chunk_id!)}
              aria-label="Next chunk"
              sx={{ width: 24, height: 24 }}
            >
              <ChevronRightIcon sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    );
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

        {/* Enhanced Features Controls */}
        {showEnhancedFeatures && canUserSearch() && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={contextExpansion}
                    onChange={handleContextExpansionChange}
                    size="small"
                    inputProps={{ 'aria-label': 'Enable Context Expansion' }}
                  />
                }
                label="Enable Context Expansion"
                sx={{ mr: 2 }}
              />
              
              <IconButton
                onClick={() => setShowSettings(!showSettings)}
                size="small"
                aria-label="Enhanced Search Settings"
              >
                <SettingsIcon />
              </IconButton>
            </Box>
            
            <Collapse in={showSettings}>
              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="caption" color="textSecondary" gutterBottom>
                  Similarity Threshold
                </Typography>
                <Slider
                  value={similarityThreshold}
                  onChange={handleSimilarityThresholdChange}
                  min={0.0}
                  max={1.0}
                  step={0.05}
                  size="small"
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                  aria-label="Similarity Threshold"
                  sx={{ ml: 1, mr: 1 }}
                />
              </Box>
            </Collapse>
          </Box>
        )}

        {/* Collection Info */}
        {collectionId && collectionSyncStatus && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Typography variant="caption" color="textSecondary">
              {collectionId} • {collectionSyncStatus.chunk_count} chunks
            </Typography>
            
            {/* Enhanced Collection Statistics */}
            {collectionSyncStatus.enhanced_features_enabled && (
              <>
                <Typography variant="caption" color="textSecondary">
                  • {collectionSyncStatus.overlap_chunk_count || 0} overlap chunks
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  • {collectionSyncStatus.context_expansion_eligible_chunks || 0} expandable
                </Typography>
              </>
            )}
            
            {!canUserSearch() && (
              <Chip size="small" label="Sync required" color="warning" variant="outlined" />
            )}
          </Box>
        )}
      </Box>

      {/* Search Results */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {/* Error Messages */}
        {enhancedSearchError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {enhancedSearchError}
            <Typography variant="body2" sx={{ mt: 1 }}>
              Falling back to standard search
            </Typography>
          </Alert>
        )}
        
        {enhancedFeaturesError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {enhancedFeaturesError}
          </Alert>
        )}

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
                  sx={{ alignItems: 'flex-start', py: 1, flexDirection: 'column' }}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1} mb={0.5} width="100%">
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
                      <Box>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          {formatContent(result.content)}
                        </Typography>
                        
                        {/* Enhanced Metadata */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', mb: 0.5 }}>
                          {result.metadata.header_hierarchy && (
                            <Typography variant="caption" color="textSecondary">
                              {result.metadata.header_hierarchy}
                            </Typography>
                          )}
                          
                          <Chip
                            size="small"
                            label={result.metadata.chunk_type}
                            variant="outlined"
                            sx={{ fontSize: '0.6rem', height: 16 }}
                          />
                          
                          {result.metadata.programming_language && (
                            <Chip
                              size="small"
                              label={result.metadata.programming_language}
                              color="primary"
                              variant="outlined"
                              sx={{ fontSize: '0.6rem', height: 16 }}
                            />
                          )}
                        </Box>
                        
                        {/* Enhanced Indicators */}
                        {showEnhancedFeatures && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
                            {renderEnhancedIndicators(result)}
                          </Box>
                        )}
                      </Box>
                    }
                  />
                  
                  {/* Chunk Navigation */}
                  {showEnhancedFeatures && renderChunkNavigation(result)}
                </ListItemButton>
                
                {index < searchResults.length - 1 && (
                  <Divider variant="inset" component="li" />
                )}
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
            {contextExpansion && ' (with context expansion)'}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default EnhancedVectorSearchPanel;