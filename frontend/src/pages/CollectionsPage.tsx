import { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Alert, CircularProgress } from '../components/ui';
// Grid has typing issues, using Box with flexbox instead
import { Button } from '../components/ui/Button';
import { useCollections } from '../hooks/useApi';
import CollectionsList from '../components/CollectionsList';
import SemanticSearch from '../components/SemanticSearch';
import SearchResultsList from '../components/SearchResultsList';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';
import WebIcon from '@mui/icons-material/Web';
import type { SearchResult } from '../types/api';

export function CollectionsPage() {
  const [selectedCollection, setSelectedCollection] = useState<string>('default');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [lastQuery, setLastQuery] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);

  const {
    collections,
    refreshCollections,
    deleteCollection,
    listLoading,
    listError,
    deleteLoading,
    deleteError,
  } = useCollections();

  // Load collections on mount
  useEffect(() => {
    refreshCollections();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Update selected collection if current one is deleted
  useEffect(() => {
    if (selectedCollection !== 'default' && collections.length > 0) {
      const exists = collections.some(c => c.name === selectedCollection);
      if (!exists) {
        setSelectedCollection('default');
      }
    }
  }, [collections, selectedCollection]);

  const handleCollectionSelect = (collectionName: string) => {
    setSelectedCollection(collectionName);
    // Clear search results when switching collections
    setSearchResults([]);
    setLastQuery('');
  };

  const handleDeleteCollection = async (collectionName: string) => {
    try {
      await deleteCollection(collectionName);
      setDeleteSuccess(`Successfully deleted collection: ${collectionName}`);
      setTimeout(() => setDeleteSuccess(null), 5000);
      
      // Clear search results if we deleted the selected collection
      if (selectedCollection === collectionName) {
        setSearchResults([]);
        setLastQuery('');
      }
    } catch (error) {
      console.error('Delete collection failed:', error);
    }
  };

  const handleSearchResults = (results: SearchResult[], query: string) => {
    setSearchResults(results);
    setLastQuery(query);
  };

  const handleSearchResultSelect = (result: SearchResult, index: number) => {
    // Could implement additional actions here, like viewing in detail
    console.log('Selected search result:', result, index);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Page Header */}
      <Box>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Collection Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your saved content collections and search with RAG-powered semantic search.
        </Typography>
      </Box>

      {/* Success Message */}
      {deleteSuccess && (
        <Alert 
          severity="success" 
          icon={<CheckCircleIcon />}
          data-testid="delete-success-message"
        >
          {deleteSuccess}
        </Alert>
      )}

      {/* Loading State */}
      {listLoading && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={32} />
              <Typography variant="body1" color="text.secondary" sx={{ ml: 2 }}>
                Loading collections...
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {listError && (
        <Alert 
          severity="error" 
          icon={<ErrorIcon />}
          action={
            <Button 
              color="error" 
              variant="text" 
              size="small" 
              onClick={refreshCollections}
            >
              Try again
            </Button>
          }
        >
          <Typography variant="subtitle2" gutterBottom>
            Failed to load collections
          </Typography>
          <Typography variant="body2">
            {listError}
          </Typography>
        </Alert>
      )}

      {/* Main Content */}
      {!listLoading && !listError && (
        <Box sx={{ flex: 1, display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
          {/* Left Column: Collections Management */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <CollectionsList
                collections={collections}
                selectedCollection={selectedCollection}
                onSelectCollection={handleCollectionSelect}
                onDeleteCollection={handleDeleteCollection}
                isDeleting={deleteLoading}
                deleteError={deleteError}
              />

            {/* Collection Statistics */}
            {collections.length > 0 && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight="semibold">
                    Statistics
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Box sx={{ flex: 1, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" fontWeight="bold">
                        {collections.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Collections
                      </Typography>
                    </Box>
                    <Box sx={{ flex: 1, textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {collections.reduce((sum, c) => sum + c.count, 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Items
                      </Typography>
                    </Box>
                  </Box>
                  
                  {/* Selected Collection Info */}
                  {selectedCollection && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                      <Typography variant="body2" color="text.secondary">
                        <Typography component="span" fontWeight="medium">Selected:</Typography> {selectedCollection}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <Typography component="span" fontWeight="medium">Items:</Typography>{' '}
                        {collections.find(c => c.name === selectedCollection)?.count || 0}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Box>

          {/* Right Column: Search Interface */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <SemanticSearch
                selectedCollection={selectedCollection}
                onSearchResults={handleSearchResults}
              />

              {/* Search Results */}
              <SearchResultsList
                results={searchResults}
                query={lastQuery}
                onSelectResult={handleSearchResultSelect}
              />
          </Box>
        </Box>
      )}

      {/* Empty State */}
      {!listLoading && !listError && collections.length === 0 && (
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <FolderIcon 
                sx={{ 
                  fontSize: 64, 
                  color: 'text.secondary',
                  mb: 2
                }} 
              />
              <Typography variant="h5" gutterBottom fontWeight="medium">
                No collections found
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 'md', mx: 'auto', mb: 4 }}>
                Start by crawling some websites and saving the content to collections. 
                Then you can search and manage your saved content here.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SearchIcon />}
                  onClick={() => window.location.hash = 'simple-crawl'}
                >
                  Start Simple Crawl
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<WebIcon />}
                  onClick={() => window.location.hash = 'deep-crawl'}
                >
                  Start Deep Crawl
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default CollectionsPage;