import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
          <div className="max-w-md w-full">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-red-100 dark:bg-red-900 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h1 className="ml-3 text-lg font-semibold text-gray-900 dark:text-white">
                  Something went wrong
                </h1>
              </div>

              <div className="space-y-4">
                <p className="text-gray-600 dark:text-gray-300">
                  An unexpected error occurred while rendering this page. This might be a temporary issue.
                </p>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Error Details:
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-mono">
                    {this.state.error?.message || 'Unknown error'}
                  </p>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => window.location.reload()}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    Reload Page
                  </button>
                  <button
                    onClick={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    Try Again
                  </button>
                </div>

                <div className="text-center">
                  <button
                    onClick={() => {
                      const errorReport = {
                        error: this.state.error?.message,
                        stack: this.state.error?.stack,
                        componentStack: this.state.errorInfo?.componentStack,
                        timestamp: new Date().toISOString(),
                        userAgent: navigator.userAgent,
                        url: window.location.href,
                      };
                      console.error('Error Report:', errorReport);
                      navigator.clipboard?.writeText(JSON.stringify(errorReport, null, 2));
                    }}
                    className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline"
                  >
                    Copy error details to clipboard
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;