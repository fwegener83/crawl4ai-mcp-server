import { useState } from 'react';
import DocumentViewerModal from './DocumentViewerModal';
import type { CrawlResult } from '../types/api';
import {
  Paper,
  Box,
  Typography,
  Chip,
  Checkbox,
  IconButton,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider
} from './ui';
import { FormControlLabel, Collapse } from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import EditIcon from '@mui/icons-material/Edit';

interface CrawlResultsListProps {
  results: CrawlResult[];
  onSelectResult?: (result: CrawlResult, index: number) => void;
  onSelectMultiple?: (results: CrawlResult[], indices: number[]) => void;
  selectedIndices?: number[];
}

export function CrawlResultsList({ 
  results, 
  onSelectResult, 
  onSelectMultiple,
  selectedIndices = [] 
}: CrawlResultsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [localSelectedIndices, setLocalSelectedIndices] = useState<number[]>(selectedIndices);
  const [showDocumentViewer, setShowDocumentViewer] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<CrawlResult | null>(null);

  const handleResultClick = (result: CrawlResult, index: number) => {
    if (onSelectResult) {
      onSelectResult(result, index);
    }
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const handleOpenDocumentViewer = (result: CrawlResult) => {
    setSelectedDocument(result);
    setShowDocumentViewer(true);
  };

  const handleCheckboxChange = (index: number, checked: boolean) => {
    const newSelected = checked 
      ? [...localSelectedIndices, index]
      : localSelectedIndices.filter(i => i !== index);
    
    setLocalSelectedIndices(newSelected);
    
    if (onSelectMultiple) {
      const selectedResults = newSelected.map(i => results[i]);
      onSelectMultiple(selectedResults, newSelected);
    }
  };

  const handleSelectAll = () => {
    const allIndices = results.map((_, index) => index);
    const isAllSelected = localSelectedIndices.length === results.length;
    const newSelected = isAllSelected ? [] : allIndices;
    
    setLocalSelectedIndices(newSelected);
    
    if (onSelectMultiple) {
      const selectedResults = newSelected.map(i => results[i]);
      onSelectMultiple(selectedResults, newSelected);
    }
  };

  const getStatusBadge = (result: CrawlResult) => {
    if (result.success) {
      return (
        <Chip 
          label="Success" 
          size="small" 
          color="success" 
        />
      );
    } else {
      return (
        <Chip 
          label="Failed" 
          size="small" 
          color="error" 
        />
      );
    }
  };

  const getDepthBadge = (depth: number) => {
    const colors = ['primary', 'secondary', 'info', 'warning'] as const;
    const color = colors[depth % colors.length];
    
    return (
      <Chip 
        label={`Depth ${depth}`} 
        size="small" 
        color={color} 
      />
    );
  };

  if (results.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <DescriptionIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No crawl results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Start a deep crawl to see results here.
        </Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={1} sx={{ 
      width: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      maxHeight: 'calc(100vh - 200px)', // Overall container height limit
      overflow: 'hidden'
    }}>
      {/* Header */}
      <Box sx={{ 
        p: 3, 
        borderBottom: 1, 
        borderColor: 'divider',
        flexShrink: 0 // Don't shrink the header
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Crawl Results ({results.length})
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={localSelectedIndices.length === results.length && results.length > 0}
                  onChange={handleSelectAll}
                  size="small"
                />
              }
              label="Select All"
              componentsProps={{
                typography: { variant: 'body2' }
              }}
            />
            {localSelectedIndices.length > 0 && (
              <Typography variant="body2" color="success.main">
                {localSelectedIndices.length} selected
              </Typography>
            )}
          </Box>
        </Box>
      </Box>

      {/* Results List - Flexible Height with Scroll */}
      <Box sx={{ 
        flex: 1, // Take all available space
        overflow: 'auto',
        minHeight: '200px' // Minimum height to ensure visibility
      }}>
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
              <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%', gap: 2 }}>
                <Checkbox
                  checked={localSelectedIndices.includes(index)}
                  onChange={(e) => handleCheckboxChange(index, e.target.checked)}
                  size="small"
                  sx={{ mt: 0.5 }}
                />
                
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <ListItemButton
                      onClick={() => handleResultClick(result, index)}
                      sx={{ 
                        flex: 1,
                        textAlign: 'left',
                        p: 0,
                        '&:hover': { bgcolor: 'transparent' }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Typography 
                            variant="body2" 
                            fontWeight="medium"
                            noWrap
                          >
                            {result.title || 'Untitled Page'}
                          </Typography>
                        }
                        secondary={
                          <Typography 
                            variant="body2" 
                            color="primary"
                            noWrap
                            sx={{ '&:hover': { textDecoration: 'underline' } }}
                          >
                            {result.url}
                          </Typography>
                        }
                      />
                    </ListItemButton>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                      {getStatusBadge(result)}
                      {getDepthBadge(result.depth)}
                      {result.metadata.score > 0 && (
                        <Chip 
                          label={`Score: ${result.metadata.score.toFixed(1)}`} 
                          size="small" 
                          color="warning" 
                        />
                      )}
                      {result.success && (
                        <Button
                          size="small"
                          variant="contained"
                          startIcon={<EditIcon />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenDocumentViewer(result);
                          }}
                          data-testid="view-edit-button"
                        >
                          View & Edit
                        </Button>
                      )}
                    </Box>
                  </Box>

                  {/* Expandable Content */}
                  <Collapse in={expandedIndex === index} timeout="auto" unmountOnExit>
                    {result.success ? (
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'action.selected', borderRadius: 1 }}>
                        <Typography variant="body2" fontWeight="medium" gutterBottom>
                          Content Preview:
                        </Typography>
                        <Box sx={{ 
                          maxHeight: 128, 
                          overflow: 'auto',
                          mb: 2,
                          whiteSpace: 'pre-wrap'
                        }}>
                          <Typography variant="body2">
                            {result.content.length > 300 
                              ? `${result.content.substring(0, 300)}...`
                              : result.content
                            }
                          </Typography>
                        </Box>
                        <Box sx={{ 
                          pt: 1,
                          borderTop: 1,
                          borderColor: 'divider',
                          display: 'flex',
                          justifyContent: 'space-between'
                        }}>
                          <Typography variant="caption" color="text.secondary">
                            Crawled: {new Date(result.metadata.crawl_time).toLocaleString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {result.content.length} characters
                          </Typography>
                        </Box>
                      </Box>
                    ) : (
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
                        <Typography variant="body2" color="error.contrastText" fontWeight="medium">
                          Crawl failed for this URL
                        </Typography>
                      </Box>
                    )}
                  </Collapse>
                </Box>

                {/* Expand/Collapse Button */}
                <IconButton
                  onClick={() => handleResultClick(result, index)}
                  size="small"
                >
                  {expandedIndex === index ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
            </ListItem>
            {index < results.length - 1 && <Divider />}
          </Box>
        ))}
        </List>
      </Box>

      {/* Summary Footer */}
      <Box sx={{ 
        p: 2, 
        bgcolor: 'action.selected', 
        borderTop: 1, 
        borderColor: 'divider',
        flexShrink: 0 // Don't shrink the footer
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Successful: {results.filter(r => r.success).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Failed: {results.filter(r => !r.success).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Content: {results.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()} chars
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Click to expand • Select for bulk actions
          </Typography>
        </Box>
      </Box>

      {/* Document Viewer Modal */}
      <DocumentViewerModal
        isOpen={showDocumentViewer}
        onClose={() => setShowDocumentViewer(false)}
        result={selectedDocument}
      />
    </Paper>
  );
}

export default CrawlResultsList;