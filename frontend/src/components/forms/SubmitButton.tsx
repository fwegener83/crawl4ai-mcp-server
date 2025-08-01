import React from 'react';
import { LoadingButton } from '../ui';
import type { LoadingButtonProps } from '../ui';
import { useFormState } from 'react-hook-form';

export interface SubmitButtonProps extends Omit<LoadingButtonProps, 'type' | 'loading'> {
  loading?: boolean;
  submitText?: string;
  loadingText?: string;
}

export const SubmitButton: React.FC<SubmitButtonProps> = ({
  loading: externalLoading = false,
  submitText = 'Submit',
  loadingText = 'Submitting...',
  disabled,
  children,
  ...props
}) => {
  const { isSubmitting } = useFormState();
  const isLoading = externalLoading || isSubmitting;

  return (
    <LoadingButton
      type="submit"
      variant="contained"
      loading={isLoading}
      disabled={disabled || isLoading}
      {...props}
    >
      {children || (isLoading ? loadingText : submitText)}
    </LoadingButton>
  );
};

export default SubmitButton;