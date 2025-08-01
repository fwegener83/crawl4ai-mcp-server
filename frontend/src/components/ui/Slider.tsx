import React from 'react';
import { Slider as MuiSlider } from '@mui/material';
import type { SliderProps as MuiSliderProps } from '@mui/material';

export interface SliderProps extends MuiSliderProps {
  // Additional custom props can be added here
}

export const Slider: React.FC<SliderProps> = (props) => {
  return <MuiSlider {...props} />;
};

export default Slider;