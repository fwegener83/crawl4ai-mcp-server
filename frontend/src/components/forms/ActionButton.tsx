import React, { useState } from 'react';
import { LoadingButton, Tooltip } from '../ui';
import type { LoadingButtonProps } from '../ui';

export interface ActionButtonProps extends Omit<LoadingButtonProps, 'loading'> {
  loading?: boolean;
  tooltip?: string;
  confirmAction?: boolean;
  confirmText?: string;
  onConfirm?: () => void | Promise<void>;
  successText?: string;
  errorText?: string;
  showFeedback?: boolean;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  loading: externalLoading = false,
  tooltip,
  confirmAction = false,
  confirmText = 'Are you sure?',
  onConfirm,
  onClick,
  successText = 'Success!',
  errorText = 'Error occurred',
  showFeedback = false,
  children,
  disabled,
  ...props
}) => {
  const [internalLoading, setInternalLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [feedback, setFeedback] = useState<'success' | 'error' | null>(null);

  const isLoading = externalLoading || internalLoading;

  const handleClick = async (event: React.MouseEvent<HTMLButtonElement>) => {
    if (confirmAction && !showConfirm) {
      setShowConfirm(true);
      return;
    }

    setShowConfirm(false);
    
    if (onConfirm && confirmAction) {
      setInternalLoading(true);
      try {
        await onConfirm();
        if (showFeedback) {
          setFeedback('success');
          setTimeout(() => setFeedback(null), 2000);
        }
      } catch (error) {
        if (showFeedback) {
          setFeedback('error');
          setTimeout(() => setFeedback(null), 2000);
        }
      } finally {
        setInternalLoading(false);
      }
    } else if (onClick) {
      if (onClick.constructor.name === 'AsyncFunction') {
        setInternalLoading(true);
        try {
          await (onClick as any)(event);
          if (showFeedback) {
            setFeedback('success');
            setTimeout(() => setFeedback(null), 2000);
          }
        } catch (error) {
          if (showFeedback) {
            setFeedback('error');
            setTimeout(() => setFeedback(null), 2000);
          }
        } finally {
          setInternalLoading(false);
        }
      } else {
        onClick(event);
      }
    }
  };

  const getButtonText = () => {
    if (feedback === 'success') return successText;
    if (feedback === 'error') return errorText;
    if (showConfirm) return confirmText;
    return children;
  };

  const getButtonColor = () => {
    if (feedback === 'success') return 'success' as const;
    if (feedback === 'error') return 'error' as const;
    if (showConfirm) return 'warning' as const;
    return props.color;
  };

  const button = (
    <LoadingButton
      loading={isLoading}
      disabled={disabled || isLoading}
      onClick={handleClick}
      color={getButtonColor()}
      {...props}
    >
      {getButtonText()}
    </LoadingButton>
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip}>
        {button}
      </Tooltip>
    );
  }

  return button;
};

export default ActionButton;