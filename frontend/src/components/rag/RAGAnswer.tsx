import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  ToggleButtonGroup,
  ToggleButton
} from '../ui';
import WarningIcon from '@mui/icons-material/Warning';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CodeIcon from '@mui/icons-material/Code';

interface RAGAnswerProps {
  answer: string | null;
  error?: string;
}

export const RAGAnswer: React.FC<RAGAnswerProps> = ({ answer, error }) => {
  const [viewMode, setViewMode] = useState<'rendered' | 'raw'>('rendered');
  // Handle degraded service state (null answer with error)
  if (answer === null && error) {
    return (
      <Card data-testid="rag-answer-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Answer
          </Typography>
          <Alert severity="warning" icon={<WarningIcon data-testid="WarningIcon" />}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Answer generation temporarily unavailable
            </Typography>
            {error.toLowerCase().includes('rate limit') && (
              <Typography variant="body2">
                Rate limit exceeded. Please try again later.
              </Typography>
            )}
            {!error.toLowerCase().includes('rate limit') && (
              <Typography variant="body2">
                {error}
              </Typography>
            )}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Handle no answer state (null answer without error)
  if (answer === null) {
    return (
      <Card data-testid="rag-answer-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Answer
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No answer generated for this query.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Handle normal answer state
  return (
    <Card data-testid="rag-answer-section" sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Answer
          </Typography>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, newMode) => newMode && setViewMode(newMode)}
            size="small"
          >
            <ToggleButton value="rendered" aria-label="rendered view">
              <VisibilityIcon fontSize="small" />
            </ToggleButton>
            <ToggleButton value="raw" aria-label="raw markdown">
              <CodeIcon fontSize="small" />
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
        
        <Box data-testid="rag-answer-content">
          {viewMode === 'rendered' ? (
            <Box
              sx={{
                '& p': { mb: 1.5, lineHeight: 1.6 },
                '& h1, & h2, & h3, & h4, & h5, & h6': { 
                  mt: 2, 
                  mb: 1,
                  fontWeight: 600,
                  color: 'primary.main'
                },
                '& code': {
                  backgroundColor: 'grey.100',
                  padding: '2px 6px',
                  borderRadius: 1,
                  fontSize: '0.875em',
                  fontFamily: 'monospace'
                },
                '& pre': {
                  backgroundColor: 'grey.50',
                  border: '1px solid',
                  borderColor: 'grey.200',
                  borderRadius: 1,
                  p: 2,
                  overflow: 'auto',
                  '& code': {
                    backgroundColor: 'transparent',
                    padding: 0
                  }
                },
                '& ul, & ol': { pl: 2, mb: 1.5 },
                '& li': { mb: 0.5 },
                '& blockquote': {
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                  pl: 2,
                  ml: 0,
                  fontStyle: 'italic',
                  color: 'text.secondary'
                }
              }}
            >
              <ReactMarkdown>{answer}</ReactMarkdown>
            </Box>
          ) : (
            <Typography 
              variant="body1" 
              component="pre"
              sx={{ 
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                lineHeight: 1.6,
                fontFamily: 'monospace',
                backgroundColor: 'grey.50',
                border: '1px solid',
                borderColor: 'grey.200',
                borderRadius: 1,
                p: 2,
                fontSize: '0.875rem'
              }}
            >
              {answer}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};