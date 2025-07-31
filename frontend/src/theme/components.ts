import type { Components, Theme } from '@mui/material/styles';

// Component style overrides for MUI theme
export const components: Components<Theme> = {
  // Button component overrides
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        textTransform: 'none',
        fontWeight: 500,
        boxShadow: 'none',
        '&:hover': {
          boxShadow: 'none',
        },
      },
      contained: {
        '&:hover': {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },

  // TextField component overrides
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
        },
      },
    },
  },

  // Card component overrides
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1)',
        '&:hover': {
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.12)',
        },
      },
    },
  },

  // Paper component overrides
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: 8,
      },
      elevation1: {
        boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1)',
      },
    },
  },

  // Dialog component overrides
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 16,
      },
    },
  },

  // Chip component overrides
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 16,
      },
    },
  },

  // AppBar component overrides
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1)',
        backgroundImage: 'none',
      },
    },
  },

  // Drawer component overrides
  MuiDrawer: {
    styleOverrides: {
      paper: {
        borderRadius: 0,
        border: 'none',
      },
    },
  },

  // List item button overrides
  MuiListItemButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        margin: '2px 8px',
        '&.Mui-selected': {
          borderRadius: 8,
        },
      },
    },
  },

  // Tab component overrides
  MuiTab: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        fontWeight: 500,
        minHeight: 48,
      },
    },
  },

  // Icon button overrides
  MuiIconButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
      },
    },
  },

  // Note: MuiLoadingButton would require @mui/lab
  // Uncomment when @mui/lab is added to dependencies
  // MuiLoadingButton: {
  //   styleOverrides: {
  //     root: {
  //       borderRadius: 8,
  //       textTransform: 'none',
  //       fontWeight: 500,
  //     },
  //   },
  // },
};