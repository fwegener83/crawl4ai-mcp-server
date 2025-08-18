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
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import WebIcon from '@mui/icons-material/Web';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';

export interface TopNavigationProps {
  title?: string;
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  title = 'Crawl4AI File Manager',
  currentPage = 'file-collections',
  onNavigate
}) => {
  const { mode, toggleTheme } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const navigationTabs = [
    { id: 'file-collections', label: 'File Collections', icon: <FolderIcon fontSize="small" /> },
    { id: 'rag-query', label: 'RAG Query', icon: <SearchIcon fontSize="small" /> },
  ];

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
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
                data-testid={`${tab.id}-tab`}
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

      </Toolbar>
    </AppBar>
  );
};

export default TopNavigation;