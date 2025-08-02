import React from 'react';
import { Switch as MuiSwitch } from '@mui/material';
import type { SwitchProps as MuiSwitchProps } from '@mui/material';

export interface SwitchProps extends MuiSwitchProps {
  // Additional custom props can be added here
}

export const Switch: React.FC<SwitchProps> = (props) => {
  return <MuiSwitch {...props} />;
};

export default Switch;