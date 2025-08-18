import React, { useState } from 'react';
import {
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Description as DescriptionIcon,
  Web as WebIcon,
  TravelExplore as TravelExploreIcon
} from '@mui/icons-material';

interface AddContentMenuProps {
  onAddFile: () => void;
  onAddPage: () => void;
  onAddMultiplePages: () => void;
  disabled?: boolean;
}

const AddContentMenu: React.FC<AddContentMenuProps> = ({
  onAddFile,
  onAddPage,
  onAddMultiplePages,
  disabled = false
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMenuAction = (action: () => void) => {
    action();
    handleClose();
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddIcon />}
        onClick={handleClick}
        disabled={disabled}
        size="medium"
        aria-controls={open ? 'add-content-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        data-testid="add-content-button"
      >
        Add Content
      </Button>
      
      <Menu
        id="add-content-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'add-content-button',
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        data-testid="add-content-menu"
      >
        <MenuItem 
          onClick={() => handleMenuAction(onAddFile)}
          data-testid="add-file-item"
        >
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>New File</ListItemText>
        </MenuItem>
        
        <MenuItem 
          onClick={() => handleMenuAction(onAddPage)}
          data-testid="add-page-item"
        >
          <ListItemIcon>
            <WebIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Add Page</ListItemText>
        </MenuItem>
        
        <MenuItem 
          onClick={() => handleMenuAction(onAddMultiplePages)}
          data-testid="add-multiple-pages-item"
        >
          <ListItemIcon>
            <TravelExploreIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Add Multiple Pages</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default AddContentMenu;