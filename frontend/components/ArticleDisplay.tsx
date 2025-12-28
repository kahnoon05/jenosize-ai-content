/**
 * Article Display Component
 *
 * Displays generated articles with proper formatting, metadata,
 * and action buttons (copy, download, share).
 */

'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Copy,
  Download,
  Check,
  Clock,
  FileText,
  Tag,
  Calendar,
  Sparkles,
  Database,
} from 'lucide-react';
import { GeneratedArticle } from '@/lib/types';
import {
  formatNumber,
  formatRelativeTime,
  formatDuration,
  copyToClipboard,
  downloadAsFile,
  generateFilename,
  enumToLabel,
} from '@/lib/utils';
import { StatusBadge } from './StatusBadge';

interface ArticleDisplayProps {
  article: GeneratedArticle;
  generationTime?: number;
  className?: string;
}

export function ArticleDisplay({
  article,
  generationTime,
  className,
}: ArticleDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(article.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const filename = generateFilename(article.metadata.title, 'md');
    downloadAsFile(article.content, filename, 'text/markdown');
  };

  return (
    <div className={className}>
      {/* Header with Actions */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div className="flex-1 min-w-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {article.metadata.title}
          </h1>
          {article.metadata.meta_description && (
            <p className="text-gray-600 text-lg">
              {article.metadata.meta_description}
            </p>
          )}
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={handleCopy}
            className="btn-secondary"
            title="Copy to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 mr-2 text-green-600" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="btn-secondary"
            title="Download as Markdown"
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </button>
        </div>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-gray-500" />
          <div>
            <p className="text-xs text-gray-500">Reading Time</p>
            <p className="text-sm font-medium text-gray-900">
              {article.metadata.reading_time_minutes} min
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-gray-500" />
          <div>
            <p className="text-xs text-gray-500">Word Count</p>
            <p className="text-sm font-medium text-gray-900">
              {formatNumber(article.metadata.word_count)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-gray-500" />
          <div>
            <p className="text-xs text-gray-500">Generated</p>
            <p className="text-sm font-medium text-gray-900">
              {formatRelativeTime(article.metadata.generated_at)}
            </p>
          </div>
        </div>
        {generationTime !== undefined && (
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Generation Time</p>
              <p className="text-sm font-medium text-gray-900">
                {formatDuration(generationTime)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Tags and Metadata */}
      <div className="mb-6 space-y-3">
        {/* Industry & Audience */}
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-sm text-gray-600">Industry:</span>
          <StatusBadge status="info" label={enumToLabel(article.metadata.industry)} showIcon={false} />
          <span className="text-sm text-gray-600 ml-3">Audience:</span>
          <StatusBadge status="info" label={enumToLabel(article.metadata.audience)} showIcon={false} />
          <span className="text-sm text-gray-600 ml-3">Tone:</span>
          <StatusBadge status="info" label={enumToLabel(article.metadata.tone)} showIcon={false} />
        </div>

        {/* Keywords */}
        {article.metadata.keywords && article.metadata.keywords.length > 0 && (
          <div className="flex flex-wrap gap-2 items-start">
            <Tag className="h-4 w-4 text-gray-500 mt-1" />
            <div className="flex flex-wrap gap-2 flex-1">
              {article.metadata.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* RAG Sources */}
        {article.metadata.rag_sources_count > 0 && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Database className="h-4 w-4" />
            <span>
              Enhanced with insights from {article.metadata.rag_sources_count} similar articles
            </span>
          </div>
        )}

        {/* Model Used */}
        <div className="text-xs text-gray-500">
          Generated by: {article.metadata.model_used}
        </div>
      </div>

      {/* Article Content */}
      <div className="prose prose-lg max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl font-bold text-gray-900 mt-8 mb-4 border-b border-gray-200 pb-3">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-2xl font-bold text-gray-900 mt-6 mb-3 border-b border-gray-200 pb-2">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-xl font-semibold text-gray-900 mt-5 mb-2">
                {children}
              </h3>
            ),
            h4: ({ children }) => (
              <h4 className="text-lg font-semibold text-gray-900 mt-4 mb-2">
                {children}
              </h4>
            ),
            p: ({ children }) => (
              <p className="text-gray-700 leading-relaxed mb-4">
                {children}
              </p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside text-gray-700 mb-4 space-y-2">
                {children}
              </ol>
            ),
            li: ({ children }) => (
              <li className="ml-4">{children}</li>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-primary-500 pl-4 italic text-gray-700 my-4 bg-gray-50 py-2">
                {children}
              </blockquote>
            ),
            code: ({ children, className }) => {
              const isInline = !className;
              return isInline ? (
                <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono">
                  {children}
                </code>
              ) : (
                <code className={className}>{children}</code>
              );
            },
            pre: ({ children }) => (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                {children}
              </pre>
            ),
            a: ({ children, href }) => (
              <a
                href={href}
                className="text-primary-600 hover:text-primary-700 underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            ),
            strong: ({ children }) => (
              <strong className="font-semibold text-gray-900">
                {children}
              </strong>
            ),
            em: ({ children }) => (
              <em className="italic">{children}</em>
            ),
          }}
        >
          {article.content}
        </ReactMarkdown>
      </div>

      {/* Related Topics */}
      {article.related_topics && article.related_topics.length > 0 && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Related Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {article.related_topics.map((topic, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-white text-gray-700 border border-gray-300 hover:border-primary-300 transition-colors"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* References */}
      {article.references && article.references.length > 0 && (
        <div className="mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            References & Sources
          </h3>
          <ul className="space-y-2">
            {article.references.map((reference, index) => (
              <li key={index} className="text-sm text-gray-700">
                {index + 1}. {reference}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ArticleDisplay;
