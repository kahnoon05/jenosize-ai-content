/**
 * Error Display Component
 *
 * Displays error messages with appropriate styling and actions.
 */

import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ErrorDisplayProps {
  title?: string;
  message: string;
  details?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorDisplay({
  title = 'Error',
  message,
  details,
  onRetry,
  className,
}: ErrorDisplayProps) {
  return (
    <div className={cn('alert-error', className)}>
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-red-900 mb-1">{title}</h3>
          <p className="text-red-800 mb-2">{message}</p>
          {details && (
            <details className="text-sm text-red-700 mt-2">
              <summary className="cursor-pointer font-medium hover:text-red-900">
                Show details
              </summary>
              <pre className="mt-2 p-2 bg-red-100 rounded text-xs overflow-x-auto">
                {details}
              </pre>
            </details>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-red-700 hover:text-red-900 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ErrorDisplay;
