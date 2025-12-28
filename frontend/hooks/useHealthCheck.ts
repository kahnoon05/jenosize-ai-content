/**
 * Custom Hook for Backend Health Check
 *
 * Monitors backend API connectivity and service health status.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient, APIError } from '@/lib/api-client';
import { HealthResponse } from '@/lib/types';

interface UseHealthCheckOptions {
  enabled?: boolean;
  refetchInterval?: number;
  onError?: (error: APIError) => void;
}

/**
 * Hook for checking backend health status
 */
export function useHealthCheck(options?: UseHealthCheckOptions) {
  const {
    enabled = true,
    refetchInterval = 30000, // Check every 30 seconds
    onError,
  } = options || {};

  const query = useQuery<HealthResponse, APIError>({
    queryKey: ['health'],
    queryFn: async () => {
      return await apiClient.healthCheck();
    },
    enabled,
    refetchInterval,
    refetchIntervalInBackground: false,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    staleTime: 15000, // Consider data stale after 15 seconds
  });

  if (query.isError && onError) {
    onError(query.error);
  }

  /**
   * Check if backend is healthy
   */
  const isHealthy = query.data?.status === 'healthy';

  /**
   * Get individual service statuses
   */
  const services = query.data?.services || {};

  /**
   * Check if all services are operational
   */
  const allServicesHealthy =
    services &&
    Object.values(services).every(
      (status) =>
        status === 'connected' ||
        status === 'initialized' ||
        status === 'available' ||
        status === 'healthy'
    );

  return {
    // State
    isLoading: query.isLoading,
    isError: query.isError,
    isHealthy,
    allServicesHealthy,

    // Data
    healthData: query.data,
    services,
    error: query.error,

    // Actions
    refetch: query.refetch,

    // Raw query object
    query,
  };
}

export default useHealthCheck;
