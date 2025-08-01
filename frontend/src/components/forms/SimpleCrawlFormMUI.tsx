import { useForm } from 'react-hook-form';
import { Card, CardContent, CardHeader, Box, Typography } from '../ui';
import { FormContainer, UrlFieldElement, SubmitButton } from '../forms';
import { useApi } from '../../hooks/useApi';
import { APIService } from '../../services/api';
import { useNotification } from '../ui/NotificationProvider';
import { parseAPIError } from '../../utils/errorHandling';
import LanguageIcon from '@mui/icons-material/Language';

interface SimpleCrawlFormData {
  url: string;
}

interface SimpleCrawlFormMUIProps {
  onCrawlComplete?: (content: string) => void;
}

export function SimpleCrawlFormMUI({ onCrawlComplete }: SimpleCrawlFormMUIProps) {
  const crawlApi = useApi<string>();
  const { showError, showSuccess } = useNotification();
  
  const form = useForm<SimpleCrawlFormData>({
    defaultValues: {
      url: ''
    }
  });

  const handleSubmit = async (data: SimpleCrawlFormData) => {
    try {
      const content = await crawlApi.execute(() => 
        APIService.extractWebContent(data.url.trim())
      );
      
      showSuccess('Content extracted successfully!');
      
      if (onCrawlComplete) {
        onCrawlComplete(content);
      }
    } catch (error) {
      console.error('Crawl failed:', error);
      const parsedError = parseAPIError(error);
      showError(`${parsedError.title}: ${parsedError.message}`);
    }
  };

  return (
    <Card>
      <CardHeader
        avatar={
          <Box
            sx={{
              width: 40,
              height: 40,
              backgroundColor: 'primary.light',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <LanguageIcon color="primary" />
          </Box>
        }
        title="Simple Website Crawling"
        subheader="Extract clean content from any webpage"
      />
      <CardContent>
        <FormContainer formContext={form as any} onSuccess={handleSubmit as any}>
          <UrlFieldElement
            name="url"
            label="Website URL"
            placeholder="https://example.com"
            required
            fullWidth
            disabled={crawlApi.loading}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Extract clean content from any webpage
            </Typography>
            <SubmitButton
              loading={crawlApi.loading}
              submitText="Extract Content"
              loadingText="Extracting..."
              data-testid="crawl-button"
            />
          </Box>
        </FormContainer>
      </CardContent>
    </Card>
  );
}

export default SimpleCrawlFormMUI;