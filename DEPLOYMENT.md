# LuminaLib Deployment Guide

## Quick Start (One-Command Deployment)

### Prerequisites
- Docker Desktop installed and running
- Git
- At least 4GB RAM available for Docker

### Step-by-Step Deployment

1. **Clone and Navigate**
```bash
cd /Users/aprakash2/Documents/ILS
```

2. **Create Environment File**
```bash
cp .env.example .env
```

3. **Start All Services**
```bash
docker-compose up --build
```

This single command will:
- Build backend and frontend Docker images
- Start PostgreSQL database
- Start Redis for background tasks
- Start Ollama LLM service
- Start FastAPI backend on port 8000
- Start Next.js frontend on port 3000

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health Check**: http://localhost:8000/health

### First-Time Setup

1. Wait for all services to be healthy (check logs)
2. Database tables are created automatically on first run
3. Navigate to http://localhost:3000
4. Click "Sign Up" to create your first account
5. Start using the application!

## Development Mode

### Backend Development (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://lumina:lumina_password@localhost:5432/luminalib"
export JWT_SECRET_KEY="your-secret-key"
export STORAGE_PROVIDER="local"
export LLM_PROVIDER="mock"

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development (Without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Set environment variable
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Run development server
npm run dev
```

## Testing the Application

### Manual Testing Flow

1. **Sign Up**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Fill in: email, username, password
   - Submit

2. **Login**
   - Use your credentials to login
   - You'll be redirected to /books

3. **Upload a Book** (via API)
   ```bash
   # Get auth token first
   TOKEN=$(curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"your@email.com","password":"yourpassword"}' \
     | jq -r '.access_token')
   
   # Upload a book
   curl -X POST http://localhost:8000/books \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@sample.pdf" \
     -F "title=Sample Book" \
     -F "author=John Doe" \
     -F "genre=Fiction"
   ```

4. **Browse Books**
   - Navigate to /books
   - Search and filter books
   - Click on a book to see details

5. **Borrow a Book**
   - On book detail page, click "Borrow Book"
   - Available copies will decrease

6. **Write a Review**
   - Click "Write Review" button
   - Select rating and write review text
   - Submit (AI sentiment analysis runs in background)

7. **Get Recommendations**
   - Navigate to /recommendations
   - See personalized book recommendations

## Configuration Options

### Storage Providers

Edit `.env` file:

```bash
# Local filesystem (default)
STORAGE_PROVIDER=local

# MinIO (S3-compatible)
STORAGE_PROVIDER=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# AWS S3
STORAGE_PROVIDER=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=luminalib-books
```

### LLM Providers

```bash
# Mock provider (for testing, no actual LLM)
LLM_PROVIDER=mock

# Ollama (local, free)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart specific service
docker-compose restart backend
```

### Database Connection Issues

```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U lumina

# Connect to database
docker-compose exec postgres psql -U lumina -d luminalib
```

### Frontend Build Issues

```bash
# Clear Next.js cache
cd frontend
rm -rf .next node_modules
npm install
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
```

## Production Deployment

### Environment Variables for Production

```bash
# Generate secure JWT secret
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Use production database
DATABASE_URL=postgresql://user:pass@prod-db:5432/luminalib

# Use production storage
STORAGE_PROVIDER=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Use production LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

### Production Docker Compose

For production, modify docker-compose.yml:
- Remove volume mounts for code
- Use production builds (not --reload)
- Add nginx reverse proxy
- Enable HTTPS
- Use managed database (RDS, etc.)

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

