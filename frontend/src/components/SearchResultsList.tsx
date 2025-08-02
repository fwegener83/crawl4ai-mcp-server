import { useState } from 'react';
import type { SearchResult } from '../types/api';
import { 
  Paper, 
  Box, 
  Typography, 
  Chip, 
  IconButton, 
  List,
  ListItem,
  Divider
} from './ui';
import { Collapse, Link } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import LaunchIcon from '@mui/icons-material/Launch';

interface SearchResultsListProps {
  results: SearchResult[];
  query: string;
  onSelectResult?: (result: SearchResult, index: number) => void;
}

export function SearchResultsList({ 
  results, 
  query,
  onSelectResult 
}: SearchResultsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleResultClick = (result: SearchResult, index: number) => {
    if (onSelectResult) {
      onSelectResult(result, index);
    }
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const getScoreBadge = (score: number | undefined) => {
    if (score === undefined || score === null) {
      return (
        <Chip 
          label="No Score" 
          size="small" 
          color="default" 
        />
      );
    }
    
    if (score >= 0.8) {
      return (
        <Chip 
          label={`Excellent (${score.toFixed(3)})`} 
          size="small" 
          color="success" 
        />
      );
    } else if (score >= 0.6) {
      return (
        <Chip 
          label={`Good (${score.toFixed(3)})`} 
          size="small" 
          color="warning" 
        />
      );
    } else {
      return (
        <Chip 
          label={`Fair (${score.toFixed(3)})`} 
          size="small" 
          color="default" 
        />
      );
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <Box 
          key={index} 
          component="mark" 
          sx={{ 
            bgcolor: 'warning.light',
            color: 'warning.contrastText',
            px: 0.5,
            borderRadius: 0.5
          }}
        >
          {part}
        </Box>
      ) : (
        part
      )
    );
  };

  if (results.length === 0) {
    return (
      <Paper sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center' }}>
          <SearchIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {query ? 'No results found' : 'No search performed'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {query 
              ? `No content found matching "${query}". Try a different search term.`
              : 'Enter a search query above to find relevant content.'
            }
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Search Results ({results.length})
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Query: "{query}"
          </Typography>
        </Box>
      </Box>

      {/* Results List */}
      <List disablePadding>
        {results.map((result, index) => (
          <Box key={index}>
            <ListItem 
              sx={{ 
                flexDirection: 'column',
                alignItems: 'stretch',
                '&:hover': { bgcolor: 'action.hover' }
              }}
            >
              <Box sx={{ display: 'flex', width: '100%', alignItems: 'flex-start' }}>
                <Box sx={{ flex: 1, cursor: 'pointer' }} onClick={() => handleResultClick(result, index)}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        {result.metadata.source_url && (
                          <Link 
                            href={result.metadata.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            variant="body2"
                            sx={{ 
                              maxWidth: 300,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {result.metadata.source_url}
                          </Link>
                        )}
                        {getScoreBadge(result.metadata.score)}
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary">
                        <Box component="span" fontWeight="medium">
                          Chunk {result.metadata.chunk_index + 1}
                        </Box>
                        {' '} • Distance: {result.distance ? result.distance.toFixed(4) : 'N/A'}
                      </Typography>
                    </Box>
                  </Box>

                  {/* Content Preview */}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}
                  >
                    {highlightText(
                      result.content.length > 200 
                        ? `${result.content.substring(0, 200)}...`
                        : result.content,
                      query
                    )}
                  </Typography>
                </Box>

                {/* Expand Button */}
                <IconButton
                  onClick={() => handleResultClick(result, index)}
                  size="small"
                >
                  {expandedIndex === index ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>

              {/* Expanded Content */}
              <Collapse in={expandedIndex === index} timeout="auto" unmountOnExit>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'action.selected', borderRadius: 1 }}>
                  <Box sx={{ mb: 2 }}>
                    {/* Metadata */}
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      pb: 1,
                      borderBottom: 1,
                      borderColor: 'divider'
                    }}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          Chunk: {result.metadata.chunk_index + 1}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Score: {result.metadata.score ? result.metadata.score.toFixed(4) : 'N/A'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Distance: {result.distance ? result.distance.toFixed(4) : 'N/A'}
                        </Typography>
                      </Box>
                      {result.metadata.source_url && (
                        <Link 
                          href={result.metadata.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          variant="caption"
                          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                        >
                          View Source
                          <LaunchIcon sx={{ fontSize: 12 }} />
                        </Link>
                      )}
                    </Box>

                    {/* Full Content */}
                    <Box sx={{ 
                      mt: 2,
                      maxHeight: 256,
                      overflow: 'auto',
                      whiteSpace: 'pre-wrap'
                    }}>
                      <Typography variant="body2">
                        {highlightText(result.content, query)}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Collapse>
            </ListItem>
            {index < results.length - 1 && <Divider />}
          </Box>
        ))}
      </List>

      {/* Summary Footer */}
      <Box sx={{ 
        p: 2, 
        bgcolor: 'action.selected', 
        borderTop: 1, 
        borderColor: 'divider' 
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Avg Score: {(results.reduce((sum, r) => sum + (r.metadata.score || 0), 0) / results.length).toFixed(3)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Characters: {results.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Click to expand • Highlighted matches
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default SearchResultsList;