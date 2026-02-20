# LuminaLib - Intelligent Library System

A next-generation library management system with AI-powered features including book summarization, sentiment analysis, and ML-based recommendations.

## Features

### 🔐 Authentication & User Management

- **JWT-based Authentication**: Secure stateless authentication with access tokens
- **Password Security**: Bcrypt hashing with salt for password storage
- **Auto-login**: Automatic login after successful signup
- **Protected Routes**: Frontend route protection with authentication guards

### 📚 Book Management

- **Book Upload**: Upload actual book files (PDF/TXT) with metadata
- **Search & Filter**: Search books by title or author, filter by genre
- **Book Details**: Comprehensive book information with AI summaries
- **File Storage**: Pluggable storage backends (Local/S3)
- **Pagination**: Efficient pagination for large book collections

### 🤖 AI-Powered Features

- **Automatic Summarization**: LLM-powered book summaries on upload
- **Sentiment Analysis**: AI-driven review sentiment analysis
- **Review Consensus**: Aggregate sentiment analysis across all reviews
- **Pluggable LLM Providers**: Support for Ollama (Llama 3), OpenAI, or Mock

### 📖 Library Operations

- **Borrow/Return Workflow**: Full library mechanics with tracking
- **Availability Tracking**: Real-time book availability status
- **Borrowing History**: Track user borrowing history
- **Review System**: Users must borrow books before reviewing

### 🎯 Recommendations

- **ML-Based Recommendations**: Scikit-learn powered personalized recommendations
- **Content-Based Filtering**: Recommendations based on book metadata and summaries
- **User Preferences**: Track and utilize user genre preferences
- **Similar Books**: Find books similar to a specific title

### 💻 Modern Tech Stack

- **Fully Dockerized**: One-command deployment with docker-compose
- **Async/Await**: Full async support in backend for high performance
- **Type Safety**: TypeScript frontend with Pydantic backend validation
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Updates**: React Query for optimistic updates and caching

## Tech Stack

### Backend

- **Framework**: FastAPI 0.109.2 (Python 3.11)
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0.25 (async with asyncpg)
- **Migrations**: Alembic 1.13.1 for database schema management
- **Authentication**: JWT (python-jose) with passlib/bcrypt
- **Storage**: Pluggable storage layer (Local/S3 via boto3)
- **LLM Integration**: Ollama, OpenAI, or Mock providers
- **ML Engine**: Scikit-learn for recommendation algorithms
- **PDF Processing**: PyPDF for text extraction
- **Architecture**: Flat structure with modular routers and services

### Frontend

- **Framework**: Next.js 14.1.0 with TypeScript 5.3.3
- **State Management**: TanStack React Query 5.17.19
- **HTTP Client**: Axios 1.6.5 with interceptors
- **Styling**: Tailwind CSS 3.4.1
- **Form Handling**: React Hook Form 7.49.3 with Zod validation
- **Testing**: Jest 29.7.0 + React Testing Library

### Infrastructure

- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Database**: PostgreSQL 16-alpine
- **Cache**: Redis 7-alpine
- **LLM Service**: Ollama (optional)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### One-Command Start

1. Clone the repository:

```bash
git clone <repository-url>
cd ILS
```

2. Copy environment file:

```bash
cp .env.example .env
```

3. Start all services:

```bash
docker-compose up --build
```

This will start:

- PostgreSQL database on port 5432
- Redis on port 6379
- Ollama LLM service on port 11434
- Backend API on port 8000
- Frontend on port 3000

4. Access the application:

- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Health Check: http://localhost:8000/health

### Initial Setup

The database tables are created automatically on first run. You can start using the application immediately by:

1. Navigate to http://localhost:3000
2. Click "Sign Up" to create an account
3. Start browsing and uploading books!

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Configuration

All configuration is managed via environment variables. See `.env.example` for available options.

### Key Configuration Options

#### Database Configuration

```env
DATABASE_URL=postgresql+asyncpg://lumina:lumina_password@postgres:5432/luminalib
POSTGRES_USER=lumina
POSTGRES_PASSWORD=lumina_password
POSTGRES_DB=luminalib
```

#### JWT Configuration

```env
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Storage Configuration

Change `STORAGE_PROVIDER` in `.env`:

- `local`: Local filesystem storage (default)
- `s3`: AWS S3 storage

```env
STORAGE_PROVIDER=local
STORAGE_LOCAL_PATH=/app/book_storage

# For S3 storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=your-bucket
AWS_REGION=us-east-1
```

#### LLM Configuration

Change `LLM_PROVIDER` in `.env`:

- `ollama`: Local Ollama (Llama 3) - default
- `openai`: OpenAI API
- `mock`: Mock provider for testing (no actual LLM calls)

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://ollama:11434

# For OpenAI
OPENAI_API_KEY=your-openai-api-key
```

#### CORS Configuration

```env
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

## API Endpoints

See full interactive API documentation at http://localhost:8000/docs (Swagger UI)

### Authentication Endpoints

- `POST /auth/signup` - Register new user (auto-login enabled)
- `POST /auth/login` - Login and get JWT access token
- `GET /auth/me` - Get current user profile

### Book Endpoints

- `GET /books` - List books with pagination, search, and filters
  - Query params: `skip`, `limit`, `search`, `genre`, `author`
- `POST /books` - Upload new book with file and metadata
- `GET /books/{id}` - Get detailed book information
- `PUT /books/{id}` - Update book metadata
- `DELETE /books/{id}` - Delete a book
- `GET /books/{id}/file` - Download book file

### Library Operations

- `POST /books/{id}/borrow` - Borrow a book
- `POST /books/{id}/return` - Return a borrowed book

### Review Endpoints

- `GET /books/{id}/reviews` - Get all reviews for a book
- `POST /books/{id}/reviews` - Submit a review (must borrow first)
  - Triggers background sentiment analysis

### Recommendation Endpoints

- `GET /recommendations` - Get personalized ML-based recommendations
- `GET /recommendations/similar/{book_id}` - Get similar books from catalog
- `GET /recommendations/suggestions` - Get AI suggestions based on preferences
- `GET /recommendations/suggestions/similar/{book_id}` - Get AI suggestions similar to a book

### Health Check

- `GET /health` - API health status

## Project Structure

```
ILS/
├── backend/
│   ├── app/
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── books.py       # Book management endpoints
│   │   │   └── recommendations.py  # Recommendation endpoints
│   │   ├── llm/               # LLM provider implementations
│   │   │   ├── base.py        # Abstract LLM interface
│   │   │   ├── ollama.py      # Ollama integration
│   │   │   ├── openai.py      # OpenAI integration
│   │   │   ├── mock.py        # Mock provider for testing
│   │   │   └── prompts.py     # LLM prompt templates
│   │   ├── storage/           # Storage provider implementations
│   │   │   ├── base.py        # Abstract storage interface
│   │   │   ├── local.py       # Local filesystem storage
│   │   │   └── s3.py          # S3-compatible storage
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── config.py          # Configuration management
│   │   ├── db.py              # Database connection and session
│   │   ├── auth.py            # JWT authentication utilities
│   │   ├── deps.py            # FastAPI dependencies
│   │   ├── recommendation_ml.py  # ML recommendation engine
│   │   └── main.py            # FastAPI application entry point
│   ├── alembic/               # Database migrations
│   ├── Dockerfile             # Backend container definition
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   │   ├── books/         # Books pages
│   │   │   ├── login/         # Login page
│   │   │   ├── signup/        # Signup page
│   │   │   ├── recommendations/  # Recommendations page
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Home page
│   │   │   └── providers.tsx  # React Query provider
│   │   ├── components/        # React components
│   │   │   ├── books/         # Book-related components
│   │   │   ├── layout/        # Layout components (Navbar)
│   │   │   └── ui/            # Reusable UI components
│   │   └── lib/               # Utilities and hooks
│   │       ├── api/           # API client and services
│   │       │   ├── client.ts  # Axios client with interceptors
│   │       │   ├── services.ts  # API service functions
│   │       │   └── types.ts   # TypeScript type definitions
│   │       └── hooks/         # Custom React hooks
│   │           ├── useAuth.ts    # Authentication hook
│   │           ├── useBooks.ts   # Books hook
│   │           ├── useReviews.ts # Reviews hook
│   │           └── useRecommendations.ts  # Recommendations hook
│   ├── Dockerfile             # Frontend container definition
│   └── package.json           # Node.js dependencies
├── docker-compose.yml         # Multi-container orchestration
├── .env.example               # Environment variables template
├── README.md                  # This file
└── upload_books.sh            # Sample book upload script
```

## Database Schema

The application uses the following database models:

### Core Models

- **User**: User accounts with email, hashed password, and timestamps
- **UserPreference**: User genre preferences for recommendations
- **Book**: Book metadata including title, author, genre, file path, and AI summary
- **BookSummary**: AI-generated summaries for books
- **Borrow**: Borrowing records with borrow and return timestamps
- **Review**: User reviews with rating and text
- **ReviewAnalysis**: Sentiment analysis results for reviews

### Key Relationships

- User → Reviews (one-to-many)
- User → Borrows (one-to-many)
- User → UserPreferences (one-to-many)
- Book → Reviews (one-to-many)
- Book → Borrows (one-to-many)
- Book → BookSummary (one-to-one)

### Database Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing

### Sample Data

Use the provided script to upload sample books:

```bash
chmod +x upload_books.sh
./upload_books.sh
```

This will upload 5 sample books across different genres (Adventure, Mystery, Romance, Science Fiction, Cooking).

### Manual Testing

1. **Sign up** at http://localhost:3000/signup
2. **Browse books** at http://localhost:3000/books
3. **Search** for books by title or author
4. **View book details** and click "Borrow Book"
5. **Write a review** (only available after borrowing)
6. **Check recommendations** at http://localhost:3000/recommendations

### API Testing

Use the interactive API docs at http://localhost:8000/docs to test endpoints directly.

## Troubleshooting

### Docker Issues

If containers fail to start:

```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Database Issues

If you need to reset the database:

```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker volume rm ils_postgres_data

# Restart
docker-compose up -d
```

### Network Issues

If you can't rebuild due to network issues, copy updated files directly:

```bash
# Copy updated backend file
docker cp backend/app/routers/books.py luminalib-backend:/app/app/routers/books.py

# Restart backend
docker-compose restart backend
```

## Performance Considerations

- **Async Database Operations**: All database queries use async/await for non-blocking I/O
- **Connection Pooling**: SQLAlchemy manages database connection pools
- **Query Optimization**: Proper indexing on frequently queried fields
- **Caching**: React Query caches API responses on the frontend
- **Background Tasks**: LLM operations run in background tasks to avoid blocking requests

## Security Features

- **Password Hashing**: Bcrypt with salt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **CORS Protection**: Configurable allowed origins
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Input Validation**: Pydantic schemas validate all inputs
- **File Upload Validation**: File type and size validation

## Support

For issues and questions, please open an issue on GitHub.

## Contributors

This project was built as a technical assessment for an Intelligent Library System.
