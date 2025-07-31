import React, { useState, useMemo } from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import LoadingSpinner from '../LoadingSpinner';
import Icon from '../ui/Icon';

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
        <div key={node.path}>
          <div
            onClick={() => toggleFolder(node.path)}
            className="group flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
            style={{ paddingLeft }}
          >
            <Icon 
              name="chevronRight" 
              size="sm" 
              className={`mr-2 transition-transform ${
                isExpanded ? 'rotate-90' : ''
              }`}
            />
            <Icon name="folder" size="sm" color="blue" className="mr-2" />
            <span className="text-sm text-gray-900 dark:text-white font-medium">
              {node.name}
            </span>
            {node.children && (
              <span className="ml-auto text-xs text-gray-400 dark:text-gray-500">
                {node.children.filter(child => child.type === 'file').length} files
              </span>
            )}
          </div>
          
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderTreeNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    }

    // File node
    const isSelected = state.editor.filePath === node.path;
    return (
      <div
        key={node.path}
        onClick={() => {
          const pathParts = node.path.split('/');
          const filename = pathParts.pop()!;
          const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
          handleFileClick(filename, folder);
        }}
        className={`group flex items-center justify-between p-2 cursor-pointer transition-colors ${
          isSelected
            ? 'bg-blue-50 dark:bg-blue-900/50 border-r-2 border-blue-500'
            : 'hover:bg-gray-50 dark:hover:bg-gray-700'
        }`}
        style={{ paddingLeft }}
      >
        <div className="flex items-center min-w-0 flex-1">
          <Icon name="document" size="sm" className="mr-2" />
          <div className="min-w-0 flex-1">
            <p className={`text-sm truncate ${
              isSelected
                ? 'text-blue-700 dark:text-blue-300 font-medium'
                : 'text-gray-900 dark:text-white'
            }`}>
              {node.name}
            </p>
            {node.metadata && 'source_url' in node.metadata && node.metadata.source_url && (
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                from {new URL(node.metadata.source_url).hostname}
              </p>
            )}
          </div>
        </div>
        
        {/* Delete button */}
        <button
          onClick={(e) => {
            const pathParts = node.path.split('/');
            const filename = pathParts.pop()!;
            const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
            handleFileDelete(filename, e, folder);
          }}
          className="opacity-0 group-hover:opacity-100 ml-2 p-1 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-all"
          title="Delete file"
        >
          <Icon name="trash" size="xs" color="current" />
        </button>
      </div>
    );
  };

  if (state.ui.loading.files) {
    return (
      <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="p-4">
          <div className="flex items-center justify-center">
            <LoadingSpinner size="sm" />
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading files...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Files & Folders</h3>
          <button
            onClick={() => openModal('newFile')}
            className="inline-flex items-center p-1.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded transition-colors"
            title="New file"
          >
            <Icon name="plus" size="sm" />
          </button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search files..."
            className="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <Icon name="search" size="sm" className="absolute left-2.5 top-2.5" />
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto">
        {filteredTree.length === 0 ? (
          <div className="p-4 text-center">
            {searchTerm ? (
              <div>
                <div className="text-gray-400 dark:text-gray-500 mb-4">
                  <Icon name="search" size="xl" className="mx-auto" />
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">No files match "{searchTerm}"</p>
                <button
                  onClick={() => setSearchTerm('')}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Clear search
                </button>
              </div>
            ) : (
              <div>
                <div className="text-gray-400 dark:text-gray-500 mb-4">
                  <Icon name="document" size="xl" className="mx-auto" />
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">No files in this collection</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">
                  Add pages by crawling URLs or create new files manually
                </p>
                <div className="space-y-2">
                  <button
                    onClick={() => openModal('addPage')}
                    className="block w-full px-3 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                  >
                    Add Page from URL
                  </button>
                  <button
                    onClick={() => openModal('newFile')}
                    className="block w-full px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
                  >
                    Create New File
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="py-2">
            {filteredTree.map(node => renderTreeNode(node))}
          </div>
        )}
      </div>
    </div>
  );
}

export default FileExplorer;