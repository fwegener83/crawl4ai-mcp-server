import { Box } from '../ui';
import CollectionSidebar from './CollectionSidebar';
import MainContent from './MainContent';
import NewCollectionModal from './modals/NewCollectionModal';
import AddPageModal from './modals/AddPageModal';
import NewFileModal from './modals/NewFileModal';
import DeleteConfirmationModal from './modals/DeleteConfirmationModal';

export interface CollectionFileManagerProps {
  className?: string;
}

export const CollectionFileManager: React.FC<CollectionFileManagerProps> = ({ 
  className = '' 
}) => {
  return (
    <Box 
      sx={{ 
        height: '100%', 
        display: 'flex',
        bgcolor: 'background.default'
      }}
      className={className}
    >
      {/* Collections Sidebar */}
      <Box sx={{ 
        width: 320, 
        flexShrink: 0,
        borderRight: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper'
      }}>
        <CollectionSidebar />
      </Box>
      
      {/* Main Content Area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <MainContent />
      </Box>
      
      {/* Modals */}
      <NewCollectionModal />
      <AddPageModal />
      <NewFileModal />
      <DeleteConfirmationModal />
    </Box>
  );
};

export default CollectionFileManager;