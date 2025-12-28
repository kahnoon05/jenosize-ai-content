/**
 * Status Badge Component
 *
 * Displays status indicators with different variants.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { CheckCircle2, AlertCircle, Clock, Info } from 'lucide-react';

interface StatusBadgeProps {
  status: 'success' | 'error' | 'warning' | 'info' | 'pending';
  label?: string;
  showIcon?: boolean;
  className?: string;
}

const statusConfig = {
  success: {
    className: 'badge-success',
    icon: CheckCircle2,
    defaultLabel: 'Success',
  },
  error: {
    className: 'badge-error',
    icon: AlertCircle,
    defaultLabel: 'Error',
  },
  warning: {
    className: 'badge-warning',
    icon: AlertCircle,
    defaultLabel: 'Warning',
  },
  info: {
    className: 'badge-primary',
    icon: Info,
    defaultLabel: 'Info',
  },
  pending: {
    className: 'badge-secondary',
    icon: Clock,
    defaultLabel: 'Pending',
  },
};

export function StatusBadge({
  status,
  label,
  showIcon = true,
  className,
}: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;
  const displayLabel = label || config.defaultLabel;

  return (
    <span className={cn(config.className, className)}>
      {showIcon && <Icon className="h-3 w-3 mr-1" />}
      {displayLabel}
    </span>
  );
}

export default StatusBadge;
