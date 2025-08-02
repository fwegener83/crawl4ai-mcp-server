import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip
} from '../ui';
import { DataTable } from '../ui/DataTable';
import { ActionButton } from '../forms';
import type { Column } from '../ui/DataTable';
import { useNotification } from '../ui/NotificationProvider';
import LanguageIcon from '@mui/icons-material/Language';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DownloadIcon from '@mui/icons-material/Download';
import SaveIcon from '@mui/icons-material/Save';
import RefreshIcon from '@mui/icons-material/Refresh';

export interface CrawlResult {
  id: string;
  url: string;
  title?: string;
  status: 'pending' | 'crawling' | 'completed' | 'failed';
  progress?: number;
  contentLength?: number;
  extractedAt?: Date;
  error?: string;
  metadata?: {
    domain: string;
    description?: string;
    keywords?: string[];
    images?: number;
    links?: number;
  };
}

export interface CrawlResultsTableProps {
  results: CrawlResult[];
  loading?: boolean;
  onViewContent?: (result: CrawlResult) => void;
  onDownloadContent?: (result: CrawlResult) => void;
  onSaveToCollection?: (result: CrawlResult) => void;
  onRetryFailed?: (result: CrawlResult) => void;
  onClearResults?: () => void;
  title?: string;
}

export const CrawlResultsTable: React.FC<CrawlResultsTableProps> = ({
  results,
  loading = false,
  onViewContent,
  onDownloadContent,
  onSaveToCollection,
  onRetryFailed,
  onClearResults,
  title = 'Crawl Results',
}) => {
  const [selectedResults, setSelectedResults] = useState<CrawlResult[]>([]);
  const { showSuccess, showError } = useNotification();

  const getStatusChip = (status: CrawlResult['status'], error?: string) => {
    const configs = {
      pending: { 
        color: 'default' as const, 
        icon: <HourglassEmptyIcon sx={{ fontSize: 14 }} />, 
        label: 'Pending' 
      },
      crawling: { 
        color: 'info' as const, 
        icon: <HourglassEmptyIcon sx={{ fontSize: 14 }} />, 
        label: 'Crawling' 
      },
      completed: { 
        color: 'success' as const, 
        icon: <CheckCircleIcon sx={{ fontSize: 14 }} />, 
        label: 'Completed' 
      },
      failed: { 
        color: 'error' as const, 
        icon: <ErrorIcon sx={{ fontSize: 14 }} />, 
        label: 'Failed' 
      },
    };

    const config = configs[status];
    return (
      <Tooltip title={error || config.label}>
        <Chip
          icon={config.icon}
          label={config.label}
          color={config.color}
          size="small"
          variant="outlined"
        />
      </Tooltip>
    );
  };

  const formatContentLength = (bytes?: number): string => {
    if (!bytes) return '-';
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const columns: Column<CrawlResult>[] = [
    {
      id: 'url',
      label: 'URL',
      sortable: true,
      align: 'left',
      render: (value, row) => (
        <Box sx={{ maxWidth: 300 }}>
          <Typography
            variant="body2"
            fontWeight="medium"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {row.title || value}
          </Typography>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              display: 'block',
            }}
          >
            {value}
          </Typography>
          {row.metadata?.domain && (
            <Chip
              label={row.metadata.domain}
              size="small"
              variant="outlined"
              sx={{ mt: 0.5, fontSize: '0.7rem', height: 20 }}
            />
          )}
        </Box>
      )
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value, row) => getStatusChip(value, row.error)
    },
    {
      id: 'contentLength',
      label: 'Size',
      sortable: true,
      align: 'right',
      render: (value) => formatContentLength(value)
    },
    {
      id: 'extractedAt',
      label: 'Extracted',
      sortable: true,
      align: 'right',
      render: (value) => value ? new Date(value).toLocaleString() : '-'
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (_, row) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {row.status === 'completed' && (
            <>
              <Tooltip title="View Content">
                <IconButton
                  size="small"
                  onClick={() => onViewContent?.(row)}
                >
                  <VisibilityIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download">
                <IconButton
                  size="small"
                  onClick={() => onDownloadContent?.(row)}
                >
                  <DownloadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Save to Collection">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={() => onSaveToCollection?.(row)}
                >
                  <SaveIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
          {row.status === 'failed' && (
            <Tooltip title="Retry">
              <IconButton
                size="small"
                color="warning"
                onClick={() => onRetryFailed?.(row)}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      )
    }
  ];

  const handleBulkSave = async () => {
    try {
      const completedResults = selectedResults.filter(r => r.status === 'completed');
      for (const result of completedResults) {
        await onSaveToCollection?.(result);
      }
      setSelectedResults([]);
      showSuccess(`${completedResults.length} result(s) saved to collection!`);
    } catch (error) {
      showError('Failed to save selected results');
    }
  };

  const handleBulkRetry = async () => {
    try {
      const failedResults = selectedResults.filter(r => r.status === 'failed');
      for (const result of failedResults) {
        await onRetryFailed?.(result);
      }
      setSelectedResults([]);
      showSuccess(`${failedResults.length} result(s) queued for retry!`);
    } catch (error) {
      showError('Failed to retry selected results');
    }
  };

  // Statistics
  const stats = {
    total: results.length,
    completed: results.filter(r => r.status === 'completed').length,
    failed: results.filter(r => r.status === 'failed').length,
    pending: results.filter(r => r.status === 'pending' || r.status === 'crawling').length,
    totalSize: results
      .filter(r => r.contentLength)
      .reduce((sum, r) => sum + (r.contentLength || 0), 0)
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        avatar={<LanguageIcon color="primary" />}
        title={title}
        subheader={
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Chip 
              label={`${stats.completed} completed`} 
              color="success" 
              size="small" 
              variant="outlined" 
            />
            <Chip 
              label={`${stats.failed} failed`} 
              color="error" 
              size="small" 
              variant="outlined" 
            />
            <Chip 
              label={`${stats.pending} pending`} 
              color="info" 
              size="small" 
              variant="outlined" 
            />
            <Chip 
              label={formatContentLength(stats.totalSize)} 
              size="small" 
              variant="outlined" 
            />
          </Box>
        }
        action={
          <ActionButton
            variant="outlined"
            color="warning"
            size="small"
            onClick={onClearResults}
            confirmAction
            confirmText="Clear all results?"
            disabled={results.length === 0}
          >
            Clear All
          </ActionButton>
        }
      />

      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
        {/* Bulk Actions Toolbar */}
        {selectedResults.length > 0 && (
          <Box sx={{ 
            p: 2, 
            borderBottom: 1, 
            borderColor: 'divider',
            backgroundColor: 'action.hover'
          }}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {selectedResults.length} selected
              </Typography>
              
              {selectedResults.some(r => r.status === 'completed') && (
                <ActionButton
                  variant="contained"
                  color="primary"
                  size="small"
                  onClick={handleBulkSave}
                  startIcon={<SaveIcon />}
                >
                  Save to Collection
                </ActionButton>
              )}
              
              {selectedResults.some(r => r.status === 'failed') && (
                <ActionButton
                  variant="outlined"
                  color="warning"
                  size="small"
                  onClick={handleBulkRetry}
                  startIcon={<RefreshIcon />}
                >
                  Retry Failed
                </ActionButton>
              )}
            </Box>
          </Box>
        )}

        {/* Results Table */}
        <Box sx={{ flex: 1 }}>
          <DataTable
            data={results}
            columns={columns}
            loading={loading}
            selectable
            onSelectionChange={setSelectedResults}
            searchable
            searchPlaceholder="Search URLs..."
            pagination
            defaultRowsPerPage={25}
            rowsPerPageOptions={[10, 25, 50, 100]}
            emptyMessage="No crawl results available"
            stickyHeader
            maxHeight="100%"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default CrawlResultsTable;