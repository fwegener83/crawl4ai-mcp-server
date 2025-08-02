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
  Chip,
  Tabs,
  Tab
} from '../ui';
import { useTheme } from '../../contexts/ThemeContext';
import SettingsIcon from '@mui/icons-material/Settings';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import WebIcon from '@mui/icons-material/Web';
import HomeIcon from '@mui/icons-material/Home';
import LanguageIcon from '@mui/icons-material/Language';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import StorageIcon from '@mui/icons-material/Storage';
import FolderIcon from '@mui/icons-material/Folder';

export interface TopNavigationProps {
  title?: string;
  currentPage?: string;
  onNavigate?: (page: string) => void;
  onSettingsClick?: () => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  title = 'Crawl4AI File Manager',
  currentPage = 'file-collections',
  onNavigate,
  onSettingsClick
}) => {
  const { mode, toggleTheme } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [settingsAnchorEl, setSettingsAnchorEl] = React.useState<null | HTMLElement>(null);

  const navigationTabs = [
    { id: 'home', label: 'Home', icon: <HomeIcon fontSize="small" /> },
    { id: 'simple-crawl', label: 'Simple Crawl', icon: <LanguageIcon fontSize="small" /> },
    { id: 'deep-crawl', label: 'Deep Crawl', icon: <TravelExploreIcon fontSize="small" /> },
    { id: 'collections', label: 'Collections', icon: <StorageIcon fontSize="small" /> },
    { id: 'file-collections', label: 'File Collections', icon: <FolderIcon fontSize="small" /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon fontSize="small" /> }
  ];

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

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    if (onNavigate) {
      onNavigate(newValue);
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
        <Box sx={{ display: 'flex', alignItems: 'center', mr: 3 }}>
          <WebIcon sx={{ color: 'primary.main', mr: 1.5 }} />
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 'bold',
              color: 'text.primary',
              whiteSpace: 'nowrap'
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

        {/* Center - Navigation Tabs */}
        <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
          <Tabs
            value={currentPage}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 48,
                textTransform: 'none',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'text.secondary',
                '&.Mui-selected': {
                  color: 'primary.main',
                  fontWeight: 600
                }
              }
            }}
          >
            {navigationTabs.map((tab) => (
              <Tab
                key={tab.id}
                value={tab.id}
                label={tab.label}
                icon={tab.icon}
                iconPosition="start"
                sx={{ 
                  minWidth: 'auto',
                  px: 2
                }}
              />
            ))}
          </Tabs>
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