/**
 * Home Page - Main Article Generation Interface
 *
 * Primary user interface for the Jenosize AI Content Generation application.
 * Combines form input, article generation, and result display.
 */

'use client';

import React, { useState } from 'react';
import { Sparkles, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { ArticleGenerationForm } from '@/components/ArticleGenerationForm';
import { ArticleDisplay } from '@/components/ArticleDisplay';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorDisplay } from '@/components/ErrorDisplay';
import { StatusBadge } from '@/components/StatusBadge';
import { useArticleGeneration } from '@/hooks/useArticleGeneration';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { ArticleGenerationFormData } from '@/lib/validation';
import { GeneratedArticle } from '@/lib/types';

export default function HomePage() {
  const [currentArticle, setCurrentArticle] = useState<GeneratedArticle | undefined>();
  const [generationTime, setGenerationTime] = useState<number | undefined>();

  // Backend health check
  const { isHealthy, allServicesHealthy, isLoading: healthLoading } = useHealthCheck({
    enabled: true,
    refetchInterval: 30000, // Check every 30 seconds
  });

  // Article generation
  const {
    generateArticle,
    isLoading: isGenerating,
    isError,
    errorMessage,
    reset,
  } = useArticleGeneration({
    onSuccess: (data) => {
      if (data.success && data.article) {
        setCurrentArticle(data.article);
        setGenerationTime(data.generation_time_seconds);
        toast.success('Article generated successfully!', {
          icon: '✨',
        });
        // Scroll to article
        setTimeout(() => {
          document.getElementById('article-display')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
        }, 100);
      } else {
        toast.error(data.error || 'Failed to generate article');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'An error occurred');
    },
  });

  // Handle form submission
  const handleFormSubmit = (data: ArticleGenerationFormData) => {
    reset(); // Clear previous results
    setCurrentArticle(undefined);
    setGenerationTime(undefined);
    generateArticle(data);
  };

  // Handle retry on error
  const handleRetry = () => {
    reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-primary-500 to-primary-600 p-2 rounded-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Jenosize AI Content Generator
                </h1>
                <p className="text-sm text-gray-600">
                  Generate high-quality business trend and future ideas articles
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {healthLoading ? (
                <StatusBadge status="pending" label="Checking..." />
              ) : isHealthy && allServicesHealthy ? (
                <StatusBadge status="success" label="All Systems Operational" />
              ) : (
                <StatusBadge status="error" label="Service Unavailable" />
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  Article Parameters
                </h2>
                <p className="text-sm text-gray-600">
                  Configure your article generation settings
                </p>
              </div>
              <ArticleGenerationForm
                onSubmit={handleFormSubmit}
                isLoading={isGenerating}
                disabled={!isHealthy || !allServicesHealthy}
              />
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {/* Loading State */}
            {isGenerating && (
              <div className="card text-center py-16">
                <LoadingSpinner size="xl" message="Generating your article..." />
                <div className="mt-6 space-y-2">
                  <p className="text-sm text-gray-600">
                    This may take 5-30 seconds
                  </p>
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span>Analyzing topic</span>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span>Retrieving context from knowledge base</span>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500 animate-pulse">
                    <div className="h-4 w-4 rounded-full border-2 border-primary-600 border-t-transparent animate-spin" />
                    <span>Generating content...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Error State */}
            {isError && !isGenerating && (
              <div className="card">
                <ErrorDisplay
                  title="Generation Failed"
                  message={errorMessage || 'An unexpected error occurred'}
                  onRetry={handleRetry}
                />
              </div>
            )}

            {/* Success State - Show Article */}
            {currentArticle && !isGenerating && (
              <div id="article-display" className="card animate-fade-in">
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-900">
                      Article Generated Successfully
                    </p>
                    <p className="text-xs text-green-700 mt-0.5">
                      Generated in {generationTime?.toFixed(2)}s with{' '}
                      {currentArticle.metadata.word_count} words
                    </p>
                  </div>
                </div>
                <ArticleDisplay
                  article={currentArticle}
                  generationTime={generationTime}
                />
              </div>
            )}

            {/* Initial State - Welcome Message */}
            {!isGenerating && !isError && !currentArticle && (
              <div className="card text-center py-16">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full mb-4">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">
                  Welcome to Jenosize AI Content Generator
                </h2>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Configure your article parameters in the form and click
                  &quot;Generate Article&quot; to create high-quality business content
                  powered by AI.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto text-left">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="font-semibold text-gray-900 mb-2">
                      1. Set Parameters
                    </div>
                    <p className="text-sm text-gray-600">
                      Choose topic, industry, audience, and tone
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="font-semibold text-gray-900 mb-2">
                      2. Generate Content
                    </div>
                    <p className="text-sm text-gray-600">
                      AI creates your article with RAG-enhanced insights
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="font-semibold text-gray-900 mb-2">
                      3. Download & Use
                    </div>
                    <p className="text-sm text-gray-600">
                      Copy or download your article in Markdown format
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              Powered by OpenAI GPT, LangChain, and Qdrant Vector Database
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Jenosize AI Content Generation System - Built for Generative AI Engineer Position
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
