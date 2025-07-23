import type { APIError } from '../types/api';

export interface ParsedError {
  title: string;
  message: string;
  code?: string;
  isNetworkError: boolean;
  isServerError: boolean;
  isClientError: boolean;
  statusCode?: number;
}

export function parseAPIError(error: any): ParsedError {
  // Handle API errors with our structure
  if (error && typeof error === 'object' && error.error && error.message) {
    const apiError = error as APIError;
    const statusCode = typeof apiError.error === 'string' ? 
      parseInt(apiError.error) : 
      (typeof apiError.error === 'number' ? apiError.error : undefined);

    return {
      title: getErrorTitle(statusCode, apiError.error),
      message: apiError.message,
      code: apiError.error.toString(),
      isNetworkError: apiError.error === 'NetworkError',
      isServerError: statusCode ? statusCode >= 500 : false,
      isClientError: statusCode ? statusCode >= 400 && statusCode < 500 : false,
      statusCode,
    };
  }

  // Handle network errors
  if (error?.name === 'NetworkError' || error?.code === 'NETWORK_ERROR') {
    return {
      title: 'Connection Failed',
      message: 'Unable to connect to the server. Please check your connection and try again.',
      isNetworkError: true,
      isServerError: false,
      isClientError: false,
    };
  }

  // Handle timeout errors
  if (error?.name === 'TimeoutError' || error?.code === 'TIMEOUT') {
    return {
      title: 'Request Timeout',
      message: 'The request took too long to complete. Please try again.',
      isNetworkError: false,
      isServerError: false,
      isClientError: false,
    };
  }

  // Handle generic errors
  const message = error?.message || error?.toString() || 'An unexpected error occurred';
  
  return {
    title: 'Error',
    message,
    isNetworkError: false,
    isServerError: false,
    isClientError: false,
  };
}

function getErrorTitle(statusCode?: number, errorCode?: string | number): string {
  if (statusCode) {
    switch (statusCode) {
      case 400:
        return 'Bad Request';
      case 401:
        return 'Unauthorized';
      case 403:
        return 'Forbidden';
      case 404:
        return 'Not Found';
      case 408:
        return 'Request Timeout';
      case 429:
        return 'Too Many Requests';
      case 500:
        return 'Server Error';
      case 502:
        return 'Bad Gateway';
      case 503:
        return 'Service Unavailable';
      case 504:
        return 'Gateway Timeout';
      default:
        if (statusCode >= 400 && statusCode < 500) {
          return 'Client Error';
        } else if (statusCode >= 500) {
          return 'Server Error';
        }
        return 'HTTP Error';
    }
  }

  if (errorCode === 'NetworkError') {
    return 'Connection Failed';
  }

  return 'Error';
}

export function getErrorActionSuggestion(error: ParsedError): string {
  if (error.isNetworkError) {
    return 'Check your internet connection and try again.';
  }

  if (error.isServerError) {
    return 'The server is experiencing issues. Please try again in a few moments.';
  }

  if (error.statusCode === 404) {
    return 'The requested resource was not found. Please check the URL or contact support.';
  }

  if (error.statusCode === 401) {
    return 'Authentication is required. Please log in and try again.';
  }

  if (error.statusCode === 403) {
    return 'You do not have permission to perform this action.';
  }

  if (error.statusCode === 429) {
    return 'You are making requests too frequently. Please wait and try again.';
  }

  if (error.isClientError) {
    return 'Please check your input and try again.';
  }

  return 'Please try again. If the problem persists, contact support.';
}

export function shouldRetryRequest(error: ParsedError): boolean {
  // Retry network errors
  if (error.isNetworkError) {
    return true;
  }

  // Retry server errors (5xx)
  if (error.isServerError) {
    return true;
  }

  // Don't retry client errors (4xx) except for specific cases
  if (error.isClientError) {
    // Retry timeouts and rate limits
    return error.statusCode === 408 || error.statusCode === 429;
  }

  return false;
}

export function formatErrorForLogging(error: any, context?: string): {
  level: 'error' | 'warn' | 'info';
  message: string;
  details: any;
} {
  const parsed = parseAPIError(error);
  
  const level = parsed.isClientError ? 'warn' : 'error';
  const message = context ? `${context}: ${parsed.title}` : parsed.title;
  
  const details = {
    originalError: error,
    parsedError: parsed,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  };

  return { level, message, details };
}