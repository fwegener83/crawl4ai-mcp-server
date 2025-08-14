import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Stack,
  Divider
} from '../ui';
import InfoIcon from '@mui/icons-material/Info';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import type { RAGQueryMetadata } from '../../types/api';

interface RAGMetadataProps {
  metadata: RAGQueryMetadata;
}

export const RAGMetadata: React.FC<RAGMetadataProps> = ({ metadata }) => {
  const formatResponseTime = (ms: number): string => {
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatChunksUsed = (count: number): string => {
    return count === 1 ? `${count} chunk` : `${count} chunks`;
  };

  const getCollectionName = (name: string | null): string => {
    return name || 'All Collections';
  };

  const getLLMProvider = (provider: string | null): string => {
    return provider || 'Vector Search Only';
  };

  return (
    <Card data-testid="rag-metadata-section" sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <InfoIcon color="primary" fontSize="small" />
          <Typography variant="h6">
            Query Metadata
          </Typography>
        </Box>

        <Stack spacing={2}>
          {/* Primary Metrics */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box data-testid="chunks-used">
              <Typography variant="caption" color="text.secondary" display="block">
                Chunks Used
              </Typography>
              <Chip
                icon={<StorageIcon fontSize="small" />}
                label={formatChunksUsed(metadata.chunks_used)}
                size="small"
                variant="outlined"
                color="primary"
              />
            </Box>

            <Box data-testid="collection-searched">
              <Typography variant="caption" color="text.secondary" display="block">
                Collection
              </Typography>
              <Chip
                label={getCollectionName(metadata.collection_searched)}
                size="small"
                variant="outlined"
              />
            </Box>

            <Box data-testid="llm-provider">
              <Typography variant="caption" color="text.secondary" display="block">
                LLM Provider
              </Typography>
              <Chip
                icon={<SmartToyIcon fontSize="small" />}
                label={getLLMProvider(metadata.llm_provider)}
                size="small"
                variant="outlined"
                color={metadata.llm_provider ? "success" : "default"}
              />
            </Box>

            <Box data-testid="response-time">
              <Typography variant="caption" color="text.secondary" display="block">
                Response Time
              </Typography>
              <Chip
                icon={<AccessTimeIcon fontSize="small" />}
                label={formatResponseTime(metadata.response_time_ms)}
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>

          {/* Token Usage (if available) */}
          {metadata.token_usage && (
            <>
              <Divider />
              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SmartToyIcon fontSize="small" />
                  Tokens Used
                </Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Total
                    </Typography>
                    <Typography variant="body2" fontWeight="600">
                      {metadata.token_usage.total}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Prompt
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {metadata.token_usage.prompt}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Completion
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {metadata.token_usage.completion}
                    </Typography>
                  </Box>
                </Stack>
              </Box>
            </>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};