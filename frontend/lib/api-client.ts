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
import {
  API_TIMEOUT_DEFAULT,
  API_TIMEOUT_ARTICLE_GENERATION,
  ERROR_TYPE_NETWORK,
  ERROR_TYPE_UNKNOWN,
  ERROR_TYPE_CANCEL,
  ERROR_MSG_NO_RESPONSE,
  ERROR_MSG_REQUEST_CANCELLED,
  ERROR_MSG_UNKNOWN,
  TOPIC_MIN_LENGTH,
  KEYWORDS_MAX_COUNT,
  TARGET_LENGTH_MIN,
  TARGET_LENGTH_MAX,
  TEMPERATURE_MIN,
  TEMPERATURE_MAX,
} from './api-constants';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';

/**
 * Custom error class for API errors with enhanced error information
 *
 * Provides structured error information including status codes, error types,
 * and detailed messages for better error handling and user feedback.
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
      // Server responded with error
      this._handleServerError(error);
    } else if (error?.request) {
      // Request made but no response received
      this._handleNetworkError();
    } else {
      // Other errors (e.g., request setup issues)
      this._handleUnknownError(error);
    }
  }

  private _handleServerError(error: any): void {
    const errorData = error.response.data as ErrorResponse;
    this.statusCode = error.response.status;
    this.errorType = errorData.error;
    this.detail = errorData.detail;
    this.path = errorData.path;
  }

  private _handleNetworkError(): void {
    this.statusCode = 0;
    this.errorType = ERROR_TYPE_NETWORK;
    this.detail = ERROR_MSG_NO_RESPONSE;
  }

  private _handleUnknownError(error: any): void {
    this.errorType = ERROR_TYPE_UNKNOWN;
    this.detail = error?.message || ERROR_MSG_UNKNOWN;
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
      timeout: API_TIMEOUT_DEFAULT,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    this._setupInterceptors();
  }

  /**
   * Setup axios interceptors for logging and error handling
   *
   * Configures request and response interceptors for debugging in development
   * and consistent error handling across all requests.
   */
  private _setupInterceptors(): void {
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
      this._validateGenerationRequest(request);

      const response = await this.client.post<ArticleGenerationResponse>(
        `/api/${API_VERSION}/generate-article`,
        request,
        {
          ...config,
          // Use longer timeout for article generation
          timeout: config?.timeout || API_TIMEOUT_ARTICLE_GENERATION,
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isCancel(error)) {
        throw new APIError(ERROR_MSG_REQUEST_CANCELLED, error);
      }
      throw new APIError('Failed to generate article', error);
    }
  }

  /**
   * Validate generation request before sending to API
   *
   * Provides client-side validation for better UX by catching errors
   * before making the API request.
   *
   * @throws {APIError} If validation fails
   */
  private _validateGenerationRequest(request: ArticleGenerationRequest): void {
    // Validate topic
    if (!request.topic || request.topic.trim().length < TOPIC_MIN_LENGTH) {
      throw new APIError(`Topic must be at least ${TOPIC_MIN_LENGTH} characters long`);
    }

    // Validate keywords count
    if (request.keywords && request.keywords.length > KEYWORDS_MAX_COUNT) {
      throw new APIError(`Maximum ${KEYWORDS_MAX_COUNT} keywords allowed`);
    }

    // Validate target length
    if (request.target_length !== undefined) {
      if (request.target_length < TARGET_LENGTH_MIN || request.target_length > TARGET_LENGTH_MAX) {
        throw new APIError(
          `Target length must be between ${TARGET_LENGTH_MIN} and ${TARGET_LENGTH_MAX} words`
        );
      }
    }

    // Validate temperature
    if (request.temperature !== undefined) {
      if (request.temperature < TEMPERATURE_MIN || request.temperature > TEMPERATURE_MAX) {
        throw new APIError(
          `Temperature must be between ${TEMPERATURE_MIN} and ${TEMPERATURE_MAX}`
        );
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
