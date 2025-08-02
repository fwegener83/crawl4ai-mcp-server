import { useState } from 'react';
import { Box, Typography, Card, CardContent, Badge } from '../components/ui';
import { Button } from '../components/ui/Button';
import { useNotification } from '../components/ui/NotificationProvider';
import SimpleCrawlForm from '../components/SimpleCrawlForm';
import MarkdownEditor from '../components/MarkdownEditor';
import SaveToCollectionModal from '../components/SaveToCollectionModal';
import SaveIcon from '@mui/icons-material/Save';
import DescriptionIcon from '@mui/icons-material/Description';

export function SimpleCrawlPage() {
  const [crawledContent, setCrawledContent] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const { showSuccess } = useNotification();

  const handleCrawlComplete = (content: string) => {
    setCrawledContent(content);
    setEditedContent(content);
    showSuccess('Website content has been successfully crawled and is ready for editing.');
  };

  const handleContentChange = (content: string) => {
    setEditedContent(content);
    setHasUnsavedChanges(content !== crawledContent);
  };

  const handleSaveClick = () => {
    if (editedContent.trim()) {
      setShowSaveModal(true);
    }
  };

  const handleSaveComplete = (collectionName: string) => {
    setHasUnsavedChanges(false);
    showSuccess(`Successfully saved to collection: ${collectionName}`);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Page Header */}
      <Box>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Simple Website Crawling
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Extract clean content from any webpage and edit it with our markdown editor.
        </Typography>
      </Box>

      {/* Crawl Form */}
      <Card>
        <CardContent>
          <SimpleCrawlForm onCrawlComplete={handleCrawlComplete} />
        </CardContent>
      </Card>

      {/* Content Editor */}
      {crawledContent && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6" component="h2">
              Extracted Content
            </Typography>
            <Button
              variant="contained"
              color="success"
              startIcon={<SaveIcon />}
              onClick={handleSaveClick}
              disabled={!editedContent.trim()}
              data-testid="save-to-collection-button"
              sx={{ position: 'relative' }}
            >
              Save to Collection
              {hasUnsavedChanges && (
                <Badge
                  color="warning"
                  variant="dot"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                  }}
                />
              )}
            </Button>
          </Box>
          
          <Card sx={{ flex: 1 }}>
            <CardContent sx={{ height: '100%' }}>
              <MarkdownEditor
                content={crawledContent}
                onChange={handleContentChange}
                onSave={handleSaveClick}
              />
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Empty State */}
      {!crawledContent && (
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <DescriptionIcon 
                sx={{ 
                  fontSize: 64, 
                  color: 'text.secondary',
                  mb: 2
                }} 
              />
              <Typography variant="h6" gutterBottom>
                No content yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter a URL above to start crawling and see the extracted content here.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Save Modal */}
      <SaveToCollectionModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        content={editedContent}
        onSaveComplete={handleSaveComplete}
      />
    </Box>
  );
}

export default SimpleCrawlPage;