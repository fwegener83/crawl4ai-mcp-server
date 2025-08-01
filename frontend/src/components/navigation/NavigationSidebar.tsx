import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  IconButton,
  Tooltip
} from '../ui';
import { useTheme } from '../../contexts/ThemeContext';
import HomeIcon from '@mui/icons-material/Home';
import LanguageIcon from '@mui/icons-material/Language';
import StorageIcon from '@mui/icons-material/Storage';
import SettingsIcon from '@mui/icons-material/Settings';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import MenuIcon from '@mui/icons-material/Menu';

export interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  active?: boolean;
}

export interface NavigationSidebarProps {
  items?: NavigationItem[];
  currentPath?: string;
  onNavigate?: (path: string) => void;
  variant?: 'permanent' | 'temporary';
  open?: boolean;
  onClose?: () => void;
  width?: number;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  items = [],
  currentPath = '/',
  onNavigate,
  variant = 'permanent',
  open = true,
  onClose,
  width = 280,
}) => {
  const { mode, toggleTheme } = useTheme();

  const defaultItems: NavigationItem[] = [
    {
      id: 'home',
      label: 'Home',
      icon: <HomeIcon />,
      path: '/',
      active: currentPath === '/'
    },
    {
      id: 'simple-crawl',
      label: 'Simple Crawl',
      icon: <LanguageIcon />,
      path: '/simple-crawl',
      active: currentPath === '/simple-crawl'
    },
    {
      id: 'collections',
      label: 'Collections',
      icon: <StorageIcon />,
      path: '/collections',
      active: currentPath === '/collections'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
      active: currentPath === '/settings'
    }
  ];

  const navigationItems = items.length > 0 ? items : defaultItems;

  const handleItemClick = (path: string) => {
    if (onNavigate) {
      onNavigate(path);
    }
    if (variant === 'temporary' && onClose) {
      onClose();
    }
  };

  const drawerContent = (
    <Box sx={{ width, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            Crawl4AI
          </Typography>
          {variant === 'temporary' && (
            <IconButton onClick={onClose} size="small">
              <MenuIcon />
            </IconButton>
          )}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Web Content Extraction
        </Typography>
      </Box>

      {/* Navigation Items */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ py: 1 }}>
          {navigationItems.map((item) => (
            <ListItem key={item.id} disablePadding>
              <ListItemButton
                selected={item.active || currentPath === item.path}
                onClick={() => handleItemClick(item.path)}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.main',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    }
                  }
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    variant: 'body2',
                    fontWeight: item.active || currentPath === item.path ? 'medium' : 'regular'
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Theme
          </Typography>
          <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
            <IconButton onClick={toggleTheme} size="small">
              {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );

  if (variant === 'temporary') {
    return (
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width,
          },
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default NavigationSidebar;