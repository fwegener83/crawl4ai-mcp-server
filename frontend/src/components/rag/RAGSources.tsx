import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack
} from '../ui';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArticleIcon from '@mui/icons-material/Article';
import type { RAGSource } from '../../types/api';

interface RAGSourcesProps {
  sources: RAGSource[];
}

export const RAGSources: React.FC<RAGSourcesProps> = ({ sources }) => {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

  // Sort sources by similarity score in descending order
  const sortedSources = [...sources].sort((a, b) => b.similarity_score - a.similarity_score);

  const toggleSource = (index: number) => {
    const newExpanded = new Set(expandedSources);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSources(newExpanded);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return null;
    }
  };

  const truncateContent = (content: string, maxLength = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  if (sources.length === 0) {
    return (
      <Card data-testid="rag-sources-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Sources
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No sources found for this query.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card data-testid="rag-sources-section" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Sources
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {sources.length} sources found
        </Typography>

        <Stack spacing={2}>
          {sortedSources.map((source, index) => (
            <Accordion
              key={`${source.metadata.source}-${index}`}
              data-testid={`source-item-${index}`}
              expanded={expandedSources.has(index)}
              onChange={() => toggleSource(index)}
              sx={{
                '&:before': { display: 'none' },
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                '&.Mui-expanded': {
                  margin: 0
                }
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{
                  '&.Mui-expanded': {
                    minHeight: 48
                  },
                  '& .MuiAccordionSummary-content': {
                    margin: '12px 0',
                    '&.Mui-expanded': {
                      margin: '12px 0'
                    }
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <ArticleIcon color="primary" fontSize="small" />
                  
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {source.metadata.source}
                    </Typography>
                    
                    {!expandedSources.has(index) && (
                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        data-testid={`source-preview-${index}`}
                        sx={{ 
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {truncateContent(source.content)}
                      </Typography>
                    )}
                  </Box>

                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      label={`${Math.round(source.similarity_score * 100)}%`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    
                    {source.collection_name && (
                      <Chip
                        label={source.collection_name}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Stack>
                </Box>
              </AccordionSummary>

              <AccordionDetails>
                <Stack spacing={2}>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-line',
                      wordBreak: 'break-word',
                      lineHeight: 1.6,
                      bgcolor: 'background.paper',
                      p: 2,
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                  >
                    {source.content}
                  </Typography>
                  
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      <strong>File:</strong> {source.file_path || source.metadata.source}
                      {source.metadata.created_at && formatDate(source.metadata.created_at) && (
                        <>
                          {' • '}
                          <strong>Created:</strong> {formatDate(source.metadata.created_at)}
                        </>
                      )}
                    </Typography>
                  </Box>
                </Stack>
              </AccordionDetails>
            </Accordion>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
};