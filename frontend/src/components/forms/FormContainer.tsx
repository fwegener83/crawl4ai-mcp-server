import React from 'react';
import { FormContainer as RHFFormContainer } from 'react-hook-form-mui';
import type { FormContainerProps } from 'react-hook-form-mui';
import { Box } from '../ui';

export interface FormContainerWrapperProps extends FormContainerProps {
  children: React.ReactNode;
  spacing?: number;
}

export const FormContainer: React.FC<FormContainerWrapperProps> = ({
  children,
  spacing = 3,
  ...props
}) => {
  return (
    <RHFFormContainer {...props}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: spacing }}>
        {children}
      </Box>
    </RHFFormContainer>
  );
};

export default FormContainer;