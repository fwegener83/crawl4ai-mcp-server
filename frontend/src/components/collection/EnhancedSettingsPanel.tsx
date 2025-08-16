import React, { useState, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Alert,
  Collapse,
  Chip,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  TuneRounded as TuneIcon,
  SmartToy as SmartToyIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import type { VectorSyncStatus } from '../../types/api';

interface EnhancedSettings {
  enhancedProcessingEnabled: boolean;
  contextExpansionThreshold: number;
  chunkOverlapPercentage: number;
  chunkingStrategy: string;
  // Advanced settings
  maxContextWindow?: number;
  relationshipSensitivity?: number;
  memoryLimit?: number;
}

interface EnhancedSettingsPanelProps {
  collectionName: string;
  syncStatus: VectorSyncStatus;
  open: boolean;
  onClose: () => void;
  onSettingsChange: (settings: EnhancedSettings) => void;
  onApplySettings: (settings: EnhancedSettings) => void;
  onResetToDefaults: () => void;
  applyingSettings?: boolean;
  settingsError?: string;
}

const DEFAULT_SETTINGS: EnhancedSettings = {
  enhancedProcessingEnabled: true,
  contextExpansionThreshold: 0.75,
  chunkOverlapPercentage: 25,
  chunkingStrategy: 'enhanced_overlap_aware',
  maxContextWindow: 8000,
  relationshipSensitivity: 0.8,
  memoryLimit: 512
};

const CHUNKING_STRATEGIES = [
  { value: 'enhanced_overlap_aware', label: 'Enhanced Overlap-Aware', description: 'Advanced chunking with overlap detection and relationship tracking' },
  { value: 'markdown_intelligent', label: 'Markdown Intelligent', description: 'Header-aware chunking for structured documents' },
  { value: 'baseline', label: 'Baseline', description: 'Standard chunking without enhanced features' }
];

export const EnhancedSettingsPanel: React.FC<EnhancedSettingsPanelProps> = ({
  collectionName,
  syncStatus,
  open,
  onClose,
  onSettingsChange,
  onApplySettings,
  onResetToDefaults,
  applyingSettings = false,
  settingsError
}) => {
  const [settings, setSettings] = useState<EnhancedSettings>(DEFAULT_SETTINGS);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Initialize settings based on sync status
  useEffect(() => {
    const initialSettings: EnhancedSettings = {
      enhancedProcessingEnabled: syncStatus.enhanced_features_enabled ?? false,
      contextExpansionThreshold: 0.75, // Default, could be loaded from backend
      chunkOverlapPercentage: syncStatus.overlap_chunk_count && syncStatus.chunk_count
        ? Math.round((syncStatus.overlap_chunk_count / syncStatus.chunk_count) * 100)
        : 25,
      chunkingStrategy: syncStatus.enhanced_features_enabled ? 'enhanced_overlap_aware' : 'baseline',
      maxContextWindow: 8000,
      relationshipSensitivity: 0.8,
      memoryLimit: 512
    };
    
    setSettings(initialSettings);
  }, [syncStatus]);

  // Calculate performance impact
  const performanceImpact = useMemo(() => {
    const storageIncrease = Math.round(settings.chunkOverlapPercentage * 1.2); // Rough estimate
    const queryLatency = settings.enhancedProcessingEnabled 
      ? Math.round(settings.contextExpansionThreshold * 30) + 10 // ms
      : 0;
    
    return {
      storageIncrease,
      queryLatency,
      memoryUsage: settings.enhancedProcessingEnabled 
        ? Math.round(settings.chunkOverlapPercentage * 2) + 50 // MB estimate
        : 0
    };
  }, [settings]);

  // Current statistics calculations
  const currentStats = useMemo(() => {
    const storageOverhead = syncStatus.overlap_chunk_count && syncStatus.chunk_count
      ? Math.round((syncStatus.overlap_chunk_count / syncStatus.chunk_count) * 100)
      : 0;
    
    const expansionEligible = syncStatus.context_expansion_eligible_chunks && syncStatus.chunk_count
      ? Math.round((syncStatus.context_expansion_eligible_chunks / syncStatus.chunk_count) * 100)
      : 0;

    return { storageOverhead, expansionEligible };
  }, [syncStatus]);

  const updateSettings = (key: keyof EnhancedSettings, value: any) => {
    const newSettings = { ...settings, [key]: value };
    
    // Validate the new value
    const errors = { ...validationErrors };
    
    if (key === 'contextExpansionThreshold') {
      if (value < 0 || value > 1) {
        errors[key] = 'Threshold must be between 0.0 and 1.0';
      } else if (isNaN(value)) {
        errors[key] = 'Please enter a valid number';
      } else {
        delete errors[key];
      }
    }
    
    if (key === 'chunkOverlapPercentage') {
      if (value > 50) {
        errors[key] = 'Warning: High overlap may significantly increase storage requirements';
      } else {
        delete errors[key];
      }
    }

    setValidationErrors(errors);
    setSettings(newSettings);
    setHasUnsavedChanges(true);
    onSettingsChange(newSettings);
  };

  const handleApplySettings = () => {
    if (Object.keys(validationErrors).length === 0) {
      onApplySettings(settings);
      setHasUnsavedChanges(false);
    }
  };

  const handleResetToDefaults = () => {
    setSettings(DEFAULT_SETTINGS);
    setValidationErrors({});
    setHasUnsavedChanges(false);
    onResetToDefaults();
  };

  const renderMainSettings = () => (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TimelineIcon />
        Enhanced RAG Configuration
      </Typography>

      {/* Enhanced Processing Toggle */}
      <FormControlLabel
        control={
          <Switch
            checked={settings.enhancedProcessingEnabled}
            onChange={(e) => updateSettings('enhancedProcessingEnabled', e.target.checked)}
          />
        }
        label="Enable Enhanced Processing"
        sx={{ mb: 2 }}
      />

      {/* Context Expansion Settings */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Context Expansion Settings
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Context expansion uses similarity thresholds to include related chunks in search results.
        </Typography>
        
        <TextField
          label="Context Expansion Threshold"
          type="number"
          value={settings.contextExpansionThreshold}
          onChange={(e) => updateSettings('contextExpansionThreshold', parseFloat(e.target.value))}
          inputProps={{ 
            min: 0, 
            max: 1, 
            step: 0.05,
            'aria-label': 'Context expansion similarity threshold'
          }}
          error={!!validationErrors.contextExpansionThreshold}
          helperText={validationErrors.contextExpansionThreshold || 'Higher values = more selective context expansion'}
          disabled={!settings.enhancedProcessingEnabled}
          size="small"
          sx={{ mb: 2, width: '100%' }}
        />
      </Box>

      {/* Chunk Overlap Settings */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Chunk Overlap Settings
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Chunk overlap creates redundancy between adjacent chunks for better context continuity.
        </Typography>
        
        <Typography variant="body2" gutterBottom>
          Chunk Overlap Percentage: {settings.chunkOverlapPercentage}%
        </Typography>
        <Slider
          value={settings.chunkOverlapPercentage}
          onChange={(_event, value) => updateSettings('chunkOverlapPercentage', value)}
          min={0}
          max={60}
          step={5}
          marks={[
            { value: 0, label: '0%' },
            { value: 25, label: '25%' },
            { value: 50, label: '50%' }
          ]}
          disabled={!settings.enhancedProcessingEnabled}
          aria-label="Chunk overlap percentage"
          sx={{ mb: 1 }}
        />
        {validationErrors.chunkOverlapPercentage && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            {validationErrors.chunkOverlapPercentage}
          </Alert>
        )}
      </Box>

      {/* Chunking Strategy */}
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth size="small">
          <InputLabel>Chunking Strategy</InputLabel>
          <Select
            value={settings.chunkingStrategy}
            onChange={(e) => updateSettings('chunkingStrategy', e.target.value)}
            label="Chunking Strategy"
            inputProps={{ 'aria-label': 'Chunking strategy' }}
          >
            {CHUNKING_STRATEGIES.map((strategy) => (
              <MenuItem key={strategy.value} value={strategy.value}>
                <Box>
                  <Typography variant="body1">{strategy.label}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {strategy.description}
                  </Typography>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    </Box>
  );

  const renderAdvancedSettings = () => (
    <Collapse in={showAdvanced}>
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Advanced Configuration
        </Typography>

        <Box sx={{ mb: 2 }}>
          <TextField
            label="Maximum Context Window"
            type="number"
            value={settings.maxContextWindow}
            onChange={(e) => updateSettings('maxContextWindow', parseInt(e.target.value))}
            inputProps={{ 
              min: 1000, 
              max: 32000, 
              step: 1000,
              'aria-label': 'Maximum context window size'
            }}
            helperText="Maximum tokens for context expansion (1000-32000)"
            disabled={!settings.enhancedProcessingEnabled}
            size="small"
            fullWidth
            sx={{ mb: 2 }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>
            Relationship Detection Sensitivity: {settings.relationshipSensitivity}
          </Typography>
          <Slider
            value={settings.relationshipSensitivity}
            onChange={(_event, value) => updateSettings('relationshipSensitivity', value)}
            min={0.1}
            max={1.0}
            step={0.1}
            disabled={!settings.enhancedProcessingEnabled}
            aria-label="Relationship detection sensitivity"
            sx={{ mb: 1 }}
          />
          <Typography variant="caption" color="textSecondary">
            Higher values detect more relationships between chunks
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <TextField
            label="Memory Usage Limit (MB)"
            type="number"
            value={settings.memoryLimit}
            onChange={(e) => updateSettings('memoryLimit', parseInt(e.target.value))}
            inputProps={{ 
              min: 128, 
              max: 2048, 
              step: 64,
              'aria-label': 'Memory usage limit (MB)'
            }}
            helperText="Maximum memory for enhanced processing (128-2048 MB)"
            disabled={!settings.enhancedProcessingEnabled}
            size="small"
            fullWidth
          />
        </Box>
      </Box>
    </Collapse>
  );

  const renderCurrentStatistics = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="subtitle1" gutterBottom>
          Collection: {collectionName}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Typography variant="body2">
            Enhanced Features Status:
          </Typography>
          <Chip
            size="small"
            label={syncStatus.enhanced_features_enabled ? 'Active' : 'Inactive'}
            color={syncStatus.enhanced_features_enabled ? 'success' : 'default'}
            icon={<SmartToyIcon />}
          />
        </Box>

        {syncStatus.enhanced_features_enabled ? (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Statistics
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Typography variant="body2">
                Total Chunks: {syncStatus.chunk_count}
              </Typography>
              <Typography variant="body2">
                Overlap Chunks: {syncStatus.overlap_chunk_count || 0}
              </Typography>
              <Typography variant="body2">
                Expandable Chunks: {syncStatus.context_expansion_eligible_chunks || 0}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Storage Overhead: {currentStats.storageOverhead}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Expansion Eligible: {currentStats.expansionEligible}%
              </Typography>
            </Box>
          </Box>
        ) : (
          <Alert severity="info" sx={{ mb: 2 }}>
            Enable enhanced processing to access advanced features
          </Alert>
        )}

        {/* Current Enhanced Statistics */}
        <Typography variant="subtitle2" gutterBottom>
          Current Enhanced Statistics
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="body2">
            Storage Overhead: {currentStats.storageOverhead}%
          </Typography>
          <Typography variant="body2">
            Expansion Eligible: {currentStats.expansionEligible}%
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  const renderPerformanceImpact = () => (
    settings.enhancedProcessingEnabled && (
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Performance Impact:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="body2">
            Storage increase: ~{performanceImpact.storageIncrease}%
          </Typography>
          <Typography variant="body2">
            Query latency: +{performanceImpact.queryLatency}ms
          </Typography>
          <Typography variant="body2">
            Memory usage: ~{performanceImpact.memoryUsage}MB
          </Typography>
        </Box>
      </Alert>
    )
  );

  const renderUnsavedChanges = () => (
    hasUnsavedChanges && (
      <Alert severity="warning" icon={<InfoIcon />} sx={{ mb: 2 }}>
        <Typography variant="body2">
          <strong>Unsaved Changes</strong> - Apply settings to save your changes
        </Typography>
      </Alert>
    )
  );

  const renderErrorAlert = () => (
    settingsError && (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Typography variant="subtitle2">Settings Error</Typography>
        <Typography variant="body2">{settingsError}</Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
          <Button size="small" variant="outlined" onClick={handleApplySettings}>
            Try Again
          </Button>
          <Button size="small" variant="text" onClick={handleResetToDefaults}>
            Use Defaults
          </Button>
        </Box>
      </Alert>
    )
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '600px' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SettingsIcon />
        Enhanced RAG Settings
      </DialogTitle>

      <DialogContent>
        {renderErrorAlert()}
        {renderUnsavedChanges()}
        {renderCurrentStatistics()}
        {renderPerformanceImpact()}
        {renderMainSettings()}

        {/* Advanced Settings Toggle */}
        <Button
          onClick={() => setShowAdvanced(!showAdvanced)}
          startIcon={<TuneIcon />}
          endIcon={
            <ExpandMoreIcon
              sx={{
                transform: showAdvanced ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s ease'
              }}
            />
          }
          sx={{ mb: 2 }}
        >
          Advanced Settings
        </Button>

        {renderAdvancedSettings()}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={handleResetToDefaults}
          startIcon={<RefreshIcon />}
          disabled={applyingSettings}
        >
          Reset to Defaults
        </Button>
        
        <Box sx={{ flex: 1 }} />
        
        <Button
          onClick={onClose}
          disabled={applyingSettings}
        >
          Cancel
        </Button>
        
        <Button
          onClick={handleApplySettings}
          variant="contained"
          startIcon={applyingSettings ? <CircularProgress size={16} /> : <SaveIcon />}
          disabled={applyingSettings || Object.keys(validationErrors).length > 0}
        >
          {applyingSettings ? 'Applying...' : 'Apply Settings'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EnhancedSettingsPanel;