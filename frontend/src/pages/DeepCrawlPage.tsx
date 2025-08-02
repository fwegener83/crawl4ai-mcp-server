import { useState } from 'react';
import { Box, Typography, Card, CardContent, Alert } from '../components/ui';
import { Button } from '../components/ui/Button';
import DeepCrawlForm from '../components/DeepCrawlForm';
import CrawlResultsList from '../components/CrawlResultsList';
import BulkSaveModal from '../components/BulkSaveModal';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PublicIcon from '@mui/icons-material/Public';
import SaveIcon from '@mui/icons-material/Save';
import type { CrawlResult } from '../types/api';

export function DeepCrawlPage() {
  const [crawlResults, setCrawlResults] = useState<CrawlResult[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [showBulkSaveModal, setShowBulkSaveModal] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const handleCrawlComplete = (results: CrawlResult[]) => {
    setCrawlResults(results);
    setSelectedIndices([]);
    setSaveSuccess(null);
  };

  const handleSelectMultiple = (_results: CrawlResult[], indices: number[]) => {
    setSelectedIndices(indices);
  };

  const handleBulkSaveClick = () => {
    console.log('Bulk Save clicked:', { 
      selectedIndices: selectedIndices.length, 
      crawlResults: crawlResults.length,
      selectedData: selectedIndices.map(i => ({index: i, hasSuccess: crawlResults[i]?.success}))
    });
    if (selectedIndices.length > 0) {
      console.log('Opening BulkSaveModal');
      setShowBulkSaveModal(true);
    } else {
      console.log('No items selected');
    }
  };

  const handleBulkSaveComplete = (collectionName: string, savedCount: number) => {
    setSaveSuccess(`Successfully saved ${savedCount} results to collection: ${collectionName}`);
    setTimeout(() => setSaveSuccess(null), 5000);
  };

  const successfulResults = crawlResults.filter(r => r.success);
  const failedResults = crawlResults.filter(r => r.success === false);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Page Header */}
      <Box>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Deep Website Crawling
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Crawl entire domains with advanced strategies, filtering, and bulk operations.
        </Typography>
      </Box>

      {/* Success Message */}
      {saveSuccess && (
        <Alert 
          severity="success" 
          icon={<CheckCircleIcon />}
          data-testid="bulk-success-message"
        >
          {saveSuccess}
        </Alert>
      )}

      {/* Deep Crawl Form */}
      <Card>
        <CardContent>
          <DeepCrawlForm onCrawlComplete={handleCrawlComplete} />
        </CardContent>
      </Card>

      {/* Results Summary and Actions - STICKY */}
      {crawlResults.length > 0 && (
        <Card sx={{ 
          position: 'sticky', 
          top: 0, 
          zIndex: 100,
          backgroundColor: 'background.paper',
          boxShadow: 2
        }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: { xs: 'wrap', md: 'nowrap' }, gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
                <Typography variant="body2" color="text.secondary">
                  <Typography component="span" fontWeight="medium" color="success.main">
                    {successfulResults.length}
                  </Typography>
                  {' '}successful
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <Typography component="span" fontWeight="medium" color="error.main">
                    {failedResults.length}
                  </Typography>
                  {' '}failed
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <Typography component="span" fontWeight="medium">
                    {crawlResults.reduce((sum, r) => sum + r.content.length, 0).toLocaleString()}
                  </Typography>
                  {' '}total characters
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {selectedIndices.length} selected
                </Typography>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<SaveIcon />}
                  onClick={handleBulkSaveClick}
                  disabled={selectedIndices.length === 0}
                >
                  Bulk Save to Collection
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Results List */}
      {crawlResults.length > 0 ? (
        <CrawlResultsList
          results={crawlResults}
          onSelectMultiple={handleSelectMultiple}
          selectedIndices={selectedIndices}
        />
      ) : (
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <PublicIcon 
                sx={{ 
                  fontSize: 64, 
                  color: 'text.secondary',
                  mb: 2
                }} 
              />
              <Typography variant="h6" gutterBottom>
                No crawl results yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Configure your deep crawl settings above and start crawling to see results here.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Bulk Save Modal */}
      <BulkSaveModal
        isOpen={showBulkSaveModal}
        onClose={() => setShowBulkSaveModal(false)}
        results={crawlResults}
        selectedIndices={selectedIndices}
        onSaveComplete={handleBulkSaveComplete}
      />
    </Box>
  );
}

export default DeepCrawlPage;