import { Component, type ErrorInfo, type ReactNode } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert
} from './ui';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box 
          sx={{ 
            minHeight: '100vh', 
            bgcolor: 'background.default',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            p: 2 
          }}
        >
          <Paper 
            sx={{ 
              maxWidth: 'md', 
              width: '100%', 
              p: 4,
              textAlign: 'center'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, justifyContent: 'center' }}>
              <Box 
                sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'error.light', 
                  borderRadius: 2, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  mr: 2
                }}
              >
                <ErrorIcon sx={{ color: 'error.main' }} />
              </Box>
              <Typography variant="h5" fontWeight="medium">
                Something went wrong
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Typography variant="body1" color="text.secondary">
                An unexpected error occurred while rendering this page. This might be a temporary issue.
              </Typography>

              <Alert severity="error" sx={{ textAlign: 'left' }}>
                <Typography variant="body2" fontWeight="medium" gutterBottom>
                  Error Details:
                </Typography>
                <Typography variant="body2" fontFamily="monospace" sx={{ wordBreak: 'break-word' }}>
                  {this.state.error?.message || 'Unknown error'}
                </Typography>
              </Alert>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  onClick={() => window.location.reload()}
                  variant="contained"
                  startIcon={<RefreshIcon />}
                >
                  Reload Page
                </Button>
                <Button
                  onClick={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}
                  variant="outlined"
                >
                  Try Again
                </Button>
              </Box>

              <Button
                onClick={() => {
                  const errorReport = {
                    error: this.state.error?.message,
                    stack: this.state.error?.stack,
                    componentStack: this.state.errorInfo?.componentStack,
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent,
                    url: window.location.href,
                  };
                  console.error('Error Report:', errorReport);
                  navigator.clipboard?.writeText(JSON.stringify(errorReport, null, 2));
                }}
                variant="text"
                size="small"
                startIcon={<ContentCopyIcon />}
                color="inherit"
              >
                Copy error details to clipboard
              </Button>
            </Box>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;