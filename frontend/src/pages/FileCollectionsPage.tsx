import { CollectionProvider } from '../contexts/CollectionContext';
import CollectionSidebar from '../components/collection/CollectionSidebar';
import MainContent from '../components/collection/MainContent';
import NewCollectionModal from '../components/collection/modals/NewCollectionModal';
import AddPageModal from '../components/collection/modals/AddPageModal';
import NewFileModal from '../components/collection/modals/NewFileModal';
import DeleteConfirmationModal from '../components/collection/modals/DeleteConfirmationModal';

export function FileCollectionsPage() {
  return (
    <CollectionProvider>
      <div className="h-full flex bg-gray-50 dark:bg-gray-900">
        <CollectionSidebar className="w-80 flex-shrink-0" />
        <MainContent />
        
        {/* Modals */}
        <NewCollectionModal />
        <AddPageModal />
        <NewFileModal />
        <DeleteConfirmationModal />
      </div>
    </CollectionProvider>
  );
}

export default FileCollectionsPage;