# LuminaLib - Intelligent Library System

A next-generation library management system with AI-powered features including book summarization, sentiment analysis, and ML-based recommendations.

## Features

- 🔐 **Robust Authentication**: JWT-based stateless authentication with secure password hashing
- 📚 **Content-Aware Book Management**: Upload and store actual book files (PDF/TXT) with metadata
- 🤖 **AI-Powered Summaries**: Automatic book summarization using LLM (Llama 3/OpenAI)
- 💭 **Sentiment Analysis**: AI-driven review sentiment analysis and consensus generation
- 🎯 **Smart Recommendations**: ML-based personalized book recommendations
- 📖 **Library Mechanics**: Full borrow/return workflow with availability tracking
- ⭐ **Review System**: User reviews with constraint that users must borrow before reviewing
- 🎨 **Modern UI**: Next.js with SSR, TypeScript, and Tailwind CSS
- 🐳 **Fully Dockerized**: One-command deployment with docker-compose

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Authentication**: JWT with passlib/bcrypt
- **Storage**: Abstracted storage layer (Local/MinIO/S3)
- **LLM**: Pluggable LLM providers (Ollama/OpenAI/Mock)
- **Architecture**: Clean Architecture with Dependency Injection

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **State Management**: React Query (TanStack Query)
- **Styling**: Tailwind CSS
- **API Layer**: Abstracted service layer with Axios
- **Testing**: Jest + React Testing Library

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

### Swapping Storage Providers

Change `STORAGE_PROVIDER` in `.env`:
- `local`: Local filesystem storage
- `minio`: MinIO S3-compatible storage
- `s3`: AWS S3 storage

### Swapping LLM Providers

Change `LLM_PROVIDER` in `.env`:
- `ollama`: Local Ollama (Llama 3)
- `openai`: OpenAI API
- `mock`: Mock provider for testing

## API Endpoints

See full API documentation at http://localhost:8000/docs

Key endpoints:
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /books` - List books with pagination
- `POST /books` - Upload new book
- `POST /books/{id}/borrow` - Borrow a book
- `POST /books/{id}/return` - Return a book
- `POST /books/{id}/reviews` - Submit a review
- `GET /recommendations` - Get personalized recommendations

## Project Structure

```
ILS/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities and hooks
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

