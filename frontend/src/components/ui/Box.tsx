import React from 'react';
import { Box as MuiBox, BoxProps as MuiBoxProps } from '@mui/material';

export interface BoxProps extends MuiBoxProps {
  // Additional custom props can be added here
}

export const Box: React.FC<BoxProps> = (props) => {
  return <MuiBox {...props} />;
};

export default Box;