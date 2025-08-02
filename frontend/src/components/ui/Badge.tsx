import React from 'react';
import { Badge as MuiBadge } from '@mui/material';
import type { BadgeProps as MuiBadgeProps } from '@mui/material';

export interface BadgeProps extends MuiBadgeProps {
  // Additional custom props can be added here
}

export const Badge: React.FC<BadgeProps> = (props) => {
  return <MuiBadge {...props} />;
};

export default Badge;