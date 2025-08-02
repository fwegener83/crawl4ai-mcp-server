import React from 'react';
import { SwitchElement as RHFSwitchElement } from 'react-hook-form-mui';
import type { SwitchElementProps } from 'react-hook-form-mui';

export interface CustomSwitchElementProps extends SwitchElementProps {
  // Additional custom props can be added here
}

export const SwitchElement: React.FC<CustomSwitchElementProps> = (props) => {
  return <RHFSwitchElement {...props as any} />;
};

export default SwitchElement;