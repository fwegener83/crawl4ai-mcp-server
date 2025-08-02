import React from 'react';
import { TextFieldElement } from './TextFieldElement';
import type { TextFieldElementProps } from 'react-hook-form-mui';

export interface UrlFieldElementProps extends Omit<TextFieldElementProps, 'type' | 'rules'> {
  required?: boolean;
  placeholder?: string;
}

export const UrlFieldElement: React.FC<UrlFieldElementProps> = ({
  required = false,
  placeholder = 'https://example.com',
  ...props
}) => {
  const urlValidation = {
    required: required ? 'URL is required' : false,
    pattern: {
      value: /^https?:\/\/.+/,
      message: 'Please enter a valid URL starting with http:// or https://'
    }
  };

  return (
    <TextFieldElement
      type="url"
      placeholder={placeholder}
      rules={urlValidation}
      {...props}
    />
  );
};

export default UrlFieldElement;