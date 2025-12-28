/**
 * Article Generation Form Component
 *
 * Main form for inputting article generation parameters with validation
 * and real-time feedback using React Hook Form and Zod.
 */

'use client';

import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Sparkles,
  Settings,
  ChevronDown,
  ChevronUp,
  Info,
} from 'lucide-react';
import {
  articleGenerationSchema,
  ArticleGenerationFormData,
  defaultFormValues,
} from '@/lib/validation';
import {
  INDUSTRY_OPTIONS,
  AUDIENCE_OPTIONS,
  TONE_OPTIONS,
  LENGTH_PRESETS,
  EXAMPLE_TOPICS,
  FORM_LIMITS,
} from '@/lib/constants';
import { KeywordInput } from './KeywordInput';
import { cn } from '@/lib/utils';

interface ArticleGenerationFormProps {
  onSubmit: (data: ArticleGenerationFormData) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ArticleGenerationForm({
  onSubmit,
  isLoading = false,
  disabled = false,
}: ArticleGenerationFormProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<number | null>(2000);

  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors, isValid },
  } = useForm<ArticleGenerationFormData>({
    resolver: zodResolver(articleGenerationSchema),
    defaultValues: defaultFormValues,
    mode: 'onChange',
  });

  // Handle form submission
  const onFormSubmit = (data: ArticleGenerationFormData) => {
    onSubmit(data);
  };

  // Load example topic
  const loadExampleTopic = () => {
    const randomTopic = EXAMPLE_TOPICS[Math.floor(Math.random() * EXAMPLE_TOPICS.length)];
    setValue('topic', randomTopic, { shouldValidate: true });
  };

  // Handle length preset selection
  const handlePresetSelect = (value: number) => {
    setSelectedPreset(value);
    setValue('target_length', value, { shouldValidate: true });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {/* Topic Input */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label htmlFor="topic" className="label">
            Article Topic <span className="text-red-500">*</span>
          </label>
          <button
            type="button"
            onClick={loadExampleTopic}
            className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            disabled={disabled || isLoading}
          >
            Load Example
          </button>
        </div>
        <textarea
          id="topic"
          {...register('topic')}
          placeholder="Enter the main topic or subject for your article..."
          className={cn('textarea', errors.topic && 'input-error')}
          rows={3}
          disabled={disabled || isLoading}
        />
        {errors.topic && (
          <p className="mt-1 text-sm text-red-600">{errors.topic.message}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {watch('topic')?.length || 0} / {FORM_LIMITS.TOPIC_MAX_LENGTH} characters
        </p>
      </div>

      {/* Industry Selection */}
      <div>
        <label htmlFor="industry" className="label">
          Industry
        </label>
        <select
          id="industry"
          {...register('industry')}
          className={cn('select', errors.industry && 'input-error')}
          disabled={disabled || isLoading}
        >
          {INDUSTRY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {errors.industry && (
          <p className="mt-1 text-sm text-red-600">{errors.industry.message}</p>
        )}
      </div>

      {/* Audience Selection */}
      <div>
        <label htmlFor="audience" className="label">
          Target Audience
        </label>
        <select
          id="audience"
          {...register('audience')}
          className={cn('select', errors.audience && 'input-error')}
          disabled={disabled || isLoading}
        >
          {AUDIENCE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {errors.audience && (
          <p className="mt-1 text-sm text-red-600">{errors.audience.message}</p>
        )}
      </div>

      {/* Keywords Input */}
      <div>
        <label htmlFor="keywords" className="label">
          SEO Keywords (Optional)
        </label>
        <Controller
          name="keywords"
          control={control}
          render={({ field }) => (
            <KeywordInput
              keywords={field.value || []}
              onChange={field.onChange}
              maxKeywords={FORM_LIMITS.KEYWORDS_MAX_COUNT}
              disabled={disabled || isLoading}
            />
          )}
        />
        {errors.keywords && (
          <p className="mt-1 text-sm text-red-600">{errors.keywords.message}</p>
        )}
      </div>

      {/* Target Length */}
      <div>
        <label htmlFor="target_length" className="label">
          Article Length
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
          {LENGTH_PRESETS.map((preset) => (
            <button
              key={preset.value}
              type="button"
              onClick={() => handlePresetSelect(preset.value)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-all border-2',
                selectedPreset === preset.value
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300'
              )}
              disabled={disabled || isLoading}
            >
              {preset.label}
              <span className="block text-xs opacity-75 mt-0.5">
                {preset.readingTime}
              </span>
            </button>
          ))}
        </div>
        <input
          type="number"
          id="target_length"
          {...register('target_length', { valueAsNumber: true })}
          className={cn('input', errors.target_length && 'input-error')}
          min={FORM_LIMITS.TARGET_LENGTH_MIN}
          max={FORM_LIMITS.TARGET_LENGTH_MAX}
          step={100}
          disabled={disabled || isLoading}
        />
        {errors.target_length && (
          <p className="mt-1 text-sm text-red-600">{errors.target_length.message}</p>
        )}
      </div>

      {/* Tone Selection */}
      <div>
        <label htmlFor="tone" className="label">
          Content Tone
        </label>
        <select
          id="tone"
          {...register('tone')}
          className={cn('select', errors.tone && 'input-error')}
          disabled={disabled || isLoading}
        >
          {TONE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label} - {option.description}
            </option>
          ))}
        </select>
        {errors.tone && (
          <p className="mt-1 text-sm text-red-600">{errors.tone.message}</p>
        )}
      </div>

      {/* Content Options */}
      <div className="space-y-3">
        <label className="label">Content Options</label>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              {...register('include_examples')}
              className="h-4 w-4 text-primary-600 rounded focus:ring-primary-500"
              disabled={disabled || isLoading}
            />
            <span className="text-sm text-gray-700">
              Include real-world examples and case studies
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              {...register('include_statistics')}
              className="h-4 w-4 text-primary-600 rounded focus:ring-primary-500"
              disabled={disabled || isLoading}
            />
            <span className="text-sm text-gray-700">
              Include relevant statistics and data
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              {...register('generate_seo_metadata')}
              className="h-4 w-4 text-primary-600 rounded focus:ring-primary-500"
              disabled={disabled || isLoading}
            />
            <span className="text-sm text-gray-700">
              Generate SEO metadata (description, tags)
            </span>
          </label>
        </div>
      </div>

      {/* Advanced Options */}
      <div className="border-t border-gray-200 pt-4">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          disabled={disabled || isLoading}
        >
          <Settings className="h-4 w-4" />
          Advanced Options
          {showAdvanced ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>

        {showAdvanced && (
          <div className="mt-4 space-y-4 animate-slide-up">
            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  {...register('use_rag')}
                  className="h-4 w-4 text-primary-600 rounded focus:ring-primary-500"
                  disabled={disabled || isLoading}
                />
                <span className="text-sm text-gray-700">
                  Use RAG (Retrieval-Augmented Generation)
                </span>
                <Info className="h-4 w-4 text-gray-400" title="Retrieve similar articles for better context" />
              </label>
              <p className="mt-1 ml-6 text-xs text-gray-500">
                Retrieve similar articles from the database for enhanced context
              </p>
            </div>

            <div>
              <label htmlFor="temperature" className="label">
                Temperature (Creativity)
              </label>
              <input
                type="range"
                id="temperature"
                {...register('temperature', { valueAsNumber: true })}
                min={FORM_LIMITS.TEMPERATURE_MIN}
                max={FORM_LIMITS.TEMPERATURE_MAX}
                step={FORM_LIMITS.TEMPERATURE_STEP}
                className="w-full"
                disabled={disabled || isLoading}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>More Focused</span>
                <span className="font-medium">
                  {watch('temperature')?.toFixed(1) || '0.7'}
                </span>
                <span>More Creative</span>
              </div>
              {errors.temperature && (
                <p className="mt-1 text-sm text-red-600">{errors.temperature.message}</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!isValid || disabled || isLoading}
        className="btn-primary w-full py-3 text-base font-semibold"
      >
        {isLoading ? (
          <>
            <div className="spinner h-5 w-5 mr-2" />
            Generating Article...
          </>
        ) : (
          <>
            <Sparkles className="h-5 w-5 mr-2" />
            Generate Article
          </>
        )}
      </button>

      {/* Help Text */}
      <div className="alert-info text-xs">
        <Info className="h-4 w-4 inline-block mr-1" />
        Generation typically takes 5-30 seconds depending on article length and complexity.
      </div>
    </form>
  );
}

export default ArticleGenerationForm;
