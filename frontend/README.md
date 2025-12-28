# Jenosize AI Content Generation - Frontend

A modern Next.js 14 application for generating high-quality business trend and future ideas articles using AI.

## Features

- **Modern UI/UX**: Built with Next.js 14 App Router, React 18, and Tailwind CSS
- **Form Validation**: React Hook Form with Zod schemas for robust input validation
- **Real-time Feedback**: TanStack Query for optimized data fetching and caching
- **Article Generation**: Customizable parameters for topic, industry, audience, and tone
- **Rich Display**: Markdown rendering with syntax highlighting and proper formatting
- **Responsive Design**: Mobile-first, fully responsive layout
- **Toast Notifications**: User-friendly feedback for all actions
- **Copy & Download**: Easy content export functionality
- **Health Monitoring**: Real-time backend health status checking

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Form Management**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Markdown Rendering**: react-markdown + remark-gfm
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## Prerequisites

- Node.js 18.0.0 or higher
- npm 9.0.0 or higher
- Backend API running on http://localhost:8000

## Installation

1. **Install Dependencies**

```bash
npm install
```

2. **Configure Environment Variables**

Create a `.env.local` file in the root directory:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Application Settings
NEXT_PUBLIC_APP_NAME=Jenosize AI Content Generator
NEXT_PUBLIC_APP_DESCRIPTION=Generate high-quality business trend and future ideas articles
```

3. **Start Development Server**

```bash
npm run dev
```

The application will be available at http://localhost:3000

## Project Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── layout.tsx             # Root layout with metadata
│   ├── page.tsx               # Main homepage
│   ├── providers.tsx          # React Query provider
│   └── globals.css            # Global styles
├── components/                 # React components
│   ├── ArticleDisplay.tsx     # Article display with formatting
│   ├── ArticleGenerationForm.tsx # Main generation form
│   ├── ErrorDisplay.tsx       # Error handling component
│   ├── KeywordInput.tsx       # Keyword input with validation
│   ├── LoadingSpinner.tsx     # Loading indicators
│   └── StatusBadge.tsx        # Status badges
├── hooks/                      # Custom React hooks
│   ├── useArticleGeneration.ts # Article generation hook
│   ├── useHealthCheck.ts      # Backend health check
│   └── useSupportedOptions.ts # Fetch supported options
├── lib/                        # Utilities and helpers
│   ├── api-client.ts          # API client with error handling
│   ├── constants.ts           # Application constants
│   ├── types.ts               # TypeScript type definitions
│   ├── utils.ts               # Utility functions
│   └── validation.ts          # Zod validation schemas
├── public/                     # Static assets
├── .env.local                 # Environment variables
├── next.config.js             # Next.js configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies and scripts
```

## Available Scripts

```bash
# Development
npm run dev              # Start development server
npm run build            # Build for production
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking
```

## Key Components

### ArticleGenerationForm
Main form component with:
- Topic input with example loader
- Industry, audience, and tone selectors
- Keyword management (up to 10 keywords)
- Article length presets (1,000 - 3,000 words)
- Advanced options (RAG toggle, temperature control)
- Real-time validation with error messages

### ArticleDisplay
Displays generated articles with:
- Formatted markdown content
- Metadata (word count, reading time, generation time)
- Copy to clipboard and download functionality
- SEO keywords and tags
- Related topics and references
- RAG sources information

### API Integration
- Type-safe API client with Axios
- Automatic retry on failure
- Request/response transformation
- Comprehensive error handling
- Cancel token support for request cancellation

## Form Validation

All inputs are validated using Zod schemas:

```typescript
- Topic: 3-200 characters, required
- Keywords: Max 10, each max 50 characters
- Target Length: 800-4000 words
- Temperature: 0-1 (optional)
```

## API Endpoints Used

```
GET  /health                        # Backend health check
GET  /api/v1/supported-options     # Get dropdown options
POST /api/v1/generate-article      # Generate article
```

## Styling

The application uses a custom Tailwind CSS theme with:

- **Primary Colors**: Blue shades for main actions
- **Secondary Colors**: Purple accents
- **Accent Colors**: Orange for highlights
- **Responsive Breakpoints**: Mobile-first design
- **Custom Components**: Button, input, card, badge, alert styles
- **Animations**: Fade-in, slide-up, pulse effects

## Error Handling

Comprehensive error handling includes:

1. **Network Errors**: Connection issues display user-friendly messages
2. **Validation Errors**: Real-time form validation with detailed feedback
3. **API Errors**: Backend errors parsed and displayed appropriately
4. **Timeout Handling**: 3-minute timeout for article generation
5. **Retry Logic**: Automatic retry with exponential backoff

## Performance Optimizations

- **React Query Caching**: Efficient data caching and revalidation
- **Code Splitting**: Automatic code splitting with Next.js
- **Image Optimization**: Next.js automatic image optimization
- **Font Optimization**: Optimized Google Fonts loading
- **Production Build**: Minified and optimized for production

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify environment variables
cat .env.local
```

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install

# Run type checking
npm run type-check
```

### CORS Issues
Ensure backend CORS settings allow frontend origin:
```python
# backend/app/core/config.py
cors_origins = ["http://localhost:3000"]
```

---

**Built with love for the Jenosize Generative AI Engineer position**
