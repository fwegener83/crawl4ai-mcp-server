import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  LinearProgress,
  Collapse,
  Tooltip,
  Button,
  Divider
} from '@mui/material';
import {
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import type { VectorSyncStatus } from '../../types/api';

interface EnhancedCollectionSyncStatusProps {
  syncStatus: VectorSyncStatus;
  collectionName: string;
  onSyncClick?: () => void;
  onShowDetails?: () => void;
  onShowStatistics?: (collectionName: string) => void;
  showEnhancedFeatures?: boolean;
  compact?: boolean;
}

export const EnhancedCollectionSyncStatus: React.FC<EnhancedCollectionSyncStatusProps> = ({
  syncStatus,
  collectionName,
  onSyncClick,
  onShowDetails,
  onShowStatistics,
  showEnhancedFeatures = true,
  compact = false
}) => {
  const [expanded, setExpanded] = useState(false);

  // Memoized calculations for performance
  const enhancedMetrics = useMemo(() => {
    if (!syncStatus.enhanced_features_enabled || !showEnhancedFeatures) {
      return null;
    }

    const overlapRatio = syncStatus.overlap_chunk_count && syncStatus.chunk_count 
      ? (syncStatus.overlap_chunk_count / syncStatus.chunk_count * 100).toFixed(0)
      : '0';

    const expansionRatio = syncStatus.context_expansion_eligible_chunks && syncStatus.chunk_count
      ? (syncStatus.context_expansion_eligible_chunks / syncStatus.chunk_count * 100).toFixed(0)
      : '0';

    return {
      overlapRatio,
      expansionRatio,
      overlapChunks: syncStatus.overlap_chunk_count || 0,
      expandableChunks: syncStatus.context_expansion_eligible_chunks || 0
    };
  }, [syncStatus, showEnhancedFeatures]);

  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'few seconds ago';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return date.toLocaleDateString();
  };

  const getStatusIcon = () => {
    switch (syncStatus.status) {
      case 'in_sync':
        return <CheckCircleIcon color="success" />;
      case 'syncing':
        return <SyncIcon className="animate-spin" color="primary" />;
      case 'sync_error':
        return <ErrorIcon color="error" />;
      case 'out_of_sync':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="action" />;
    }
  };

  const getStatusColor = () => {
    switch (syncStatus.status) {
      case 'in_sync':
        return 'success';
      case 'syncing':
        return 'info';
      case 'sync_error':
        return 'error';
      case 'out_of_sync':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 0.9) return 'success';
    if (score >= 0.7) return 'warning';
    return 'error';
  };

  const renderMainStatus = () => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {getStatusIcon()}
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {collectionName}
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', flex: 1 }}>
        <Chip
          size="small"
          label={syncStatus.status.replace('_', ' ')}
          color={getStatusColor() as any}
          variant="outlined"
        />
        
        {syncStatus.enhanced_features_enabled && showEnhancedFeatures && (
          <Tooltip title="Collection uses enhanced RAG features with overlap-aware chunking and context expansion">
            <Chip
              size="small"
              icon={<TimelineIcon />}
              label="Enhanced RAG"
              color="secondary"
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          </Tooltip>
        )}
        
        {syncStatus.errors.length > 0 && (
          <Chip
            size="small"
            icon={<ErrorIcon />}
            label={`${syncStatus.errors.length} Error${syncStatus.errors.length > 1 ? 's' : ''}`}
            color="error"
            variant="outlined"
          />
        )}
        
        {syncStatus.warnings.length > 0 && (
          <Chip
            size="small"
            icon={<WarningIcon />}
            label={`${syncStatus.warnings.length} Warning${syncStatus.warnings.length > 1 ? 's' : ''}`}
            color="warning"
            variant="outlined"
          />
        )}
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title="Show sync details">
          <IconButton
            onClick={() => setExpanded(!expanded)}
            size="small"
            aria-label="Show sync details"
          >
            <ExpandMoreIcon 
              sx={{ 
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s ease'
              }}
            />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );

  const renderQuickStats = () => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
      <Typography variant="body2" color="textSecondary">
        Files: {syncStatus.synced_files}/{syncStatus.total_files}
      </Typography>
      
      <Typography variant="body2" color="textSecondary">
        {formatNumber(syncStatus.chunk_count)} total chunks
      </Typography>
      
      {enhancedMetrics && (
        <>
          <Typography variant="body2" color="textSecondary">
            {formatNumber(enhancedMetrics.overlapChunks)} overlap chunks
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {formatNumber(enhancedMetrics.expandableChunks)} expandable chunks
          </Typography>
        </>
      )}
      
      <Typography variant="body2" color="textSecondary">
        {Math.round(syncStatus.sync_health_score * 100)}% health
      </Typography>
      
      {syncStatus.last_sync && (
        <Typography variant="body2" color="textSecondary">
          Last sync: {formatTimeAgo(syncStatus.last_sync)}
        </Typography>
      )}
    </Box>
  );

  const renderProgress = () => {
    if (syncStatus.status !== 'syncing' || syncStatus.sync_progress === null) {
      return null;
    }

    return (
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">
            Syncing... ({Math.round(syncStatus.sync_progress * 100)}%)
          </Typography>
          {syncStatus.enhanced_features_enabled && (
            <Typography variant="caption" color="textSecondary">
              Enhanced Processing
            </Typography>
          )}
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={syncStatus.sync_progress * 100}
          sx={{ borderRadius: 1 }}
        />
      </Box>
    );
  };

  const renderDetailedStats = () => (
    <Collapse in={expanded}>
      <Divider sx={{ mb: 2 }} />
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          <Box sx={{ flex: 1, minWidth: '300px' }}>
            <Typography variant="subtitle2" gutterBottom>
              <SpeedIcon sx={{ mr: 1, fontSize: 16 }} />
              Performance Metrics
            </Typography>
            
            <Box sx={{ pl: 3, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {syncStatus.last_sync_duration && (
                <Typography variant="body2">
                  Sync Duration: {formatDuration(syncStatus.last_sync_duration)}
                </Typography>
              )}
              
              <Typography variant="body2">
                Health Score: 
                <Chip 
                  size="small" 
                  label={`${Math.round(syncStatus.sync_health_score * 100)}%`}
                  color={getHealthColor(syncStatus.sync_health_score) as any}
                  sx={{ ml: 1, fontSize: '0.7rem', height: 20 }}
                />
              </Typography>
              
              {syncStatus.enhanced_features_enabled && (
                <Typography variant="body2" color="success.main">
                  Enhanced Processing: Active
                </Typography>
              )}
            </Box>
          </Box>
          
          {enhancedMetrics && (
            <Box sx={{ flex: 1, minWidth: '300px' }}>
              <Typography variant="subtitle2" gutterBottom>
                <TimelineIcon sx={{ mr: 1, fontSize: 16 }} />
                Enhanced RAG Metrics
              </Typography>
              
              <Box sx={{ pl: 3, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Typography variant="body2">
                  Overlap Ratio: {enhancedMetrics.overlapRatio}%
                </Typography>
                
                <Typography variant="body2">
                  Context Expansion Eligible: {enhancedMetrics.expansionRatio}%
                </Typography>
                
                <Typography variant="body2">
                  Total Enhanced Chunks: {formatNumber(enhancedMetrics.overlapChunks + enhancedMetrics.expandableChunks)}
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          {onShowStatistics && (
            <Button
              size="small"
              variant="outlined"
              onClick={() => onShowStatistics(collectionName)}
              startIcon={<TrendingUpIcon />}
            >
              View Statistics
            </Button>
          )}
          
          {onSyncClick && syncStatus.status !== 'syncing' && (
            <Button
              size="small"
              variant="contained"
              onClick={onSyncClick}
              startIcon={<SyncIcon />}
            >
              Sync Now
            </Button>
          )}
        </Box>
      </Box>
      
      {/* Error and Warning Details */}
      {(syncStatus.errors.length > 0 || syncStatus.warnings.length > 0) && (
        <Box sx={{ mt: 2 }}>
          <Divider sx={{ mb: 2 }} />
          
          {syncStatus.errors.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="error" gutterBottom>
                Errors:
              </Typography>
              {syncStatus.errors.map((error, index) => (
                <Typography key={index} variant="body2" color="error" sx={{ pl: 2 }}>
                  • {error}
                </Typography>
              ))}
            </Box>
          )}
          
          {syncStatus.warnings.length > 0 && (
            <Box>
              <Typography variant="subtitle2" color="warning.main" gutterBottom>
                Warnings:
              </Typography>
              {syncStatus.warnings.map((warning, index) => (
                <Typography key={index} variant="body2" color="warning.main" sx={{ pl: 2 }}>
                  • {warning}
                </Typography>
              ))}
            </Box>
          )}
        </Box>
      )}
    </Collapse>
  );

  return (
    <Paper 
      elevation={1} 
      sx={{ p: 2 }}
      role="region"
      aria-label="Collection sync status"
    >
      {renderMainStatus()}
      {renderProgress()}
      {!compact && renderQuickStats()}
      {renderDetailedStats()}
    </Paper>
  );
};

export default EnhancedCollectionSyncStatus;