/**
 * Custom Hook for Article Generation
 *
 * Handles article generation logic, state management, and API communication
 * using TanStack Query for optimal caching and error handling.
 */

import { useMutation, UseMutationResult } from '@tanstack/react-query';
import { apiClient, APIError } from '@/lib/api-client';
import {
  ArticleGenerationRequest,
  ArticleGenerationResponse,
  GeneratedArticle,
} from '@/lib/types';
import { useCallback } from 'react';

interface UseArticleGenerationOptions {
  onSuccess?: (data: ArticleGenerationResponse) => void;
  onError?: (error: APIError) => void;
}

/**
 * Hook for article generation with loading states and error handling
 */
export function useArticleGeneration(options?: UseArticleGenerationOptions) {
  const mutation: UseMutationResult<
    ArticleGenerationResponse,
    APIError,
    ArticleGenerationRequest
  > = useMutation({
    mutationFn: async (request: ArticleGenerationRequest) => {
      return await apiClient.generateArticle(request);
    },
    onSuccess: (data) => {
      if (options?.onSuccess) {
        options.onSuccess(data);
      }
    },
    onError: (error: APIError) => {
      if (options?.onError) {
        options.onError(error);
      }
    },
    retry: 1, // Retry once on failure
    retryDelay: 1000, // 1 second delay before retry
  });

  /**
   * Generate article with the provided parameters
   */
  const generateArticle = useCallback(
    (request: ArticleGenerationRequest) => {
      return mutation.mutate(request);
    },
    [mutation]
  );

  /**
   * Get the generated article from the response
   */
  const article: GeneratedArticle | undefined = mutation.data?.article;

  /**
   * Check if generation was successful
   */
  const isSuccess: boolean = mutation.isSuccess && mutation.data?.success === true;

  /**
   * Get error message if generation failed
   */
  const errorMessage: string | undefined = mutation.error?.message || mutation.data?.error;

  /**
   * Get generation time in seconds
   */
  const generationTime: number | undefined = mutation.data?.generation_time_seconds;

  /**
   * Reset mutation state (clear generated article and errors)
   */
  const reset = useCallback(() => {
    mutation.reset();
  }, [mutation]);

  return {
    // State
    isLoading: mutation.isPending,
    isError: mutation.isError || mutation.data?.success === false,
    isSuccess,
    article,
    errorMessage,
    generationTime,

    // Actions
    generateArticle,
    reset,

    // Raw mutation object for advanced use cases
    mutation,
  };
}

export default useArticleGeneration;
