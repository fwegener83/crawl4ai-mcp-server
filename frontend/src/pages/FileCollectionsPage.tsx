import { Box } from '../components/ui';
import { CollectionProvider } from '../contexts/CollectionContext';
import CollectionSidebar from '../components/collection/CollectionSidebar';
import MainContent from '../components/collection/MainContent';
import NewCollectionModal from '../components/collection/modals/NewCollectionModal';
import AddPageModal from '../components/collection/modals/AddPageModal';
import AddMultiplePagesModal from '../components/collection/modals/AddMultiplePagesModal';
import NewFileModal from '../components/collection/modals/NewFileModal';
import DeleteConfirmationModal from '../components/collection/modals/DeleteConfirmationModal';

export function FileCollectionsPage() {
  return (
    <CollectionProvider>
      <Box 
        data-testid="file-collections-page"
        sx={{ 
          height: '100%', 
          display: 'flex', 
          bgcolor: 'background.default'
        }}
      >
        <Box sx={{ width: 320, flexShrink: 0 }}>
          <CollectionSidebar />
        </Box>
        <MainContent />
        
        {/* Modals */}
        <NewCollectionModal />
        <AddPageModal />
        <AddMultiplePagesModal />
        <NewFileModal />
        <DeleteConfirmationModal />
      </Box>
    </CollectionProvider>
  );
}

export default FileCollectionsPage;