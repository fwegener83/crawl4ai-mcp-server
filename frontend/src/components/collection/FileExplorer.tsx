import React, { useState, useMemo } from 'react';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import LoadingSpinner from '../LoadingSpinner';

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
            <svg
              className={`flex-shrink-0 h-4 w-4 text-gray-400 mr-2 transition-transform ${
                isExpanded ? 'rotate-90' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <svg className="flex-shrink-0 h-4 w-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
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
          <svg className="flex-shrink-0 h-4 w-4 text-gray-400 dark:text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div className="min-w-0 flex-1">
            <p className={`text-sm truncate ${
              isSelected
                ? 'text-blue-700 dark:text-blue-300 font-medium'
                : 'text-gray-900 dark:text-white'
            }`}>
              {node.name}
            </p>
            {node.metadata?.source_url && (
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
          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
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
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
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
          <svg className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto">
        {filteredTree.length === 0 ? (
          <div className="p-4 text-center">
            {searchTerm ? (
              <div>
                <div className="text-gray-400 dark:text-gray-500 mb-4">
                  <svg className="mx-auto h-8 w-8 text-gray-400 flex-shrink-0" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
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
                  <svg className="mx-auto h-8 w-8 text-gray-400 flex-shrink-0" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
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