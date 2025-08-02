import { CircularProgress, Box, Typography } from './ui';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning' | 'inherit';
  text?: string;
  centered?: boolean;
}

export function LoadingSpinner({ 
  size = 'md', 
  color = 'primary', 
  text,
  centered = false 
}: LoadingSpinnerProps) {
  const getSize = () => {
    switch (size) {
      case 'sm':
        return 16;
      case 'md':
        return 24;
      case 'lg':
        return 32;
      case 'xl':
        return 40;
      default:
        return 24;
    }
  };

  const getTextVariant = () => {
    switch (size) {
      case 'sm':
        return 'body2' as const;
      case 'md':
        return 'body1' as const;
      case 'lg':
        return 'h6' as const;
      case 'xl':
        return 'h5' as const;
      default:
        return 'body1' as const;
    }
  };

  const spinner = (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <CircularProgress 
        size={getSize()} 
        color={color}
      />
      {text && (
        <Typography variant={getTextVariant()} color="text.secondary">
          {text}
        </Typography>
      )}
    </Box>
  );

  if (centered) {
    return (
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        p: 4 
      }}>
        {spinner}
      </Box>
    );
  }

  return spinner;
}

export default LoadingSpinner;