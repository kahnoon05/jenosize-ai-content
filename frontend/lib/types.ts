/**
 * Type Definitions for Jenosize AI Content Generation Frontend
 *
 * These types mirror the backend Pydantic models and provide type safety
 * for the entire frontend application.
 */

// Enums matching backend models
export enum IndustryType {
  TECHNOLOGY = "technology",
  FINANCE = "finance",
  HEALTHCARE = "healthcare",
  RETAIL = "retail",
  MANUFACTURING = "manufacturing",
  EDUCATION = "education",
  REAL_ESTATE = "real_estate",
  HOSPITALITY = "hospitality",
  AUTOMOTIVE = "automotive",
  ENERGY = "energy",
  AGRICULTURE = "agriculture",
  ENTERTAINMENT = "entertainment",
  TELECOMMUNICATIONS = "telecommunications",
  GENERAL = "general",
}

export enum AudienceType {
  EXECUTIVES = "executives",
  MANAGERS = "managers",
  ENTREPRENEURS = "entrepreneurs",
  INVESTORS = "investors",
  PROFESSIONALS = "professionals",
  STUDENTS = "students",
  GENERAL_PUBLIC = "general_public",
  TECHNICAL = "technical",
  NON_TECHNICAL = "non_technical",
}

export enum ContentTone {
  PROFESSIONAL = "professional",
  CONVERSATIONAL = "conversational",
  ACADEMIC = "academic",
  INSPIRATIONAL = "inspirational",
  ANALYTICAL = "analytical",
}

// Request/Response Types
export interface ArticleGenerationRequest {
  topic: string;
  industry?: IndustryType;
  audience?: AudienceType;
  keywords?: string[];
  target_length?: number;
  tone?: ContentTone;
  include_examples?: boolean;
  include_statistics?: boolean;
  generate_seo_metadata?: boolean;
  use_rag?: boolean;
  temperature?: number;
}

export interface ArticleMetadata {
  title: string;
  meta_description?: string;
  keywords: string[];
  reading_time_minutes: number;
  word_count: number;
  industry: string;
  audience: string;
  tone: string;
  generated_at: string;
  model_used: string;
  rag_sources_count: number;
}

export interface ArticleSection {
  title: string;
  content: string;
}

export interface GeneratedArticle {
  content: string;
  metadata: ArticleMetadata;
  sections?: ArticleSection[];
  references?: string[];
  related_topics?: string[];
}

export interface ArticleGenerationResponse {
  success: boolean;
  article?: GeneratedArticle;
  error?: string;
  generation_time_seconds: number;
  request_id?: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  services: {
    [key: string]: string;
  };
}

export interface SupportedOptionsResponse {
  industries: string[];
  audiences: string[];
  tones: string[];
  target_length_range: {
    min: number;
    max: number;
    default: number;
  };
  keywords_limit: number;
  default_parameters: {
    industry: string;
    audience: string;
    tone: string;
    target_length: number;
  };
}

export interface ErrorResponse {
  error: string;
  message: string;
  detail?: string;
  timestamp: string;
  path?: string;
}

// UI State Types
export interface FormState {
  isSubmitting: boolean;
  error?: string;
  lastGeneratedArticle?: GeneratedArticle;
}

// Display Helper Types
export interface IndustryOption {
  value: IndustryType;
  label: string;
  description?: string;
}

export interface AudienceOption {
  value: AudienceType;
  label: string;
  description?: string;
}

export interface ToneOption {
  value: ContentTone;
  label: string;
  description?: string;
}
