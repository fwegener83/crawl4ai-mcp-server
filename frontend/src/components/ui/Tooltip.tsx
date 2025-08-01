import React from 'react';
import { Tooltip as MuiTooltip } from '@mui/material';
import type { TooltipProps as MuiTooltipProps } from '@mui/material';

export interface TooltipProps extends MuiTooltipProps {
  // Additional custom props can be added here
}

export const Tooltip: React.FC<TooltipProps> = (props) => {
  return <MuiTooltip {...props} />;
};

export default Tooltip;