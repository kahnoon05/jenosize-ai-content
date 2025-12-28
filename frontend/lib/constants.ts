/**
 * Application Constants
 *
 * Centralized configuration values, labels, and options for the frontend.
 */

import {
  IndustryType,
  AudienceType,
  ContentTone,
  IndustryOption,
  AudienceOption,
  ToneOption,
} from './types';

/**
 * Industry options with labels and descriptions
 */
export const INDUSTRY_OPTIONS: IndustryOption[] = [
  {
    value: IndustryType.TECHNOLOGY,
    label: 'Technology',
    description: 'Software, hardware, IT services, and digital innovation',
  },
  {
    value: IndustryType.FINANCE,
    label: 'Finance',
    description: 'Banking, fintech, investment, and financial services',
  },
  {
    value: IndustryType.HEALTHCARE,
    label: 'Healthcare',
    description: 'Medical services, healthtech, pharmaceuticals, and wellness',
  },
  {
    value: IndustryType.RETAIL,
    label: 'Retail',
    description: 'E-commerce, brick-and-mortar, and consumer goods',
  },
  {
    value: IndustryType.MANUFACTURING,
    label: 'Manufacturing',
    description: 'Production, supply chain, and industrial operations',
  },
  {
    value: IndustryType.EDUCATION,
    label: 'Education',
    description: 'EdTech, training, academic institutions, and learning',
  },
  {
    value: IndustryType.REAL_ESTATE,
    label: 'Real Estate',
    description: 'Property, construction, and proptech',
  },
  {
    value: IndustryType.HOSPITALITY,
    label: 'Hospitality',
    description: 'Hotels, tourism, restaurants, and travel',
  },
  {
    value: IndustryType.AUTOMOTIVE,
    label: 'Automotive',
    description: 'Vehicles, mobility, and transportation',
  },
  {
    value: IndustryType.ENERGY,
    label: 'Energy',
    description: 'Renewable energy, oil & gas, and utilities',
  },
  {
    value: IndustryType.AGRICULTURE,
    label: 'Agriculture',
    description: 'Farming, agtech, and food production',
  },
  {
    value: IndustryType.ENTERTAINMENT,
    label: 'Entertainment',
    description: 'Media, gaming, streaming, and content creation',
  },
  {
    value: IndustryType.TELECOMMUNICATIONS,
    label: 'Telecommunications',
    description: '5G, networking, and communication services',
  },
  {
    value: IndustryType.GENERAL,
    label: 'General / Cross-Industry',
    description: 'Applicable across multiple industries',
  },
];

/**
 * Audience options with labels and descriptions
 */
export const AUDIENCE_OPTIONS: AudienceOption[] = [
  {
    value: AudienceType.EXECUTIVES,
    label: 'Executives (C-Suite)',
    description: 'CEOs, CTOs, CFOs, and senior leadership',
  },
  {
    value: AudienceType.MANAGERS,
    label: 'Managers',
    description: 'Middle management and team leaders',
  },
  {
    value: AudienceType.ENTREPRENEURS,
    label: 'Entrepreneurs',
    description: 'Startup founders and business owners',
  },
  {
    value: AudienceType.INVESTORS,
    label: 'Investors',
    description: 'VCs, angel investors, and financial stakeholders',
  },
  {
    value: AudienceType.PROFESSIONALS,
    label: 'Professionals',
    description: 'Industry professionals and subject matter experts',
  },
  {
    value: AudienceType.STUDENTS,
    label: 'Students',
    description: 'Students and early-career professionals',
  },
  {
    value: AudienceType.GENERAL_PUBLIC,
    label: 'General Public',
    description: 'Broad audience with general interest',
  },
  {
    value: AudienceType.TECHNICAL,
    label: 'Technical Audience',
    description: 'Engineers, developers, and technical specialists',
  },
  {
    value: AudienceType.NON_TECHNICAL,
    label: 'Non-Technical Audience',
    description: 'Business-focused readers without technical background',
  },
];

/**
 * Content tone options with labels and descriptions
 */
export const TONE_OPTIONS: ToneOption[] = [
  {
    value: ContentTone.PROFESSIONAL,
    label: 'Professional',
    description: 'Formal, authoritative, and business-oriented',
  },
  {
    value: ContentTone.CONVERSATIONAL,
    label: 'Conversational',
    description: 'Friendly, approachable, and engaging',
  },
  {
    value: ContentTone.ACADEMIC,
    label: 'Academic',
    description: 'Scholarly, research-focused, and detailed',
  },
  {
    value: ContentTone.INSPIRATIONAL,
    label: 'Inspirational',
    description: 'Motivational, visionary, and forward-thinking',
  },
  {
    value: ContentTone.ANALYTICAL,
    label: 'Analytical',
    description: 'Data-driven, objective, and fact-based',
  },
];

/**
 * Article length presets
 */
export const LENGTH_PRESETS = [
  { value: 1000, label: 'Short (1,000 words)', readingTime: '5-10 sec' },
  { value: 1500, label: 'Medium (1,500 words)', readingTime: '10-15 sec' },
  { value: 2000, label: 'Standard (2,000 words)', readingTime: '15-20 sec' },
  { value: 2500, label: 'Long (2,500 words)', readingTime: '20-25 sec' },
  { value: 3000, label: 'Extended (3,000 words)', readingTime: '25-30 sec' },
];

/**
 * Form field configurations
 */
export const FORM_LIMITS = {
  TOPIC_MIN_LENGTH: 3,
  TOPIC_MAX_LENGTH: 200,
  KEYWORDS_MAX_COUNT: 10,
  KEYWORD_MAX_LENGTH: 50,
  TARGET_LENGTH_MIN: 800,
  TARGET_LENGTH_MAX: 4000,
  TARGET_LENGTH_DEFAULT: 2000,
  TEMPERATURE_MIN: 0,
  TEMPERATURE_MAX: 1,
  TEMPERATURE_STEP: 0.1,
};

/**
 * API configuration
 */
export const API_CONFIG = {
  REQUEST_TIMEOUT: 180000, // 3 minutes
  RETRY_ATTEMPTS: 2,
  RETRY_DELAY: 1000, // 1 second
};

/**
 * UI configuration
 */
export const UI_CONFIG = {
  TOAST_DURATION: 5000, // 5 seconds
  DEBOUNCE_DELAY: 300, // 300ms
  ANIMATION_DURATION: 200, // 200ms
  MAX_RECENT_ARTICLES: 5,
};

/**
 * Example topics for inspiration
 */
export const EXAMPLE_TOPICS = [
  'The Future of Artificial Intelligence in Healthcare',
  'Sustainable Business Practices for 2025',
  'Digital Transformation in Traditional Industries',
  'The Rise of Remote Work and Its Impact on Corporate Culture',
  'Blockchain Technology Beyond Cryptocurrency',
  'The Evolution of E-Commerce in Southeast Asia',
  'Green Energy Solutions for Urban Development',
  'The Impact of 5G on Business Innovation',
  'Data Privacy in the Age of AI',
  'The Future of Education Technology',
];

/**
 * Status messages
 */
export const STATUS_MESSAGES = {
  GENERATING: 'Generating your article...',
  PROCESSING: 'Processing your request...',
  ANALYZING: 'Analyzing topic and gathering insights...',
  SUCCESS: 'Article generated successfully!',
  ERROR: 'Failed to generate article. Please try again.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  VALIDATION_ERROR: 'Please check your input and try again.',
};

/**
 * Keyboard shortcuts
 */
export const KEYBOARD_SHORTCUTS = {
  SUBMIT_FORM: 'Ctrl+Enter',
  COPY_CONTENT: 'Ctrl+C',
  DOWNLOAD: 'Ctrl+D',
  CLEAR_FORM: 'Ctrl+K',
};

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  RECENT_ARTICLES: 'jenosize_recent_articles',
  FORM_DRAFT: 'jenosize_form_draft',
  USER_PREFERENCES: 'jenosize_preferences',
};
