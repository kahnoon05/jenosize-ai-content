/**
 * Custom Hook for Fetching Supported Options
 *
 * Retrieves available industries, audiences, tones, and default parameters
 * from the backend API for form dropdowns.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient, APIError } from '@/lib/api-client';
import { SupportedOptionsResponse } from '@/lib/types';

/**
 * Hook for fetching supported options from the backend
 */
export function useSupportedOptions() {
  const query = useQuery<SupportedOptionsResponse, APIError>({
    queryKey: ['supported-options'],
    queryFn: async () => {
      return await apiClient.getSupportedOptions();
    },
    staleTime: Infinity, // Options rarely change, cache indefinitely
    gcTime: Infinity, // Keep in cache
    retry: 2,
    retryDelay: 1000,
  });

  return {
    // State
    isLoading: query.isLoading,
    isError: query.isError,
    isSuccess: query.isSuccess,

    // Data
    options: query.data,
    industries: query.data?.industries || [],
    audiences: query.data?.audiences || [],
    tones: query.data?.tones || [],
    targetLengthRange: query.data?.target_length_range,
    defaultParameters: query.data?.default_parameters,

    // Error
    error: query.error,

    // Actions
    refetch: query.refetch,

    // Raw query object
    query,
  };
}

export default useSupportedOptions;
