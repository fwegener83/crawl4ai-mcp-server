import React, { useState, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Chip,
} from '../ui';
import { ActionButton, FileUpload } from '../forms';
import { DataTable } from '../ui/DataTable';
import type { Column } from '../ui/DataTable';
import { BreadcrumbNavigation } from '../navigation/BreadcrumbNavigation';
import { useNotification } from '../ui/NotificationProvider';
import StorageIcon from '@mui/icons-material/Storage';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';

export interface CollectionFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: 'file' | 'folder';
  createdAt: Date;
  modifiedAt: Date;
  metadata?: {
    sourceUrl?: string;
    description?: string;
    tags?: string[];
  };
}

export interface CollectionInfo {
  id: string;
  name: string;
  description?: string;
  fileCount: number;
  folderCount: number;
  totalSize: number;
  createdAt: Date;
  modifiedAt: Date;
}

export interface CollectionEditorProps {
  collection: CollectionInfo;
  files: CollectionFile[];
  currentPath?: string;
  loading?: boolean;
  onFileSelect?: (file: CollectionFile) => void;
  onFileDelete?: (fileId: string) => void;
  onFileDownload?: (fileId: string) => void;
  onFileEdit?: (fileId: string) => void;
  onFolderNavigate?: (path: string) => void;
  onFileUpload?: (files: File[], path: string) => void;
}

export const CollectionEditor: React.FC<CollectionEditorProps> = ({
  collection,
  files,
  currentPath = '',
  loading = false,
  onFileSelect,
  onFileDelete,
  onFileDownload,
  onFileEdit,
  onFolderNavigate,
  onFileUpload,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<CollectionFile[]>([]);
  const { showSuccess, showError } = useNotification();

  // Generate breadcrumb items from current path
  const breadcrumbItems = useMemo(() => {
    const items = [{ label: collection.name, path: '' }];
    
    if (currentPath) {
      const pathParts = currentPath.split('/').filter(Boolean);
      let buildPath = '';
      
      pathParts.forEach(part => {
        buildPath += (buildPath ? '/' : '') + part;
        items.push({
          label: part,
          path: buildPath,
          icon: <FolderIcon sx={{ fontSize: 16 }} />
        } as any);
      });
    }
    
    return items;
  }, [collection.name, currentPath]);

  // Table columns configuration
  const columns: Column<CollectionFile>[] = [
    {
      id: 'name',
      label: 'Name',
      sortable: true,
      align: 'left',
      render: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {row.type === 'folder' ? (
            <FolderIcon color="primary" sx={{ fontSize: 20 }} />
          ) : (
            <InsertDriveFileIcon color="action" sx={{ fontSize: 20 }} />
          )}
          <Typography variant="body2" fontWeight="medium">
            {value}
          </Typography>
          {row.metadata?.tags && row.metadata.tags.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {row.metadata.tags.slice(0, 2).map(tag => (
                <Chip key={tag} label={tag} size="small" variant="outlined" />
              ))}
              {row.metadata.tags.length > 2 && (
                <Chip 
                  label={`+${row.metadata.tags.length - 2}`} 
                  size="small" 
                  variant="outlined" 
                />
              )}
            </Box>
          )}
        </Box>
      )
    },
    {
      id: 'size',
      label: 'Size',
      sortable: true,
      align: 'right',
      render: (value) => formatFileSize(value)
    },
    {
      id: 'modifiedAt',
      label: 'Modified',
      sortable: true,
      align: 'right',
      render: (value) => new Date(value).toLocaleDateString()
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (_, row) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="View">
            <IconButton 
              size="small" 
              onClick={() => onFileSelect?.(row)}
            >
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {row.type === 'file' && (
            <>
              <Tooltip title="Edit">
                <IconButton 
                  size="small" 
                  onClick={() => onFileEdit?.(row.id)}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download">
                <IconButton 
                  size="small" 
                  onClick={() => onFileDownload?.(row.id)}
                >
                  <DownloadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
          <Tooltip title="Delete">
            <IconButton 
              size="small" 
              color="error"
              onClick={() => onFileDelete?.(row.id)}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleRowClick = (file: CollectionFile) => {
    if (file.type === 'folder') {
      const newPath = currentPath ? `${currentPath}/${file.name}` : file.name;
      onFolderNavigate?.(newPath);
    } else {
      onFileSelect?.(file);
    }
  };

  const handleFileUpload = (uploadedFiles: File[]) => {
    if (onFileUpload) {
      onFileUpload(uploadedFiles, currentPath);
      showSuccess(`${uploadedFiles.length} file(s) uploaded successfully!`);
    }
  };

  const handleBulkDelete = async () => {
    try {
      for (const file of selectedFiles) {
        await onFileDelete?.(file.id);
      }
      setSelectedFiles([]);
      showSuccess(`${selectedFiles.length} file(s) deleted successfully!`);
    } catch (error) {
      showError('Failed to delete selected files');
    }
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        avatar={<StorageIcon color="primary" />}
        title={
          <Box>
            <Typography variant="h6">{collection.name}</Typography>
            {collection.description && (
              <Typography variant="body2" color="text.secondary">
                {collection.description}
              </Typography>
            )}
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip 
              label={`${collection.fileCount} files`} 
              size="small" 
              variant="outlined" 
            />
            <Chip 
              label={formatFileSize(collection.totalSize)} 
              size="small" 
              variant="outlined" 
            />
          </Box>
        }
      />
      
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
        {/* Breadcrumb Navigation */}
        <Box sx={{ px: 2, py: 1, borderBottom: 1, borderColor: 'divider' }}>
          <BreadcrumbNavigation 
            items={breadcrumbItems}
            onNavigate={onFolderNavigate}
          />
        </Box>

        {/* Toolbar */}
        <Box sx={{ 
          px: 2, 
          py: 1, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: 1, 
          borderColor: 'divider' 
        }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {selectedFiles.length > 0 && (
              <ActionButton
                variant="outlined"
                color="error"
                size="small"
                confirmAction
                confirmText={`Delete ${selectedFiles.length} file(s)?`}
                onConfirm={handleBulkDelete}
                startIcon={<DeleteIcon />}
              >
                Delete Selected ({selectedFiles.length})
              </ActionButton>
            )}
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            {files.length} items
          </Typography>
        </Box>

        {/* File Upload Area */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <FileUpload
            accept=".md,.txt,.json"
            multiple
            onFilesChange={handleFileUpload}
            label="Drop files here or click to upload"
            helperText="Supported formats: .md, .txt, .json"
            maxSize={10 * 1024 * 1024} // 10MB
          />
        </Box>

        {/* Files Table */}
        <Box sx={{ flex: 1 }}>
          <DataTable
            data={files}
            columns={columns}
            loading={loading}
            selectable
            onSelectionChange={setSelectedFiles}
            searchable
            searchPlaceholder="Search files..."
            onRowClick={handleRowClick}
            emptyMessage="No files in this collection"
            dense
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default CollectionEditor;