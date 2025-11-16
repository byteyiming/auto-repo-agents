# OmniDoc - GitHub Copilot Code Review Rules

This file provides context and rules for GitHub Copilot to perform automated code reviews for pull requests.

## 🎯 Project Overview

**OmniDoc** is an AI-powered documentation generation system that creates comprehensive documentation from simple user ideas using multi-agent collaboration.

- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: Next.js 16 with React 19, TypeScript
- **Database**: PostgreSQL (Neon)
- **Task Queue**: Celery with Redis (Upstash)
- **Deployment**: Railway (backend), Vercel (frontend)

## 📋 Code Review Checklist

### Backend (Python/FastAPI)

#### 1. **Code Quality & Style**
- ✅ Follow PEP 8 style guide (line length: 100 characters)
- ✅ Use type hints for all function parameters and return values
- ✅ Use `from __future__ import annotations` for forward references
- ✅ Prefer async/await for I/O operations
- ✅ Use dataclasses or Pydantic models for data structures
- ✅ Keep functions focused and single-purpose
- ✅ Maximum function length: 50 lines (prefer smaller)

#### 2. **Error Handling**
- ✅ Always use try-except blocks for external API calls (LLM, database, Redis)
- ✅ Log errors with context using `logger.error(f"message", exc_info=True)`
- ✅ Use FastAPI's HTTPException for API errors with appropriate status codes
- ✅ Add CORS headers to ALL error responses (via exception handlers)
- ✅ Don't expose internal error details in production responses

#### 3. **Security**
- ✅ Never hardcode secrets or API keys (use environment variables)
- ✅ Validate all user input using Pydantic models
- ✅ Check CORS configuration for new endpoints
- ✅ Ensure rate limiting is applied to new endpoints
- ✅ Use parameterized queries for database operations (SQL injection prevention)

#### 4. **Database**
- ✅ Use ContextManager for all database operations
- ✅ Store document content in database, not filesystem
- ✅ Use transactions for multi-step operations
- ✅ Handle database connection errors gracefully
- ✅ Never commit sensitive data in migration files

#### 5. **Redis & Celery**
- ✅ Check Redis availability before submitting Celery tasks
- ✅ Use `rediss://` (not `redis://`) for Upstash Redis connections
- ✅ Configure `broker_transport_options` with SSL for Upstash
- ✅ Handle Redis connection failures gracefully
- ✅ Don't block request threads with Celery operations

#### 6. **Logging**
- ✅ Use structured logging with `get_logger(__name__)`
- ✅ Include Request-ID in all logs for tracing
- ✅ Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Don't log sensitive information (passwords, API keys, tokens)
- ✅ Use JSON format in production (LOG_FORMAT=json)

#### 7. **Testing**
- ✅ Write tests for new features
- ✅ Test error cases, not just happy paths
- ✅ Mock external dependencies (LLM, database, Redis)
- ✅ Test async functions with pytest-asyncio

### Frontend (Next.js/React/TypeScript)

#### 1. **Code Quality & Style**
- ✅ Use TypeScript for all files (`.ts`, `.tsx`)
- ✅ Define proper types/interfaces for all props and data
- ✅ Use functional components with hooks
- ✅ Keep components small and focused (< 200 lines)
- ✅ Extract reusable logic into custom hooks
- ✅ Use ESLint and fix all warnings

#### 2. **Performance**
- ✅ Use `useMemo` for expensive computations
- ✅ Use `useCallback` for event handlers passed to children
- ✅ Implement proper loading and error states
- ✅ Avoid unnecessary re-renders
- ✅ Use Next.js Image component for images
- ✅ Implement proper code splitting

#### 3. **State Management**
- ✅ Use React state for local component state
- ✅ Use SWR for server state and caching
- ✅ Use localStorage sparingly (only for user preferences)
- ✅ Don't store sensitive data in localStorage

#### 4. **API Integration**
- ✅ Always handle API errors gracefully
- ✅ Show user-friendly error messages
- ✅ Implement retry logic for failed requests
- ✅ Use proper loading states during API calls
- ✅ Validate API responses match TypeScript interfaces

#### 5. **i18n (Internationalization)**
- ✅ All user-facing text must use `t()` function from `useI18n()`
- ✅ Never hardcode text strings (even English)
- ✅ Add translations for all supported languages (EN, ZH, JA, KO, ES)
- ✅ Test UI in all supported languages

#### 6. **Accessibility**
- ✅ Use semantic HTML elements
- ✅ Add proper ARIA labels where needed
- ✅ Ensure keyboard navigation works
- ✅ Test with screen readers

### Common Issues to Flag

#### 🚨 Critical Issues (Must Fix)
- Security vulnerabilities (SQL injection, XSS, exposed secrets)
- Missing error handling (try-except blocks)
- Missing CORS headers on new endpoints
- Hardcoded secrets or API keys
- Missing type hints/TypeScript types
- Unused imports or variables
- Missing environment variable validation

#### ⚠️ Important Issues (Should Fix)
- Missing logging for errors
- Missing Request-ID in logs
- Inefficient database queries (N+1 problems)
- Missing input validation
- Poor error messages for users
- Missing tests for new features
- Memory leaks (unclosed connections, subscriptions)

#### 💡 Suggestions (Nice to Have)
- Code can be refactored for better readability
- Performance optimizations available
- Better naming conventions
- Missing documentation strings
- Can use more modern Python/React patterns

## 🔍 Specific Patterns to Check

### Backend Patterns

1. **FastAPI Endpoints**
   ```python
   # ✅ Good
   @router.post("/api/projects")
   async def create_project(request: ProjectCreateRequest):
       try:
           # ... logic
       except Exception as e:
           logger.error(f"Failed to create project: {e}", exc_info=True)
           raise HTTPException(status_code=500, detail="Internal server error")
   ```

2. **Environment Variables**
   ```python
   # ✅ Good
   REDIS_URL = os.getenv("REDIS_URL")
   if not REDIS_URL:
       raise ValueError("REDIS_URL not set")
   ```

3. **Redis Connections (Upstash)**
   ```python
   # ✅ Good - Use rediss:// for Upstash
   if "upstash.io" in REDIS_URL:
       if not REDIS_URL.startswith("rediss://"):
           test_url = REDIS_URL.replace("redis://", "rediss://", 1)
   ```

4. **Logging**
   ```python
   # ✅ Good
   logger.info(f"Processing project {project_id} [Request-ID: {request_id}]")
   logger.error(f"Redis connection failed: {e}", exc_info=True)
   ```

### Frontend Patterns

1. **API Calls**
   ```typescript
   // ✅ Good
   try {
     const response = await fetchJSON<ProjectResponse>(`/api/projects/${id}`);
     setProject(response);
   } catch (error) {
     logger.error("Failed to fetch project", error);
     setError("Failed to load project. Please try again.");
   }
   ```

2. **Internationalization**
   ```typescript
   // ✅ Good
   const { t } = useI18n();
   return <button>{t("common.submit")}</button>;
   ```

3. **Type Safety**
   ```typescript
   // ✅ Good
   interface Project {
     id: string;
     status: "pending" | "completed" | "failed";
   }
   ```

## 🚫 Anti-Patterns to Flag

1. **Don't catch all exceptions silently**
   ```python
   # ❌ Bad
   try:
       result = risky_operation()
   except:
       pass  # Never do this!
   ```

2. **Don't use print() for logging**
   ```python
   # ❌ Bad
   print("Error occurred")  # Use logger instead
   ```

3. **Don't hardcode URLs or configurations**
   ```python
   # ❌ Bad
   redis_url = "redis://localhost:6379"  # Use environment variable
   ```

4. **Don't ignore TypeScript errors**
   ```typescript
   // ❌ Bad
   // @ts-ignore
   const data = apiResponse.data;  # Fix the type instead
   ```

## 📝 Documentation Requirements

- ✅ All public functions/classes need docstrings
- ✅ Complex logic needs inline comments
- ✅ API endpoints need OpenAPI documentation
- ✅ README updates for new features
- ✅ Update .md files only if explicitly requested

## ✅ Review Approval Criteria

A PR should be approved if:
1. ✅ All critical issues are fixed
2. ✅ Code follows project patterns and style
3. ✅ Tests pass (if applicable)
4. ✅ No security vulnerabilities
5. ✅ Error handling is appropriate
6. ✅ Logging is adequate
7. ✅ Type hints/TypeScript types are present
8. ✅ CORS headers added for new endpoints
9. ✅ Environment variables validated
10. ✅ Redis/Celery handled correctly (if used)

## 🔗 Related Documentation

- Backend architecture: See `src/web/app.py` for patterns
- Frontend patterns: See `frontend/components/` for examples
- Database: See `src/context/context_manager.py`
- Redis: See `src/tasks/celery_app.py` and `src/utils/cache.py`
- Deployment: Railway (backend), Vercel (frontend)

