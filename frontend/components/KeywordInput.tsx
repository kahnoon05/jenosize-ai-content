/**
 * Keyword Input Component
 *
 * Allows users to add and remove keywords with validation.
 */

import React, { useState, KeyboardEvent } from 'react';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { validateKeyword } from '@/lib/validation';

interface KeywordInputProps {
  keywords: string[];
  onChange: (keywords: string[]) => void;
  maxKeywords?: number;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function KeywordInput({
  keywords,
  onChange,
  maxKeywords = 10,
  placeholder = 'Add keyword and press Enter',
  className,
  disabled = false,
}: KeywordInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState<string | undefined>();

  const addKeyword = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    // Validate keyword
    const validation = validateKeyword(trimmed);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }

    // Check for duplicates
    if (keywords.includes(trimmed)) {
      setError('Keyword already added');
      return;
    }

    // Check max limit
    if (keywords.length >= maxKeywords) {
      setError(`Maximum ${maxKeywords} keywords allowed`);
      return;
    }

    // Add keyword
    onChange([...keywords, trimmed]);
    setInputValue('');
    setError(undefined);
  };

  const removeKeyword = (index: number) => {
    onChange(keywords.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addKeyword();
    } else if (e.key === 'Backspace' && !inputValue && keywords.length > 0) {
      // Remove last keyword on backspace if input is empty
      removeKeyword(keywords.length - 1);
    }
  };

  return (
    <div className={cn('space-y-2', className)}>
      {/* Keywords Display */}
      {keywords.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {keywords.map((keyword, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium"
            >
              {keyword}
              <button
                type="button"
                onClick={() => removeKeyword(index)}
                disabled={disabled}
                className="hover:bg-primary-200 rounded-full p-0.5 transition-colors disabled:opacity-50"
                aria-label={`Remove keyword: ${keyword}`}
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Input Field */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setError(undefined);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || keywords.length >= maxKeywords}
          className={cn('input flex-1', error && 'input-error')}
          maxLength={50}
        />
        <button
          type="button"
          onClick={addKeyword}
          disabled={disabled || !inputValue.trim() || keywords.length >= maxKeywords}
          className="btn-primary px-3"
          aria-label="Add keyword"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Error Message */}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Counter */}
      <p className="text-xs text-gray-500">
        {keywords.length} / {maxKeywords} keywords
      </p>
    </div>
  );
}

export default KeywordInput;
