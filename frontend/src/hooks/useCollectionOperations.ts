import { useCallback } from 'react';
import { useCollection } from '../contexts/CollectionContext';
import { APIService } from '../services/api';
import type { 
  CreateCollectionRequest, 
  SaveFileRequest, 
  UpdateFileRequest,
  CrawlToCollectionRequest,
  CrawlResult
} from '../types/api';
import type { FileNode, FolderNode } from '../contexts/CollectionContext';

export function useCollectionOperations() {
  const { state, dispatch } = useCollection();

  // Collection operations
  const loadCollections = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'collections', value: true } });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const collections = await APIService.listFileCollections();
      dispatch({ type: 'SET_COLLECTIONS', payload: collections });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load collections';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'collections', value: false } });
    }
  }, [dispatch]);

  const createCollection = useCallback(async (request: CreateCollectionRequest) => {
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const newCollection = await APIService.createFileCollection(request);
      dispatch({ type: 'ADD_COLLECTION', payload: newCollection });
      dispatch({ type: 'CLOSE_MODAL', payload: 'newCollection' });
      return newCollection;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create collection';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, [dispatch]);

  const deleteCollection = useCallback(async (collectionId: string) => {
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      await APIService.deleteFileCollection(collectionId);
      dispatch({ type: 'REMOVE_COLLECTION', payload: collectionId });
      dispatch({ type: 'CLOSE_DELETE_CONFIRMATION' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete collection';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, [dispatch]);

  const selectCollection = useCallback(async (collectionId: string | null) => {
    dispatch({ type: 'SELECT_COLLECTION', payload: collectionId });
    
    if (collectionId) {
      // Load files for the selected collection
      dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: true } });
      
      try {
        const [, fileList] = await Promise.all([
          APIService.getFileCollection(collectionId),
          APIService.listFilesInCollection(collectionId)
        ]);
        
        // Convert file listing to FileNode and FolderNode structures
        const files: FileNode[] = fileList.files.map(file => ({
          name: file.name,
          path: file.path,
          type: 'file' as const,
          metadata: {
            filename: file.name,
            folder_path: file.folder || '',
            created_at: file.created_at,
            size: file.size,
            source_url: file.source_url || undefined
          }
        }));
        
        const folders: FolderNode[] = fileList.folders.map(folder => ({
          name: folder.name,
          path: folder.path,
          type: 'folder' as const,
          children: []
        }));
        
        dispatch({ type: 'SET_FILES', payload: { files, folders } });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load collection files';
        dispatch({ type: 'SET_ERROR', payload: errorMessage });
      } finally {
        dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: false } });
      }
    }
  }, [dispatch]);

  // File operations
  const saveFile = useCallback(async (collectionId: string, request: SaveFileRequest) => {
    dispatch({ type: 'SET_SAVING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const fileMetadata = await APIService.saveFileToCollection(collectionId, request);
      
      const newFile: FileNode = {
        name: request.filename,
        path: request.folder ? `${request.folder}/${request.filename}` : request.filename,
        type: 'file',
        metadata: fileMetadata,
      };
      
      dispatch({ type: 'ADD_FILE', payload: newFile });
      dispatch({ type: 'CLOSE_MODAL', payload: 'newFile' });
      
      return fileMetadata;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save file';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_SAVING', payload: false });
    }
  }, [dispatch]);

  const openFile = useCallback(async (collectionId: string, filename: string, folder?: string) => {
    const filePath = folder ? `${folder}/${filename}` : filename;
    
    // Check if we're already opening this file
    if (state.editor.filePath === filePath && !state.ui.loading.files) {
      return; // Already open
    }
    
    // Always immediately update the editor to show we're switching files
    dispatch({ type: 'OPEN_FILE', payload: { path: filePath, content: '' } });
    dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: true } });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const content = await APIService.readFileFromCollection(collectionId, filename, folder);
      
      // Update with the actual content
      dispatch({ type: 'OPEN_FILE', payload: { path: filePath, content } });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to open file';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: false } });
    }
  }, [dispatch, state.editor.filePath, state.ui.loading.files]);

  const saveCurrentFile = useCallback(async (collectionId: string) => {
    if (!state.editor.filePath || !state.editor.modified) {
      return;
    }

    dispatch({ type: 'SET_SAVING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const pathParts = state.editor.filePath.split('/');
      const filename = pathParts.pop()!;
      const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
      
      const request: UpdateFileRequest = {
        content: state.editor.content,
      };
      
      await APIService.updateFileInCollection(collectionId, filename, request, folder);
      dispatch({ type: 'SAVE_SUCCESS', payload: state.editor.content });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save file';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_SAVING', payload: false });
    }
  }, [state.editor, dispatch]);

  const deleteFile = useCallback(async (collectionId: string, filename: string, folder?: string) => {
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      await APIService.deleteFileFromCollection(collectionId, filename, folder);
      const filePath = folder ? `${folder}/${filename}` : filename;
      dispatch({ type: 'REMOVE_FILE', payload: filePath });
      dispatch({ type: 'CLOSE_DELETE_CONFIRMATION' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete file';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, [dispatch]);

  const updateContent = useCallback((content: string) => {
    dispatch({ type: 'UPDATE_CONTENT', payload: content });
  }, [dispatch]);

  const closeFile = useCallback(() => {
    dispatch({ type: 'CLOSE_FILE' });
  }, [dispatch]);

  // Crawl operations
  const crawlPageToCollection = useCallback(async (collectionId: string, request: CrawlToCollectionRequest) => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'crawling', value: true } });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const result = await APIService.crawlPageToCollection(collectionId, request);
      
      // Add the new file to the state if crawl was successful
      if (result.filename) {
        const newFile: FileNode = {
          name: result.filename,
          path: result.folder ? `${result.folder}/${result.filename}` : result.filename,
          type: 'file',
          metadata: {
            filename: result.filename,
            folder_path: result.folder || '',
            created_at: new Date().toISOString(),
            source_url: result.url,
            size: result.content_length || 0,
          },
        };
        
        dispatch({ type: 'ADD_FILE', payload: newFile });
      }
      
      dispatch({ type: 'CLOSE_MODAL', payload: 'addPage' });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to crawl page';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'crawling', value: false } });
    }
  }, [dispatch]);

  // Add page to collection (wrapper for crawlPageToCollection)
  const addPageToCollection = useCallback(async (collectionId: string, url: string, folder?: string) => {
    return await crawlPageToCollection(collectionId, { url, folder });
  }, [crawlPageToCollection]);

  // Add multiple pages to collection from crawl results
  const addMultiplePagesToCollection = useCallback(async (
    collectionId: string, 
    crawlResults: CrawlResult[], 
    folder?: string
  ) => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'crawling', value: true } });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    let savedCount = 0;
    const errors: string[] = [];
    const totalSuccessful = crawlResults.filter(r => r.success).length;
    
    console.log(`Starting to save ${totalSuccessful} successful results out of ${crawlResults.length} total results to collection: ${collectionId}`);
    
    try {
      for (const result of crawlResults) {
        if (!result.success) continue;
        
        try {
          // Create content with metadata similar to BulkSaveModal
          const contentWithMetadata = `# ${result.title || 'Untitled Page'}

**URL:** ${result.url}  
**Crawled:** ${new Date(result.metadata.crawl_time).toLocaleString()}  
**Depth:** ${result.depth}  
${result.metadata.score > 0 ? `**Score:** ${result.metadata.score.toFixed(1)}  ` : ''}

---

${result.content}`;

          // Create unique filename to prevent collisions
          const baseFilename = result.title || 'untitled';
          const safeFilename = baseFilename.replace(/[<>:"/\\|?*]/g, '-'); // Sanitize filename
          const timestamp = new Date().getTime();
          const filename = `${safeFilename}-${timestamp}.md`;

          console.log(`Saving page ${savedCount + 1}/${crawlResults.filter(r => r.success).length}: "${filename}"`);

          await APIService.saveFileToCollection(collectionId, {
            filename: filename,
            content: contentWithMetadata,
            folder: folder
          });
          
          savedCount++;
          console.log(`Successfully saved: "${filename}"`);
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Unknown error';
          errors.push(`Failed to save "${result.title || result.url}": ${errorMsg}`);
        }
      }
      
      // Refresh collections and reload files for current collection to show new content
      await loadCollections();
      if (collectionId === state.selectedCollection) {
        console.log(`Reloading files for collection: ${collectionId}`);
        // Manually reload files without using selectCollection to avoid dependency loop
        dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: true } });
        try {
          const fileList = await APIService.listFilesInCollection(collectionId);
          const files: FileNode[] = fileList.files.map(file => ({
            name: file.name,
            path: file.path,
            type: 'file' as const,
            metadata: {
              filename: file.name,
              folder_path: file.folder || '',
              created_at: file.created_at,
              size: file.size,
              source_url: file.source_url || undefined
            }
          }));
          
          const folders: FolderNode[] = fileList.folders.map(folder => ({
            name: folder.name,
            path: folder.path,
            type: 'folder' as const,
            children: []
          }));
          
          dispatch({ type: 'SET_FILES', payload: { files, folders } });
          console.log(`Successfully reloaded ${files.length} files and ${folders.length} folders`);
        } catch (reloadError) {
          console.error('Failed to reload files:', reloadError);
        } finally {
          dispatch({ type: 'SET_LOADING', payload: { key: 'files', value: false } });
        }
      }
      
      console.log(`Completed saving: ${savedCount} successful, ${errors.length} errors`);
      
      if (errors.length > 0) {
        console.warn('Errors encountered:', errors);
        dispatch({ type: 'SET_ERROR', payload: `Saved ${savedCount} pages. ${errors.length} errors: ${errors.join(', ')}` });
      }
      
      return { savedCount, errors };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save pages to collection';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'crawling', value: false } });
    }
  }, [dispatch, loadCollections, state.selectedCollection]);

  // Create new file
  const createNewFile = useCallback(async (collectionId: string, filename: string, content: string, folder?: string) => {
    const result = await saveFile(collectionId, { filename, content, folder });
    return result;
  }, [saveFile]);

  // Modal operations
  const openModal = useCallback((modalName: keyof typeof state.ui.modals) => {
    dispatch({ type: 'OPEN_MODAL', payload: modalName });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch]);

  const closeModal = useCallback((modalName: keyof typeof state.ui.modals) => {
    dispatch({ type: 'CLOSE_MODAL', payload: modalName });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch]);

  const openDeleteConfirmation = useCallback((type: 'collection' | 'file', target: string) => {
    dispatch({ type: 'OPEN_DELETE_CONFIRMATION', payload: { type, target } });
  }, [dispatch]);

  const closeDeleteConfirmation = useCallback(() => {
    dispatch({ type: 'CLOSE_DELETE_CONFIRMATION' });
  }, [dispatch]);

  const clearError = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, [dispatch]);

  return {
    // State
    state,
    
    // Collection operations
    loadCollections,
    createCollection,
    deleteCollection,
    selectCollection,
    
    // File operations
    saveFile,
    openFile,
    saveCurrentFile,
    deleteFile,
    updateContent,
    closeFile,
    
    // Crawl operations
    crawlPageToCollection,
    addPageToCollection,
    addMultiplePagesToCollection,
    createNewFile,
    
    // Modal operations
    openModal,
    closeModal,
    openDeleteConfirmation,
    closeDeleteConfirmation,
    
    // Utility
    clearError,
  };
}

export default useCollectionOperations;