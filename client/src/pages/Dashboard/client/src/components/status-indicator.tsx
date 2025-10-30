import { cn } from '@/lib/utils';

interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'degraded' | 'idle' | 'running' | 'stopped' | 'connected' | 'disconnected' | 'pending' | 'completed' | 'error';
  label?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const statusColors = {
  online: 'bg-green-500',
  running: 'bg-green-500',
  connected: 'bg-green-500',
  completed: 'bg-green-500',
  idle: 'bg-yellow-500',
  pending: 'bg-yellow-500',
  degraded: 'bg-orange-500',
  offline: 'bg-gray-500',
  stopped: 'bg-gray-500',
  disconnected: 'bg-gray-500',
  error: 'bg-red-500',
};

const sizes = {
  sm: 'h-2 w-2',
  md: 'h-3 w-3',
  lg: 'h-4 w-4',
};

export function StatusIndicator({ status, label, showLabel = false, size = 'md' }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      <div className={cn('rounded-full', statusColors[status], sizes[size])} />
      {showLabel && (
        <span className="text-sm text-muted-foreground capitalize">
          {label || status}
        </span>
      )}
    </div>
  );
}
