
import React from 'react';
import { Box, Typography, Card, CardContent, Avatar } from '../components/ui';
import { Button } from '../components/ui/Button';
import LanguageIcon from '@mui/icons-material/Language';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import StorageIcon from '@mui/icons-material/Storage';
import FileOpenIcon from '@mui/icons-material/FileOpen';

type Page = 'home' | 'simple-crawl' | 'deep-crawl' | 'collections' | 'file-collections';

interface HomePageProps {
  onNavigate?: (page: Page) => void;
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  buttonText: string;
  buttonColor: 'primary' | 'success' | 'secondary';
  onAction: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  buttonText,
  buttonColor,
  onAction,
}) => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar
          sx={{
            bgcolor: `${buttonColor}.light`,
            color: `${buttonColor}.main`,
            mr: 2,
          }}
        >
          {icon}
        </Avatar>
        <Typography variant="h6" component="h3">
          {title}
        </Typography>
      </Box>
      
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: 3, flexGrow: 1 }}
      >
        {description}
      </Typography>
      
      <Button
        variant="contained"
        color={buttonColor}
        fullWidth
        onClick={onAction}
        sx={{ mt: 'auto' }}
      >
        {buttonText}
      </Button>
    </CardContent>
  </Card>
);

export function HomePage({ onNavigate }: HomePageProps) {
  const features = [
    {
      title: 'Simple Website Crawling',
      description: 'Extract content from individual web pages with clean markdown output.',
      icon: <LanguageIcon />,
      buttonText: 'Start Simple Crawl',
      buttonColor: 'primary' as const,
      onAction: () => onNavigate?.('simple-crawl'),
    },
    {
      title: 'Deep Website Crawling',
      description: 'Crawl entire domains with advanced strategies and filtering options.',
      icon: <TravelExploreIcon />,
      buttonText: 'Start Deep Crawl',
      buttonColor: 'success' as const,
      onAction: () => onNavigate?.('deep-crawl'),
    },
    {
      title: 'RAG Collections',
      description: 'Organize and search your crawled content with RAG-powered semantic search.',
      icon: <StorageIcon />,
      buttonText: 'Manage Collections',
      buttonColor: 'secondary' as const,
      onAction: () => onNavigate?.('collections'),
    },
    {
      title: 'File Manager',
      description: 'Organize crawled content in file-based collections with built-in editor.',
      icon: <FileOpenIcon />,
      buttonText: 'Open File Manager',
      buttonColor: 'primary' as const,
      onAction: () => onNavigate?.('file-collections'),
    },
  ];

  const stats = [
    { value: '7', label: 'Available Tools', color: 'primary.main' },
    { value: '✓', label: 'RAG Enabled', color: 'success.main' },
    { value: '∞', label: 'Collections', color: 'secondary.main' },
  ];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', py: 2 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Web Crawling & Content Management
        </Typography>
        <Typography
          variant="h6"
          color="text.secondary"
          sx={{ maxWidth: 600, mx: 'auto' }}
        >
          Extract content from websites, perform deep crawling, and manage your data
          with our RAG-powered knowledge base system.
        </Typography>
      </Box>

      {/* Feature Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)',
          },
          gap: 3,
        }}
      >
        {features.map((feature, index) => (
          <FeatureCard key={index} {...feature} />
        ))}
      </Box>

      {/* System Status */}
      <Card sx={{ mt: 'auto' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(3, 1fr)',
              },
              gap: 4,
            }}
          >
            {stats.map((stat, index) => (
              <Box key={index} sx={{ textAlign: 'center' }}>
                <Typography
                  variant="h4"
                  component="div"
                  sx={{ color: stat.color, fontWeight: 'bold' }}
                >
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default HomePage;