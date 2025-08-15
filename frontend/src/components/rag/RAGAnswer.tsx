import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert
} from '../ui';
import WarningIcon from '@mui/icons-material/Warning';

interface RAGAnswerProps {
  answer: string | null;
  error?: string;
}

export const RAGAnswer: React.FC<RAGAnswerProps> = ({ answer, error }) => {
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
        <Typography variant="h6" gutterBottom>
          Answer
        </Typography>
        <Box data-testid="rag-answer-content">
          <Typography 
            variant="body1" 
            sx={{ 
              whiteSpace: 'pre-line',
              wordBreak: 'break-word',
              lineHeight: 1.6
            }}
          >
            {answer}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};