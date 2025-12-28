# Frontend Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Next.js 14 Application                        │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                App Router (RSC)                      │ │ │
│  │  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │ │ │
│  │  │  │ layout.tsx │  │ providers.tsx│  │  page.tsx   │ │ │ │
│  │  │  └────────────┘  └──────────────┘  └─────────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                React Components                      │ │ │
│  │  │  ┌──────────────────┐  ┌────────────────────────┐  │ │ │
│  │  │  │ Form Component   │  │  Display Component     │  │ │ │
│  │  │  │                  │  │                        │  │ │ │
│  │  │  │ - Topic Input    │  │ - Markdown Renderer    │  │ │ │
│  │  │  │ - Dropdowns      │  │ - Metadata Display     │  │ │ │
│  │  │  │ - Keywords       │  │ - Copy/Download        │  │ │ │
│  │  │  │ - Validation     │  │ - Related Topics       │  │ │ │
│  │  │  └──────────────────┘  └────────────────────────┘  │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │ │ │
│  │  │  │   Loading    │  │    Error     │  │  Status  │ │ │ │
│  │  │  │   Spinner    │  │   Display    │  │  Badge   │ │ │ │
│  │  │  └──────────────┘  └──────────────┘  └──────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                Custom Hooks                          │ │ │
│  │  │  ┌──────────────────┐  ┌────────────────────────┐  │ │ │
│  │  │  │ Article Generate │  │   Health Check         │  │ │ │
│  │  │  │  - Mutation      │  │   - Query              │  │ │ │
│  │  │  │  - Loading State │  │   - 30s interval       │  │ │ │
│  │  │  │  - Error Handle  │  │   - Service status     │  │ │ │
│  │  │  └──────────────────┘  └────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │              TanStack Query Layer                    │ │ │
│  │  │  ┌────────────┐  ┌──────────┐  ┌────────────────┐  │ │ │
│  │  │  │   Cache    │  │  Retry   │  │  Deduplication │  │ │ │
│  │  │  │  Manager   │  │  Logic   │  │    Manager     │  │ │ │
│  │  │  └────────────┘  └──────────┘  └────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                  API Client                          │ │ │
│  │  │  ┌────────────────────────────────────────────────┐ │ │ │
│  │  │  │              Axios Instance                    │ │ │ │
│  │  │  │  - Request Interceptor (logging)               │ │ │ │
│  │  │  │  - Response Interceptor (error transform)      │ │ │ │
│  │  │  │  - Timeout: 3 minutes                          │ │ │ │
│  │  │  │  - Base URL: http://localhost:8000             │ │ │ │
│  │  │  └────────────────────────────────────────────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │              Validation Layer (Zod)                  │ │ │
│  │  │  - Schema validation                                 │ │ │
│  │  │  - Type inference                                    │ │ │
│  │  │  - Error messages                                    │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ HTTP/REST API
                           │ (Axios)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                  http://localhost:8000                           │
│                                                                  │
│  ┌────────────────────┐  ┌─────────────────────────────────┐   │
│  │  /health           │  │  /api/v1/generate-article       │   │
│  │  - Service status  │  │  - Article generation           │   │
│  └────────────────────┘  └─────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  /api/v1/supported-options                             │    │
│  │  - Industries, audiences, tones                        │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App (layout.tsx)
│
├─ Providers (React Query)
│  │
│  └─ Toaster (react-hot-toast)
│
└─ Page (page.tsx)
   │
   ├─ Header
   │  ├─ Logo
   │  ├─ Title
   │  └─ StatusBadge (Health Check)
   │
   ├─ Main Content
   │  │
   │  ├─ Left Column (Form)
   │  │  └─ ArticleGenerationForm
   │  │     ├─ Topic Input (textarea)
   │  │     ├─ Industry Select
   │  │     ├─ Audience Select
   │  │     ├─ KeywordInput Component
   │  │     ├─ Length Presets
   │  │     ├─ Tone Select
   │  │     ├─ Content Options (checkboxes)
   │  │     ├─ Advanced Options (collapsible)
   │  │     │  ├─ RAG Toggle
   │  │     │  └─ Temperature Slider
   │  │     └─ Submit Button
   │  │
   │  └─ Right Column (Results)
   │     │
   │     ├─ Initial State (Welcome Message)
   │     │
   │     ├─ Loading State
   │     │  └─ LoadingSpinner
   │     │     ├─ Spinner Animation
   │     │     └─ Progress Messages
   │     │
   │     ├─ Error State
   │     │  └─ ErrorDisplay
   │     │     ├─ Error Icon
   │     │     ├─ Error Message
   │     │     ├─ Details (collapsible)
   │     │     └─ Retry Button
   │     │
   │     └─ Success State
   │        └─ ArticleDisplay
   │           ├─ Success Banner
   │           ├─ Action Buttons (Copy, Download)
   │           ├─ Metadata Grid
   │           ├─ Tags (Industry, Audience, Tone)
   │           ├─ Keywords
   │           ├─ Article Content (Markdown)
   │           ├─ Related Topics
   │           └─ References
   │
   └─ Footer
      └─ Credits & Info
```

## Data Flow

### 1. Form Submission Flow
```
User Input
    ↓
React Hook Form (validation)
    ↓
Zod Schema Validation
    ↓
[Valid] → Form Submit Handler
    ↓
useArticleGeneration Hook
    ↓
TanStack Query Mutation
    ↓
API Client (Axios)
    ↓
POST /api/v1/generate-article
    ↓
[Response] → Transform Data
    ↓
Update UI State
    ↓
Display Article
```

### 2. Health Check Flow
```
Component Mount
    ↓
useHealthCheck Hook
    ↓
TanStack Query
    ↓
GET /health (every 30s)
    ↓
[Response] → Update Status Badge
    ↓
Show "Healthy" / "Unavailable"
```

### 3. Error Handling Flow
```
API Request
    ↓
[Error Occurs]
    ↓
Axios Interceptor (catch)
    ↓
Transform to APIError
    ↓
TanStack Query Error Handler
    ↓
Hook onError Callback
    ↓
Toast Notification
    ↓
ErrorDisplay Component
    ↓
Show Error + Retry Option
```

## State Management

### Local Component State
```typescript
// UI State
const [showAdvanced, setShowAdvanced] = useState(false);
const [copied, setCopied] = useState(false);
const [selectedPreset, setSelectedPreset] = useState(2000);
```

### Form State (React Hook Form)
```typescript
const { register, control, watch, handleSubmit, formState } = useForm({
  resolver: zodResolver(schema),
  defaultValues: {...},
  mode: 'onChange'
});
```

### Server State (TanStack Query)
```typescript
// Queries
useQuery(['health'], healthCheckFn, { refetchInterval: 30000 });
useQuery(['supported-options'], optionsFn, { staleTime: Infinity });

// Mutations
useMutation(generateArticleFn, {
  onSuccess: (data) => { /* update UI */ },
  onError: (error) => { /* show error */ }
});
```

## API Integration Architecture

### API Client Structure
```typescript
class APIClient {
  private client: AxiosInstance;

  constructor() {
    // Initialize Axios with config
    // Add interceptors
  }

  async healthCheck(): Promise<HealthResponse>
  async getSupportedOptions(): Promise<SupportedOptionsResponse>
  async generateArticle(request): Promise<ArticleGenerationResponse>

  private validateGenerationRequest(request): void
  createCancelToken(): { token, cancel }
}
```

### Request/Response Pipeline
```
Request
  ↓
Validation (client-side)
  ↓
Axios Request Interceptor
  - Add headers
  - Log request (dev)
  ↓
HTTP Request → Backend
  ↓
Response
  ↓
Axios Response Interceptor
  - Log response (dev)
  - Transform errors
  ↓
Return to caller
```

## Type System

### Type Flow
```
Backend Pydantic Models
    ↓
Frontend TypeScript Types (lib/types.ts)
    ↓
Zod Schemas (lib/validation.ts)
    ↓
React Hook Form Types
    ↓
Component Props
    ↓
Rendered UI
```

### Type Safety Layers
1. **TypeScript Compiler** - Compile-time checks
2. **Zod Validation** - Runtime validation
3. **React Hook Form** - Form-level validation
4. **API Client** - Request/response types

## Styling Architecture

### Tailwind CSS Structure
```
tailwind.config.js
    ↓
Theme Configuration
  - Colors (primary, secondary, accent)
  - Fonts (Inter)
  - Animations
  - Breakpoints
    ↓
globals.css
  - @tailwind directives
  - Custom components (@layer components)
  - Utility classes (@layer utilities)
    ↓
Component Classes
  - Inline Tailwind utilities
  - Custom component classes (btn, input, card)
    ↓
Rendered Styles
```

### Component Styling Pattern
```typescript
// 1. Define base styles
const baseClasses = "btn px-4 py-2";

// 2. Add conditional styles
const variantClasses = isPrimary ? "btn-primary" : "btn-secondary";

// 3. Merge with cn() utility
const finalClasses = cn(baseClasses, variantClasses, className);

// 4. Apply to element
<button className={finalClasses}>Click</button>
```

## Performance Optimizations

### 1. Code Splitting
- Automatic route-based splitting (Next.js)
- Dynamic imports for heavy components
- Lazy loading of markdown renderer

### 2. Caching Strategy
```typescript
// React Query Cache
{
  queries: {
    staleTime: 5 * 60 * 1000,  // 5 minutes
    gcTime: 10 * 60 * 1000,     // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2
  }
}
```

### 3. Memoization
- React.memo for pure components
- useMemo for expensive calculations
- useCallback for stable function references

### 4. Bundle Optimization
- Tree shaking (remove unused code)
- Minification
- Compression (gzip/brotli)

## Error Boundaries

### Error Handling Hierarchy
```
Global Error Boundary (Next.js)
    ↓
Page-level Error Handling
    ↓
Component-level Try/Catch
    ↓
Hook-level Error Callbacks
    ↓
API-level Error Transformation
    ↓
User-facing Error Display
```

## Security Considerations

### 1. Input Sanitization
- Zod validation prevents injection
- React escapes content by default
- No dangerouslySetInnerHTML used

### 2. API Security
- CORS configuration in backend
- No sensitive data in frontend
- Environment variables for configuration

### 3. Content Security
- Markdown renderer configured safely
- Links open in new tab with noopener
- XSS protection via React

## Accessibility (a11y)

### WCAG 2.1 AA Compliance
- Semantic HTML (header, main, footer)
- ARIA labels for icons and buttons
- Keyboard navigation support
- Focus indicators
- Color contrast ratios met
- Screen reader friendly

## Testing Strategy

### Unit Tests (Future)
```typescript
// Component tests
test('ArticleGenerationForm validates topic input', () => {});
test('KeywordInput prevents duplicates', () => {});

// Hook tests
test('useArticleGeneration handles success', () => {});
test('useHealthCheck polls correctly', () => {});

// Utility tests
test('copyToClipboard works', () => {});
test('formatDuration formats correctly', () => {});
```

### Integration Tests (Future)
```typescript
// API integration
test('generates article end-to-end', () => {});
test('handles backend errors gracefully', () => {});
```

### E2E Tests (Future)
```typescript
// User flows
test('user can generate article', () => {});
test('user can copy and download article', () => {});
```

## Deployment Architecture

### Development
```
localhost:3000 (Next.js dev server)
    ↓
Hot Module Replacement
Fast Refresh
Source Maps
Debug Mode
```

### Production
```
npm run build
    ↓
Next.js Build Process
  - Optimize code
  - Generate static pages
  - Create server bundles
    ↓
npm run start
    ↓
Production Server (http://localhost:3000)
```

### Docker Deployment
```
Dockerfile
    ↓
Build Stage
  - Install dependencies
  - Build Next.js app
    ↓
Production Stage
  - Copy build artifacts
  - Minimal runtime
    ↓
Container (port 3000)
```

## Monitoring & Debugging

### Development Tools
- React DevTools (component tree)
- TanStack Query DevTools (query state)
- Next.js Dev Overlay (errors)
- Chrome DevTools (network, console)

### Logging Strategy
```typescript
// Development: verbose logging
console.log('[API Request]', method, url, data);

// Production: errors only
console.error('[Error]', error);
```

### Performance Monitoring
- Next.js Analytics (built-in)
- Web Vitals tracking
- Custom performance marks

---

## Summary

The frontend architecture is designed with:
- **Modularity**: Components are small and focused
- **Type Safety**: Full TypeScript coverage
- **Performance**: Optimized caching and code splitting
- **Maintainability**: Clear structure and documentation
- **Scalability**: Easy to add new features
- **Reliability**: Comprehensive error handling
- **Accessibility**: WCAG 2.1 AA compliant
- **Developer Experience**: Modern tooling and hot reload

This architecture ensures a robust, performant, and maintainable application ready for production deployment.
