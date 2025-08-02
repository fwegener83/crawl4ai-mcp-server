import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Divider,
  Chip
} from '../ui';
import { useTheme } from '../../contexts/ThemeContext';
import SettingsIcon from '@mui/icons-material/Settings';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import WebIcon from '@mui/icons-material/Web';

export interface TopNavigationProps {
  title?: string;
  onSettingsClick?: () => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  title = 'Crawl4AI File Manager',
  onSettingsClick
}) => {
  const { mode, toggleTheme } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [settingsAnchorEl, setSettingsAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSettingsMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchorEl(event.currentTarget);
  };

  const handleSettingsMenuClose = () => {
    setSettingsAnchorEl(null);
  };

  const handleSettingsClick = () => {
    handleSettingsMenuClose();
    if (onSettingsClick) {
      onSettingsClick();
    }
  };

  return (
    <AppBar 
      position="static" 
      elevation={1}
      sx={{ 
        bgcolor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider'
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important' }}>
        {/* Left side - Title and Brand */}
        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <WebIcon sx={{ color: 'primary.main', mr: 1.5 }} />
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 'bold',
              color: 'text.primary'
            }}
          >
            {title}
          </Typography>
          <Chip 
            label="Beta" 
            size="small" 
            color="primary" 
            variant="outlined"
            sx={{ ml: 1.5, height: 20 }}
          />
        </Box>

        {/* Right side - Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Theme Toggle */}
          <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
            <IconButton 
              onClick={toggleTheme} 
              size="medium"
              sx={{ color: 'text.primary' }}
            >
              {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Info Menu */}
          <Tooltip title="Information">
            <IconButton 
              onClick={handleMenuOpen}
              size="medium"
              sx={{ color: 'text.primary' }}
            >
              <InfoOutlinedIcon />
            </IconButton>
          </Tooltip>

          {/* Settings Menu */}
          <Tooltip title="Settings">
            <IconButton 
              onClick={handleSettingsMenuOpen}
              size="medium"
              sx={{ color: 'text.primary' }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Info Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem disabled>
            <Box>
              <Typography variant="body2" fontWeight="medium">
                Crawl4AI File Manager
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Web Content Extraction & Management
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          <MenuItem disabled>
            <Typography variant="caption" color="text.secondary">
              Version 2.0.0-beta
            </Typography>
          </MenuItem>
        </Menu>

        {/* Settings Menu */}
        <Menu
          anchorEl={settingsAnchorEl}
          open={Boolean(settingsAnchorEl)}
          onClose={handleSettingsMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={handleSettingsClick}>
            <SettingsIcon sx={{ mr: 1.5, fontSize: 20 }} />
            Settings
          </MenuItem>
          <MenuItem onClick={toggleTheme}>
            {mode === 'light' ? (
              <DarkModeIcon sx={{ mr: 1.5, fontSize: 20 }} />
            ) : (
              <LightModeIcon sx={{ mr: 1.5, fontSize: 20 }} />
            )}
            {mode === 'light' ? 'Dark Mode' : 'Light Mode'}
          </MenuItem>
          <Divider />
          <MenuItem disabled>
            <AccountCircleIcon sx={{ mr: 1.5, fontSize: 20 }} />
            User Profile (Coming Soon)
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavigation;