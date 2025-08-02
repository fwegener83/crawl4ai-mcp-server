import React from 'react';
import { Breadcrumbs, Typography, Box } from '../ui';
import { Link } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import HomeIcon from '@mui/icons-material/Home';

export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

export interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[];
  onNavigate?: (path: string) => void;
  showHomeIcon?: boolean;
  maxItems?: number;
}

export const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({
  items,
  onNavigate,
  showHomeIcon = true,
  maxItems = 8,
}) => {
  const handleClick = (event: React.MouseEvent, path: string) => {
    event.preventDefault();
    if (onNavigate) {
      onNavigate(path);
    }
  };

  const renderBreadcrumbItem = (item: BreadcrumbItem, index: number, isLast: boolean) => {
    const content = (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {item.icon && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {item.icon}
          </Box>
        )}
        {showHomeIcon && index === 0 && !item.icon && (
          <HomeIcon sx={{ fontSize: 16 }} />
        )}
        <Typography
          variant="body2"
          color={isLast ? 'text.primary' : 'text.secondary'}
          fontWeight={isLast ? 'medium' : 'regular'}
        >
          {item.label}
        </Typography>
      </Box>
    );

    if (isLast || !item.path) {
      return content;
    }

    return (
      <Link
        component="button"
        variant="body2"
        onClick={(event: React.MouseEvent) => handleClick(event, item.path!)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          textDecoration: 'none',
          color: 'text.secondary',
          '&:hover': {
            color: 'primary.main',
            textDecoration: 'underline',
          },
          border: 'none',
          background: 'none',
          cursor: 'pointer',
          p: 0,
        }}
      >
        {content}
      </Link>
    );
  };

  if (items.length === 0) {
    return null;
  }

  return (
    <Box sx={{ py: 1 }}>
      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        maxItems={maxItems}
        aria-label="breadcrumb navigation"
        sx={{
          '& .MuiBreadcrumbs-separator': {
            color: 'text.disabled',
          },
        }}
      >
        {items.map((item, index) => (
          <Box key={`${item.path || item.label}-${index}`}>
            {renderBreadcrumbItem(item, index, index === items.length - 1)}
          </Box>
        ))}
      </Breadcrumbs>
    </Box>
  );
};

export default BreadcrumbNavigation;