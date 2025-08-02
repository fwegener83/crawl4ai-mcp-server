import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  IconButton,
  Chip,
  Divider,
  Tabs,
  Tab
} from '../ui';
import { ActionButton } from '../forms';
import CloseIcon from '@mui/icons-material/Close';
import DownloadIcon from '@mui/icons-material/Download';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CodeIcon from '@mui/icons-material/Code';

export interface ContentItem {
  id: string;
  name: string;
  content: string;
  type: string;
  size: number;
  createdAt: Date;
  modifiedAt: Date;
  metadata?: {
    sourceUrl?: string;
    description?: string;
    tags?: string[];
  };
}

export interface ContentViewerDialogProps {
  open: boolean;
  content: ContentItem | null;
  onClose: () => void;
  onEdit?: (contentId: string) => void;
  onDownload?: (contentId: string) => void;
  maxHeight?: string | number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`content-tabpanel-${index}`}
    aria-labelledby={`content-tab-${index}`}
  >
    {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
  </div>
);

export const ContentViewerDialog: React.FC<ContentViewerDialogProps> = ({
  open,
  content,
  onClose,
  onEdit,
  onDownload,
  maxHeight = '80vh',
}) => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const isMarkdown = content?.type === 'markdown' || content?.name.endsWith('.md');
  const isCode = content?.type === 'code' || content?.name.match(/\.(js|ts|jsx|tsx|py|css|html|json)$/);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: maxHeight, maxHeight }
      }}
      aria-labelledby="content-viewer-dialog-title"
    >
      <DialogTitle
        id="content-viewer-dialog-title"
        sx={{ pb: 1 }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, minWidth: 0 }}>
            <VisibilityIcon color="primary" />
            <Box sx={{ minWidth: 0, flex: 1 }}>
              <Typography
                variant="h6"
                component="div"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {content?.name || 'Content Viewer'}
              </Typography>
              {content && (
                <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                  <Chip
                    label={formatFileSize(content.size)}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={new Date(content.modifiedAt).toLocaleDateString()}
                    size="small"
                    variant="outlined"
                  />
                  {content.metadata?.tags && content.metadata.tags.map(tag => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', flex: 1 }}>
        {content && (
          <>
            {/* Content metadata and source info */}
            {(content.metadata?.sourceUrl || content.metadata?.description) && (
              <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
                {content.metadata.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {content.metadata.description}
                  </Typography>
                )}
                {content.metadata.sourceUrl && (
                  <Typography variant="caption" color="text.secondary">
                    Source: {content.metadata.sourceUrl}
                  </Typography>
                )}
              </Box>
            )}

            {/* Tabs for different view modes */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={currentTab} onChange={handleTabChange}>
                <Tab label="Preview" icon={<VisibilityIcon />} />
                <Tab label="Raw Content" icon={<CodeIcon />} />
              </Tabs>
            </Box>

            {/* Content display */}
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              <TabPanel value={currentTab} index={0}>
                <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  {isMarkdown ? (
                    <Box
                      sx={{
                        '& h1, & h2, & h3, & h4, & h5, & h6': {
                          mt: 2,
                          mb: 1,
                          fontWeight: 'bold',
                        },
                        '& p': { mb: 1, lineHeight: 1.6 },
                        '& pre': {
                          backgroundColor: 'grey.100',
                          p: 2,
                          borderRadius: 1,
                          overflow: 'auto',
                          fontSize: '0.875rem',
                        },
                        '& code': {
                          backgroundColor: 'grey.100',
                          px: 0.5,
                          py: 0.25,
                          borderRadius: 0.5,
                          fontSize: '0.875rem',
                        },
                        '& blockquote': {
                          borderLeft: 4,
                          borderColor: 'primary.main',
                          pl: 2,
                          ml: 0,
                          fontStyle: 'italic',
                        },
                      }}
                    >
                      <Typography
                        component="div"
                        variant="body1"
                        sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                      >
                        {content.content}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography
                      component="pre"
                      variant="body2"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        fontFamily: isCode ? 'monospace' : 'inherit',
                        fontSize: isCode ? '0.875rem' : 'inherit',
                        backgroundColor: isCode ? 'grey.50' : 'transparent',
                        p: isCode ? 2 : 0,
                        borderRadius: isCode ? 1 : 0,
                        border: isCode ? 1 : 0,
                        borderColor: isCode ? 'divider' : 'transparent',
                        overflow: 'auto',
                      }}
                    >
                      {content.content}
                    </Typography>
                  )}
                </Box>
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  <Typography
                    component="pre"
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                      backgroundColor: 'grey.50',
                      p: 2,
                      borderRadius: 1,
                      border: 1,
                      borderColor: 'divider',
                      overflow: 'auto',
                    }}
                  >
                    {content.content}
                  </Typography>
                </Box>
              </TabPanel>
            </Box>
          </>
        )}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 2, gap: 1 }}>
        {content && onDownload && (
          <ActionButton
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => onDownload(content.id)}
          >
            Download
          </ActionButton>
        )}
        {content && onEdit && (
          <ActionButton
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => onEdit(content.id)}
          >
            Edit
          </ActionButton>
        )}
        <ActionButton variant="contained" onClick={onClose}>
          Close
        </ActionButton>
      </DialogActions>
    </Dialog>
  );
};

export default ContentViewerDialog;