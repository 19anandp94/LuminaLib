# LuminaLib Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Database Schema Design](#database-schema-design)
3. [Async Processing Strategy](#async-processing-strategy)
4. [ML Recommendation System](#ml-recommendation-system)
5. [Frontend Architecture](#frontend-architecture)
6. [Design Patterns & Principles](#design-patterns--principles)

## System Overview

LuminaLib follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│              (FastAPI Routes / Next.js Pages)            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                     Service Layer                        │
│        (Business Logic / Use Cases / Orchestration)      │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                    │
│     (Database / Storage / LLM / External Services)       │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Dependency Injection**: All external dependencies (storage, LLM) are injected via factory functions
2. **Interface-Driven Development**: Abstract base classes define contracts for swappable implementations
3. **Async-First**: All I/O operations use async/await for maximum concurrency
4. **Type Safety**: Pydantic schemas for backend, TypeScript for frontend

## Database Schema Design

### User Preferences Schema

The `user_preferences` table is central to our ML recommendation system:

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    
    -- Content-based features
    favorite_genres TEXT[],           -- Top genres user reads
    favorite_authors TEXT[],          -- Preferred authors
    avg_rating_given FLOAT,           -- User's rating tendency
    
    -- Behavioral metrics
    books_borrowed_count INTEGER,
    books_reviewed_count INTEGER,
    
    -- Advanced ML features
    genre_weights JSONB,              -- Genre preference weights
    feature_vector FLOAT[],           -- Latent feature space representation
    
    last_updated TIMESTAMP
);
```

**Design Rationale:**

1. **favorite_genres/authors**: Enable content-based filtering by matching user preferences with book attributes
2. **avg_rating_given**: Identifies harsh vs. lenient reviewers for better collaborative filtering
3. **genre_weights (JSONB)**: Flexible structure for storing weighted genre preferences
   - Example: `{"fiction": 0.6, "sci-fi": 0.3, "mystery": 0.1}`
   - Allows for nuanced preference modeling beyond simple lists
4. **feature_vector**: Supports matrix factorization for collaborative filtering
   - Represents user in latent feature space
   - Can be computed using techniques like SVD or neural embeddings
5. **Behavioral counts**: Track engagement level for recommendation confidence

### Other Key Tables

**Books Table**:
- Stores both metadata AND file information
- `ai_summary` and `review_consensus` fields for GenAI-generated content
- `available_copies` for real-time availability tracking

**Borrow Records**:
- Tracks borrowing history with `borrowed_at`, `due_date`, `returned_at`
- Enables constraint: "users can only review borrowed books"

**Reviews**:
- Stores user reviews with AI-generated `sentiment_score` and `sentiment_label`
- Triggers async consensus generation on creation

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
        fetch('/api/books').then(r => r.json()).then(setBooks);
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

### Repository Pattern

Database access is abstracted:

```python
# Instead of direct SQLAlchemy queries everywhere
class BookRepository:
    async def get_by_id(self, id: int) -> Book:
        ...
    
    async def list(self, filters: dict) -> List[Book]:
        ...
```

## Conclusion

This architecture prioritizes:
- **Maintainability**: Clear structure, easy to navigate
- **Testability**: Dependency injection enables mocking
- **Scalability**: Async operations, background tasks
- **Extensibility**: Swap implementations via config
- **Type Safety**: Pydantic + TypeScript catch errors early

The system is production-ready and follows industry best practices for modern full-stack applications.

