/**
 * Form Validation Schemas using Zod
 *
 * Provides client-side validation for article generation forms
 * with detailed error messages and type safety.
 */

import { z } from 'zod';
import { IndustryType, AudienceType, ContentTone } from './types';

/**
 * Article Generation Form Schema
 * Validates all input fields before submitting to the API
 */
export const articleGenerationSchema = z.object({
  // Required Fields
  topic: z
    .string()
    .min(3, 'Topic must be at least 3 characters long')
    .max(200, 'Topic must not exceed 200 characters')
    .trim()
    .refine((val) => val.length > 0, 'Topic is required'),

  // Optional Context Fields
  industry: z.nativeEnum(IndustryType).default(IndustryType.GENERAL),

  audience: z.nativeEnum(AudienceType).default(AudienceType.PROFESSIONALS),

  keywords: z
    .array(z.string().trim().min(1, 'Keyword cannot be empty'))
    .max(10, 'Maximum 10 keywords allowed')
    .optional()
    .transform((val) => {
      if (!val || val.length === 0) return undefined;
      // Remove duplicates and empty strings
      const unique = Array.from(new Set(val.filter((k) => k.length > 0)));
      return unique.length > 0 ? unique : undefined;
    }),

  // Content Parameters
  target_length: z
    .number()
    .int('Target length must be a whole number')
    .min(800, 'Minimum article length is 800 words')
    .max(4000, 'Maximum article length is 4000 words')
    .default(2000),

  tone: z.nativeEnum(ContentTone).default(ContentTone.PROFESSIONAL),

  include_examples: z.boolean().default(true),

  include_statistics: z.boolean().default(true),

  // SEO Parameters
  generate_seo_metadata: z.boolean().default(true),

  // Advanced Options
  use_rag: z.boolean().default(true),

  temperature: z
    .number()
    .min(0, 'Temperature must be at least 0')
    .max(1, 'Temperature must not exceed 1')
    .optional()
    .nullable()
    .transform((val) => (val === null ? undefined : val)),
});

/**
 * Inferred TypeScript type from the Zod schema
 */
export type ArticleGenerationFormData = z.infer<typeof articleGenerationSchema>;

/**
 * Default form values
 */
export const defaultFormValues: ArticleGenerationFormData = {
  topic: '',
  industry: IndustryType.GENERAL,
  audience: AudienceType.PROFESSIONALS,
  keywords: undefined,
  target_length: 2000,
  tone: ContentTone.PROFESSIONAL,
  include_examples: true,
  include_statistics: true,
  generate_seo_metadata: true,
  use_rag: true,
  temperature: undefined,
};

/**
 * Keywords input validation schema (for individual keyword input)
 */
export const keywordSchema = z
  .string()
  .trim()
  .min(1, 'Keyword cannot be empty')
  .max(50, 'Keyword too long (max 50 characters)');

/**
 * Validate a single keyword
 */
export const validateKeyword = (keyword: string): { valid: boolean; error?: string } => {
  const result = keywordSchema.safeParse(keyword);
  if (result.success) {
    return { valid: true };
  }
  return {
    valid: false,
    error: result.error.errors[0]?.message || 'Invalid keyword',
  };
};

/**
 * Sanitize and clean form data before submission
 */
export const sanitizeFormData = (data: ArticleGenerationFormData): ArticleGenerationFormData => {
  return {
    ...data,
    topic: data.topic.trim(),
    keywords: data.keywords?.filter((k) => k.trim().length > 0).map((k) => k.trim()),
    temperature: data.temperature === undefined || data.temperature === null ? undefined : data.temperature,
  };
};
