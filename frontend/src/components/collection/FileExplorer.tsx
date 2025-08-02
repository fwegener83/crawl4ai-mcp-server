import React, { useState, useMemo } from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  IconButton, 
  Paper, 
  CircularProgress,
  Tooltip
} from '../ui';
import { InputAdornment } from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import DeleteIcon from '@mui/icons-material/Delete';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';

interface FileExplorerProps {
  className?: string;
}

// Types for file tree structure
interface TreeNode {
  name: string;
  path: string;
  type: 'folder' | 'file';
  children?: TreeNode[];
  metadata?: unknown;
  expanded?: boolean;
}

export function FileExplorer({ className = '' }: FileExplorerProps) {
  const { state, openFile, openDeleteConfirmation, openModal } = useCollectionOperations();
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  const handleFileClick = (filename: string, folder?: string) => {
    if (state.selectedCollection) {
      openFile(state.selectedCollection, filename, folder);
    }
  };

  const handleFileDelete = (filename: string, e: React.MouseEvent, folder?: string) => {
    e.stopPropagation();
    const filePath = folder ? `${folder}/${filename}` : filename;
    openDeleteConfirmation('file', filePath);
  };

  const toggleFolder = (folderPath: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath);
    } else {
      newExpanded.add(folderPath);
    }
    setExpandedFolders(newExpanded);
  };

  // Build file tree from flat file structure
  const fileTree = useMemo(() => {
    const tree: TreeNode[] = [];
    const folderMap = new Map<string, TreeNode>();

    // Add all files to the tree
    state.files.forEach(file => {
      const pathParts = file.path.split('/');
      const fileName = pathParts[pathParts.length - 1];
      
      if (pathParts.length === 1) {
        // File in root directory
        tree.push({
          name: fileName,
          path: file.path,
          type: 'file',
          metadata: file.metadata,
        });
      } else {
        // File in nested folders
        let currentPath = '';
        let currentLevel = tree;
        
        // Create/find folder structure
        for (let i = 0; i < pathParts.length - 1; i++) {
          const folderName = pathParts[i];
          currentPath = currentPath ? `${currentPath}/${folderName}` : folderName;
          
          let folder = folderMap.get(currentPath);
          if (!folder) {
            folder = {
              name: folderName,
              path: currentPath,
              type: 'folder',
              children: [],
              expanded: expandedFolders.has(currentPath),
            };
            folderMap.set(currentPath, folder);
            currentLevel.push(folder);
          }
          
          currentLevel = folder.children!;
        }
        
        // Add file to the deepest folder
        currentLevel.push({
          name: fileName,
          path: file.path,
          type: 'file',
          metadata: file.metadata,
        });
      }
    });

    // Sort tree: folders first, then files, alphabetically
    const sortTree = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.sort((a, b) => {
        if (a.type !== b.type) {
          return a.type === 'folder' ? -1 : 1;
        }
        return a.name.localeCompare(b.name);
      }).map(node => ({
        ...node,
        children: node.children ? sortTree(node.children) : undefined,
      }));
    };

    return sortTree(tree);
  }, [state.files, expandedFolders]);

  // Filter tree based on search term
  const filteredTree = useMemo(() => {
    if (!searchTerm) return fileTree;
    
    const filterTree = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.reduce((acc: TreeNode[], node) => {
        if (node.type === 'file') {
          if (node.name.toLowerCase().includes(searchTerm.toLowerCase())) {
            acc.push(node);
          }
        } else {
          const filteredChildren = node.children ? filterTree(node.children) : [];
          if (filteredChildren.length > 0 || node.name.toLowerCase().includes(searchTerm.toLowerCase())) {
            acc.push({
              ...node,
              children: filteredChildren,
              expanded: true, // Auto-expand folders in search results
            });
          }
        }
        return acc;
      }, []);
    };

    return filterTree(fileTree);
  }, [fileTree, searchTerm]);

  // Render tree node recursively
  const renderTreeNode = (node: TreeNode, depth = 0): React.ReactNode => {
    const isExpanded = expandedFolders.has(node.path) || (searchTerm && node.type === 'folder');
    const paddingLeft = depth * 20 + 8;

    if (node.type === 'folder') {
      return (
        <Box key={node.path}>
          <Box
            onClick={() => toggleFolder(node.path)}
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 1,
              pl: `${paddingLeft}px`,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover'
              },
              transition: 'background-color 0.2s'
            }}
          >
            <ChevronRightIcon 
              fontSize="small"
              sx={{ 
                mr: 1, 
                transition: 'transform 0.2s',
                transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)'
              }}
            />
            <FolderIcon 
              fontSize="small" 
              color="primary" 
              sx={{ mr: 1 }} 
            />
            <Typography variant="body2" fontWeight="medium" sx={{ flex: 1 }}>
              {node.name}
            </Typography>
            {node.children && (
              <Typography variant="caption" color="text.secondary">
                {node.children.filter(child => child.type === 'file').length} files
              </Typography>
            )}
          </Box>
          
          {isExpanded && node.children && (
            <Box>
              {node.children.map(child => renderTreeNode(child, depth + 1))}
            </Box>
          )}
        </Box>
      );
    }

    // File node
    const isSelected = state.editor.filePath === node.path;
    return (
      <Box
        key={node.path}
        onClick={() => {
          const pathParts = node.path.split('/');
          const filename = pathParts.pop()!;
          const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
          handleFileClick(filename, folder);
        }}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 1,
          pl: `${paddingLeft}px`,
          cursor: 'pointer',
          borderRight: isSelected ? 2 : 0,
          borderColor: isSelected ? 'primary.main' : 'transparent',
          bgcolor: isSelected ? 'primary.50' : 'transparent',
          '&:hover': {
            bgcolor: isSelected ? 'primary.100' : 'action.hover',
            '& .delete-button': {
              opacity: 1
            }
          },
          transition: 'all 0.2s'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 0, flex: 1 }}>
          <DescriptionIcon 
            fontSize="small" 
            sx={{ mr: 1, color: isSelected ? 'primary.main' : 'action.active' }} 
          />
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography 
              variant="body2" 
              sx={{
                fontWeight: isSelected ? 'medium' : 'normal',
                color: isSelected ? 'primary.main' : 'text.primary',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {node.name}
            </Typography>
            {node.metadata && typeof node.metadata === 'object' && 'source_url' in node.metadata && 
             typeof (node.metadata as any).source_url === 'string' && (node.metadata as any).source_url && (
              <Typography 
                variant="caption" 
                color="text.secondary"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  display: 'block'
                }}
              >
                from {new URL((node.metadata as any).source_url).hostname}
              </Typography>
            )}
          </Box>
        </Box>
        
        {/* Delete button */}
        <Tooltip title="Delete file">
          <IconButton
            className="delete-button"
            onClick={(e) => {
              const pathParts = node.path.split('/');
              const filename = pathParts.pop()!;
              const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
              handleFileDelete(filename, e, folder);
            }}
            size="small"
            color="error"
            sx={{ 
              opacity: 0, 
              transition: 'opacity 0.2s',
              ml: 1
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    );
  };

  if (state.ui.loading.files) {
    return (
      <Paper 
        elevation={0} 
        sx={{ 
          borderRight: 1, 
          borderColor: 'divider',
          borderRadius: 0
        }} 
        className={className}
      >
        <Box sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Loading files...
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        borderRight: 1, 
        borderColor: 'divider',
        borderRadius: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }} 
      className={className}
    >
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="semibold">
            Files & Folders
          </Typography>
          <Tooltip title="New file">
            <IconButton
              onClick={() => openModal('newFile')}
              size="small"
              color="primary"
            >
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* Search */}
        <TextField
          size="small"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search files..."
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* File Tree */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {filteredTree.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            {searchTerm ? (
              <Box>
                <SearchIcon 
                  sx={{ 
                    fontSize: 48, 
                    color: 'text.secondary',
                    mb: 2,
                    display: 'block',
                    mx: 'auto'
                  }} 
                />
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  No files match "{searchTerm}"
                </Typography>
                <Button
                  onClick={() => setSearchTerm('')}
                  size="small"
                  variant="text"
                >
                  Clear search
                </Button>
              </Box>
            ) : (
              <Box>
                <CreateNewFolderIcon 
                  sx={{ 
                    fontSize: 48, 
                    color: 'text.secondary',
                    mb: 2,
                    display: 'block',
                    mx: 'auto'
                  }} 
                />
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  No files in this collection
                </Typography>
                <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mb: 3 }}>
                  Add pages by crawling URLs or create new files manually
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    onClick={() => openModal('addPage')}
                    variant="contained"
                    color="success"
                    size="small"
                    startIcon={<WebIcon />}
                    fullWidth
                  >
                    Add Page from URL
                  </Button>
                  <Button
                    onClick={() => openModal('newFile')}
                    variant="outlined"
                    size="small"
                    startIcon={<DescriptionIcon />}
                    fullWidth
                  >
                    Create New File
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        ) : (
          <Box sx={{ py: 1 }}>
            {filteredTree.map(node => renderTreeNode(node))}
          </Box>
        )}
      </Box>
    </Paper>
  );
}

export default FileExplorer;