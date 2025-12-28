/**
 * API Constants
 *
 * Centralizes all API-related constants including timeouts, limits,
 * and error types for consistent use across the frontend.
 */

// ============================================
// API Timeout Configuration
// ============================================
export const API_TIMEOUT_DEFAULT = 120000; // 2 minutes for standard requests
export const API_TIMEOUT_ARTICLE_GENERATION = 180000; // 3 minutes for article generation
export const API_TIMEOUT_HEALTH_CHECK = 10000; // 10 seconds for health checks

// ============================================
// Validation Limits
// ============================================
export const TOPIC_MIN_LENGTH = 3;
export const TOPIC_MAX_LENGTH = 200;

export const KEYWORDS_MAX_COUNT = 10;
export const KEYWORDS_MIN_COUNT = 0;

export const TARGET_LENGTH_MIN = 800;
export const TARGET_LENGTH_MAX = 4000;

export const TEMPERATURE_MIN = 0;
export const TEMPERATURE_MAX = 1;

// ============================================
// Error Type Constants
// ============================================
export const ERROR_TYPE_VALIDATION = 'ValidationError';
export const ERROR_TYPE_NETWORK = 'NetworkError';
export const ERROR_TYPE_TIMEOUT = 'TimeoutError';
export const ERROR_TYPE_CANCEL = 'CancelError';
export const ERROR_TYPE_INTERNAL = 'InternalServerError';
export const ERROR_TYPE_UNKNOWN = 'UnknownError';

// ============================================
// Error Messages
// ============================================
export const ERROR_MSG_NO_RESPONSE = 'No response received from server. Please check your connection.';
export const ERROR_MSG_REQUEST_CANCELLED = 'Request was cancelled';
export const ERROR_MSG_UNKNOWN = 'An unknown error occurred';

// ============================================
// HTTP Status Codes
// ============================================
export const HTTP_STATUS_SUCCESS = 200;
export const HTTP_STATUS_VALIDATION_ERROR = 422;
export const HTTP_STATUS_INTERNAL_ERROR = 500;

// ============================================
// Retry Configuration
// ============================================
export const MUTATION_RETRY_COUNT = 1;
export const MUTATION_RETRY_DELAY = 1000; // 1 second
