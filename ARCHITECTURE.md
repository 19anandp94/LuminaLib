# LuminaLib Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Database Schema Design](#database-schema-design)
3. [Async Processing Strategy](#async-processing-strategy)
4. [ML Recommendation System](#ml-recommendation-system)
5. [Frontend Architecture](#frontend-architecture)
6. [Design Patterns & Principles](#design-patterns--principles)

## System Overview

LuminaLib follows a **flat, modular architecture** with clear separation of concerns through routers, models, and pluggable providers:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│                      Port 3000                           │
└─────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                      Port 8000                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Routers (auth, books, recommendations)         │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Models & Schemas (SQLAlchemy + Pydantic)       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Pluggable Providers (LLM, Storage)             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │   Ollama     │
│  Port 5432   │    │  Port 6379   │    │  Port 11434  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Key Architectural Decisions

1. **Flat Structure**: Simple, pragmatic file organization without nested layers
2. **Modular Routers**: API endpoints organized by domain (auth, books, recommendations)
3. **Strategy Pattern**: Pluggable LLM and storage providers via abstract base classes
4. **Dependency Injection**: FastAPI's DI system for database sessions and current user
5. **Async-First**: All I/O operations use async/await for maximum concurrency
6. **Type Safety**: Pydantic schemas for backend validation, TypeScript for frontend

## Database Schema Design

### Actual Implementation

The application uses a **simple, normalized schema** with the following models (defined in `backend/app/models.py`):

#### Core Models

**User**: Authentication and user management

- `id`, `email` (unique), `hashed_password`, `created_at`
- Relationships: reviews, borrows, preferences, books_added

**UserPreference**: Simple genre tracking for recommendations

- `id`, `user_id`, `genre`, `created_at`
- Design: One row per genre preference (e.g., user likes "Fiction", "Mystery")

**Book**: Book metadata and file storage

- `id`, `title`, `author`, `genre`, `summary` (AI-generated), `file_path`, `file_name`, `added_by_user_id`, `created_at`
- Indexed on: title, author, genre (for search/filter performance)
- Relationships: reviews, borrows, book_summary

**BookSummary**: AI-generated book summaries

- `id`, `book_id` (unique), `summary`, `created_at`
- Separate table to keep Book model clean

**Borrow**: Library borrowing records

- `id`, `user_id`, `book_id`, `borrowed_at`, `returned_at` (nullable)
- Business rule: `returned_at` is NULL while book is borrowed
- Enables constraint: users must borrow before reviewing

**Review**: User book reviews

- `id`, `user_id`, `book_id`, `rating` (1-5), `text`, `created_at`
- Triggers background sentiment analysis on creation

**ReviewAnalysis**: AI sentiment analysis of reviews

- `id`, `review_id` (unique), `sentiment`, `confidence`, `created_at`
- Populated by LLM in background task

### Database Relationships

```
User ──┬─> Reviews (one-to-many)
       ├─> Borrows (one-to-many)
       ├─> UserPreferences (one-to-many)
       └─> Books (one-to-many, as uploader)

Book ──┬─> Reviews (one-to-many)
       ├─> Borrows (one-to-many)
       └─> BookSummary (one-to-one)

Review ──> ReviewAnalysis (one-to-one)
```

### Indexing Strategy

- **users.email**: Unique index for fast login lookups
- **books.title, author, genre**: Indexes for search and filter queries
- **borrows.user_id, book_id**: For borrowing history queries

### Design Philosophy

The schema is **intentionally simple** and **normalized**:

- No complex JSONB fields or feature vectors (YAGNI principle)
- Clear foreign key relationships
- Separate tables for AI-generated content (summaries, sentiment)
- Easy to understand and maintain

## Async Processing Strategy

### Challenge

LLM operations (summarization, sentiment analysis) can take 10-60 seconds. We cannot block HTTP requests.

### Solution: Background Task Pattern

```python
# In API route
@router.post("/books")
async def create_book(...):
    # 1. Upload file and create book record (fast)
    book = create_book_in_db(...)

    # 2. Schedule async summarization (non-blocking)
    schedule_book_summarization(book.id)

    # 3. Return immediately
    return book
```

### Implementation

**Current (Development)**:

```python
def schedule_book_summarization(book_id: int):
    asyncio.create_task(process_book_summarization(book_id))
```

**Production-Ready Approach**:
For production, this would use Celery with Redis:

```python
@celery_app.task
def process_book_summarization(book_id: int):
    # Runs in separate worker process
    # Retries on failure
    # Monitored via Flower dashboard
```

### Why This Approach?

1. **Non-blocking**: API responds immediately, UX remains snappy
2. **Scalable**: Background workers can scale independently
3. **Resilient**: Failed tasks can be retried
4. **Observable**: Task status can be tracked

### Async Flow Diagram

```
User uploads book
       │
       ├─> API creates DB record ──> Returns 201 Created
       │
       └─> Triggers background task
                   │
                   ├─> Downloads file from storage
                   ├─> Extracts text content
                   ├─> Calls LLM for summary
                   └─> Updates book.ai_summary
```

## ML Recommendation System

### Strategy: Hybrid Approach

We combine multiple recommendation techniques:

1. **Content-Based Filtering** (60% weight)
   - Match user's favorite genres/authors with book attributes
   - Fast, works for new users with minimal data

2. **Collaborative Filtering** (30% weight)
   - "Users who borrowed X also borrowed Y"
   - Requires sufficient user interaction data

3. **Popularity-Based** (10% weight)
   - Trending books as fallback
   - Ensures diversity in recommendations

### Implementation

```python
class RecommendationEngine:
    async def get_recommendations(self, user_id: int, limit: int = 10):
        # 1. Get user preferences
        preferences = await get_user_preferences(user_id)

        # 2. Content-based: Books in favorite genres
        content_recs = await get_books_by_genres(
            preferences.favorite_genres
        )

        # 3. Collaborative: Similar users' books
        similar_users = await find_similar_users(user_id)
        collab_recs = await get_books_from_users(similar_users)

        # 4. Merge and rank
        return merge_recommendations([content_recs, collab_recs])
```

### User Preference Updates

Preferences are updated after each interaction:

```python
async def update_user_preferences(user_id: int):
    # Analyze borrowing history
    borrowed_books = await get_borrowed_books(user_id)

    # Extract patterns
    genres = Counter([b.genre for b in borrowed_books])
    authors = Counter([b.author for b in borrowed_books])

    # Calculate weights
    genre_weights = {
        genre: count / total
        for genre, count in genres.items()
    }

    # Update preferences
    await save_preferences(user_id, {
        'favorite_genres': top_genres,
        'genre_weights': genre_weights,
        ...
    })
```

### Future Enhancements

1. **Matrix Factorization**: Use SVD to compute `feature_vector`
2. **Deep Learning**: Train neural collaborative filtering model
3. **A/B Testing**: Compare recommendation algorithms
4. **Diversity**: Ensure recommendations aren't too similar

## Frontend Architecture

### Design Principles

1. **Layered Architecture**: Clear separation between UI, logic, and data
2. **Component Composition**: Small, reusable components over monoliths
3. **Abstracted Network Layer**: No direct fetch/axios calls in components
4. **Type Safety**: Full TypeScript coverage

### Architecture Layers

```
┌─────────────────────────────────────────┐
│         Pages (app/*/page.tsx)          │  ← Route handlers
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│    Feature Components (components/)     │  ← Business logic
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│      UI Components (components/ui/)     │  ← Reusable atoms
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│      Hooks (lib/hooks/use*.ts)          │  ← State management
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│    Services (lib/api/services.ts)       │  ← API abstraction
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│     API Client (lib/api/client.ts)      │  ← HTTP client
└─────────────────────────────────────────┘
```

### State Management Choice: React Query

**Why React Query over Redux/Zustand?**

1. **Server State Focus**: Most state is server-derived (books, reviews)
2. **Built-in Caching**: Automatic cache invalidation and refetching
3. **Loading States**: Handles loading/error states automatically
4. **Optimistic Updates**: Easy optimistic UI updates
5. **Less Boilerplate**: No actions/reducers needed

Example:

```typescript
// Instead of Redux actions/reducers
const { data, isLoading } = useBooks({ page: 1 });

// Mutations with automatic cache invalidation
const createBook = useCreateBook();
await createBook.mutateAsync({ data, file });
// ↑ Automatically refetches book list
```

### Network Layer Abstraction

Components never call APIs directly:

```typescript
// ❌ Bad: Direct API call in component
const BookList = () => {
  const [books, setBooks] = useState([]);
  useEffect(() => {
    fetch("/api/books")
      .then((r) => r.json())
      .then(setBooks);
  }, []);
};

// ✅ Good: Abstracted through hooks and services
const BookList = () => {
  const { data: books } = useBooks();
};
```

Benefits:

- Easy to mock for testing
- Centralized error handling
- Type safety across the stack
- Can swap API implementation without touching components

### SSR Strategy

Next.js App Router enables:

1. **Server Components**: Initial page load is server-rendered
2. **Client Components**: Interactive parts use 'use client'
3. **Streaming**: Progressive page rendering

Example:

```typescript
// Server Component (default)
export default async function BooksPage() {
    // This runs on server, SEO-friendly
    const books = await getBooks();
    return <BookList books={books} />;
}

// Client Component (interactive)
'use client';
export function BookList({ books }) {
    // This hydrates on client
    const [selected, setSelected] = useState(null);
    ...
}
```

## Design Patterns & Principles

### SOLID Principles Applied

1. **Single Responsibility**: Each service class has one job
   - `StorageProvider`: Only handles file storage
   - `LLMProvider`: Only handles LLM operations
   - `RecommendationEngine`: Only handles recommendations

2. **Open/Closed**: Extensible without modification
   - New storage provider? Implement `StorageProvider` interface
   - New LLM? Implement `LLMProvider` interface

3. **Liskov Substitution**: Implementations are interchangeable

   ```python
   storage: StorageProvider = get_storage_provider()
   # Could be Local, MinIO, or S3 - code doesn't care
   ```

4. **Interface Segregation**: Focused interfaces
   - `StorageProvider` only defines storage operations
   - Not bloated with unrelated methods

5. **Dependency Inversion**: Depend on abstractions

   ```python
   # High-level module depends on abstraction
   def upload_book(storage: StorageProvider, file):
       storage.upload_file(file)

   # Not on concrete implementation
   def upload_book(local_storage: LocalStorage, file):  # ❌
   ```

### Factory Pattern

Used for creating provider instances:

```python
def get_storage_provider() -> StorageProvider:
    if settings.storage_provider == "local":
        return LocalStorageProvider(...)
    elif settings.storage_provider == "s3":
        return S3StorageProvider(...)
```

### Direct Database Queries (Pragmatic Approach)

**Note**: The current implementation uses **direct SQLAlchemy queries** in routers for simplicity:

```python
# Current approach (direct queries in routers)
@router.get("/books")
async def list_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book))
    return result.scalars().all()
```

This is pragmatic for small applications. For larger codebases, consider the Repository pattern for better testability and abstraction.

## Backend Implementation Details

### File Structure (Flat Architecture)

```
backend/app/
├── main.py              # FastAPI app initialization, CORS, routers
├── config.py            # Pydantic Settings for environment variables
├── db.py                # Database engine and session management
├── models.py            # All SQLAlchemy models in one file
├── schemas.py           # All Pydantic schemas in one file
├── auth.py              # JWT token creation and verification
├── deps.py              # FastAPI dependencies (get_db, get_current_user)
├── recommendation_ml.py # ML recommendation engine
├── routers/
│   ├── auth.py          # POST /auth/signup, /auth/login, GET /auth/me
│   ├── books.py         # CRUD + borrow/return + reviews
│   └── recommendations.py  # ML recommendations + AI suggestions
├── llm/
│   ├── base.py          # Abstract LLMBackend class
│   ├── ollama.py        # Ollama implementation
│   ├── openai.py        # OpenAI implementation
│   ├── mock.py          # Mock for testing
│   └── prompts.py       # Prompt templates
└── storage/
    ├── base.py          # Abstract StorageBackend class
    ├── local.py         # Local filesystem storage
    └── s3.py            # AWS S3 storage
```

### Search Implementation

The search functionality demonstrates efficient PostgreSQL querying with filters:

```python
@router.get("", response_model=BookListResponse)
async def list_books(
    search: str = None,      # Search by title or author
    genre: str = None,       # Filter by genre
    author: str = None,      # Filter by author
    db: AsyncSession = Depends(get_db),
):
    query = select(Book)

    # Case-insensitive search using PostgreSQL's ilike
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Book.title.ilike(search_pattern)) |
            (Book.author.ilike(search_pattern))
        )

    # Get total count with filters applied
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated results
    items = (await db.execute(query.offset(skip).limit(limit))).scalars().all()

    return BookListResponse(items=items, total=total)
```

**Key Features**: Case-insensitive search, multi-field search, proper pagination with filtered counts.

### Authentication Flow

```
Signup → Hash password → Create user → Generate JWT → Return token (auto-login)
Login → Verify password → Generate JWT → Return token
Protected Routes → Validate JWT → Inject user → Execute logic
```

### LLM Integration (Strategy Pattern)

```python
def get_llm_backend() -> LLMBackend:
    if settings.llm_provider == "ollama":
        return OllamaBackend(...)
    elif settings.llm_provider == "openai":
        return OpenAIBackend(...)
    else:
        return MockLLMBackend()
```

Swap providers via environment variable. Easy to add new providers.

## Conclusion

This architecture prioritizes:

- **Simplicity**: Flat structure, easy to navigate
- **Pragmatism**: Direct queries instead of over-engineering
- **Maintainability**: Clear separation via routers
- **Testability**: Dependency injection enables mocking
- **Scalability**: Async operations, background tasks
- **Extensibility**: Swap LLM/storage via config
- **Type Safety**: Pydantic + TypeScript catch errors early
- **Performance**: Async/await, proper indexing, efficient queries

The system follows **modern Python best practices** while avoiding unnecessary complexity. Production-ready for small to medium-scale deployments.
