/**
 * API Client for Jenosize AI Content Generation Backend
 *
 * Provides type-safe HTTP client for all API endpoints with proper
 * error handling, request/response transformation, and timeout management.
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import {
  ArticleGenerationRequest,
  ArticleGenerationResponse,
  HealthResponse,
  SupportedOptionsResponse,
  ErrorResponse,
} from './types';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
const API_TIMEOUT = 120000; // 2 minutes for article generation

/**
 * Custom error class for API errors with enhanced error information
 */
export class APIError extends Error {
  statusCode?: number;
  errorType?: string;
  detail?: string;
  path?: string;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructor(message: string, error?: any) {
    super(message);
    this.name = 'APIError';

    if (error?.response?.data) {
      const errorData = error.response.data as ErrorResponse;
      this.statusCode = error.response.status;
      this.errorType = errorData.error;
      this.detail = errorData.detail;
      this.path = errorData.path;
    } else if (error?.request) {
      this.statusCode = 0;
      this.errorType = 'NetworkError';
      this.detail = 'No response received from server. Please check your connection.';
    } else {
      this.errorType = 'UnknownError';
      this.detail = error?.message || 'An unknown error occurred';
    }
  }

  toString(): string {
    return `${this.name}: ${this.message} (${this.errorType})${this.detail ? `\n${this.detail}` : ''}`;
  }
}

/**
 * API Client Class
 */
class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Request interceptor for logging (development only)
    if (process.env.NODE_ENV === 'development') {
      this.client.interceptors.request.use(
        (config) => {
          console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            params: config.params,
          });
          return config;
        },
        (error) => {
          console.error('[API Request Error]', error);
          return Promise.reject(error);
        }
      );
    }

    // Response interceptor for logging and error transformation
    this.client.interceptors.response.use(
      (response) => {
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API Response] ${response.config.url}`, {
            status: response.status,
            data: response.data,
          });
        }
        return response;
      },
      (error: AxiosError) => {
        console.error('[API Response Error]', {
          url: error.config?.url,
          status: error.response?.status,
          data: error.response?.data,
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Health check endpoint
   * Verifies backend API connectivity and service status
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>('/health');
      return response.data;
    } catch (error) {
      throw new APIError('Health check failed', error);
    }
  }

  /**
   * Get supported options for form dropdowns
   * Returns available industries, audiences, tones, and default parameters
   */
  async getSupportedOptions(): Promise<SupportedOptionsResponse> {
    try {
      const response = await this.client.get<SupportedOptionsResponse>(
        `/api/${API_VERSION}/supported-options`
      );
      return response.data;
    } catch (error) {
      throw new APIError('Failed to fetch supported options', error);
    }
  }

  /**
   * Generate article endpoint
   * Main endpoint for generating articles based on user parameters
   *
   * @param request - Article generation parameters
   * @param config - Optional Axios request configuration (e.g., for cancel tokens)
   * @returns Generated article with metadata
   */
  async generateArticle(
    request: ArticleGenerationRequest,
    config?: AxiosRequestConfig
  ): Promise<ArticleGenerationResponse> {
    try {
      // Validate request before sending
      this.validateGenerationRequest(request);

      const response = await this.client.post<ArticleGenerationResponse>(
        `/api/${API_VERSION}/generate-article`,
        request,
        {
          ...config,
          // Allow longer timeout for article generation
          timeout: config?.timeout || 180000, // 3 minutes
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isCancel(error)) {
        throw new APIError('Request was cancelled', error);
      }
      throw new APIError('Failed to generate article', error);
    }
  }

  /**
   * Validate generation request before sending to API
   * Provides client-side validation for better UX
   */
  private validateGenerationRequest(request: ArticleGenerationRequest): void {
    if (!request.topic || request.topic.trim().length < 3) {
      throw new APIError('Topic must be at least 3 characters long');
    }

    if (request.keywords && request.keywords.length > 10) {
      throw new APIError('Maximum 10 keywords allowed');
    }

    if (request.target_length) {
      if (request.target_length < 800 || request.target_length > 4000) {
        throw new APIError('Target length must be between 800 and 4000 words');
      }
    }

    if (request.temperature !== undefined) {
      if (request.temperature < 0 || request.temperature > 1) {
        throw new APIError('Temperature must be between 0 and 1');
      }
    }
  }

  /**
   * Create a cancel token for request cancellation
   * Useful for implementing request cancellation on component unmount
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createCancelToken(): { token: any; cancel: any } {
    const CancelToken = axios.CancelToken;
    const source = CancelToken.source();
    return {
      token: source.token,
      cancel: source.cancel,
    };
  }

  /**
   * Check if error is a cancel error
   */
  isCancelError(error: any): boolean {
    return axios.isCancel(error);
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing or custom instances
export default APIClient;
