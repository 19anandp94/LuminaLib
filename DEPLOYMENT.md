# LuminaLib Deployment Guide

## Quick Start (One-Command Deployment)

### Prerequisites

- **Docker Desktop** installed and running
- **Git** for cloning the repository
- At least **4GB RAM** available for Docker
- **8GB disk space** for images and data

### Step-by-Step Deployment

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd ILS
```

#### 2. Create Environment File

```bash
cp .env.example .env
```

**Optional**: Edit `.env` to customize configuration (database credentials, JWT secret, etc.)

#### 3. Start All Services

```bash
docker-compose up -d --build
```

**Note**: Use `-d` flag to run in detached mode (background).

This command will:

- Build backend (FastAPI) and frontend (Next.js) Docker images
- Start PostgreSQL 16 database on port 5432
- Start Redis 7 for caching on port 6379
- Start Ollama LLM service on port 11434
- Start FastAPI backend on port 8000
- Start Next.js frontend on port 3000

#### 4. Wait for Services to Start

```bash
# Check service status
docker-compose ps

# Watch logs to ensure all services are healthy
docker-compose logs -f
```

Wait until you see:

- `backend` - "Application startup complete"
- `frontend` - "Ready in X ms"
- `postgres` - "database system is ready to accept connections"

Press `Ctrl+C` to stop following logs (services continue running).

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs (Swagger)**: http://localhost:8000/docs
- **Backend Health Check**: http://localhost:8000/health

### First-Time Setup

1. **Create an Account**
   - Navigate to http://localhost:3000
   - Click "Sign Up"
   - Enter email and password
   - You'll be automatically logged in

2. **Populate Sample Data** (Optional but Recommended)
   - See [Populating Sample Data](#populating-sample-data) section below

3. **Start Using the Application**
   - Browse books at http://localhost:3000/books
   - Search for books by title or author
   - Borrow books and write reviews
   - Get personalized recommendations

## Populating Sample Data

### Automated Sample Data Upload

The repository includes a script to upload sample books for testing. This is **highly recommended** for first-time setup.

#### Step 1: Create Sample Book Files

```bash
# Create a directory for sample books
mkdir -p sample_books

# Create sample text files
cat > sample_books/adventure.txt << 'EOF'
The Great Adventure

Chapter 1: The Journey Begins

In a land far away, a young hero embarked on an epic quest to find the legendary treasure of the ancient kingdom. Along the way, they encountered mystical creatures, solved ancient riddles, and discovered the true meaning of courage.

The journey was filled with danger and excitement at every turn. From crossing treacherous mountains to navigating through enchanted forests, our hero's determination never wavered.

This is a story of bravery, friendship, and the pursuit of dreams.
EOF

cat > sample_books/mystery.txt << 'EOF'
Mystery at Midnight Manor

Chapter 1: The Invitation

Detective Sarah received a mysterious invitation to Midnight Manor. Upon arrival, she discovered that the mansion held dark secrets and unsolved mysteries from decades past.

As the clock struck midnight, strange events began to unfold. Doors creaked open on their own, shadows moved in the hallways, and whispers echoed through the empty rooms.

Sarah knew she had to solve the mystery before it was too late.
EOF

cat > sample_books/romance.txt << 'EOF'
Love in Paris

Chapter 1: A Chance Encounter

Emma never expected to find love when she moved to Paris for work. But a chance encounter at a small café changed everything.

The city of lights became the backdrop for a beautiful love story filled with passion, laughter, and unforgettable moments. From strolls along the Seine to candlelit dinners in hidden bistros, every moment was magical.

This is a tale of two hearts finding each other in the most romantic city in the world.
EOF

cat > sample_books/scifi.txt << 'EOF'
Journey to the Stars

Chapter 1: First Contact

In the year 2157, humanity made first contact with an alien civilization. Captain Alex Chen led the mission to establish diplomatic relations and explore the far reaches of the galaxy.

Advanced technology, interstellar travel, and encounters with diverse alien species awaited the crew. Each discovery brought new questions about the nature of the universe and humanity's place in it.

This is a story of exploration, discovery, and the infinite possibilities of the cosmos.
EOF

cat > sample_books/cooking.txt << 'EOF'
The Art of Home Cooking

Chapter 1: Mastering the Basics

Cooking is both an art and a science. This comprehensive guide will teach you everything from basic knife skills to advanced culinary techniques.

Learn how to prepare delicious meals using fresh, seasonal ingredients. Discover the secrets of flavor combinations, proper seasoning, and presentation that will impress your family and friends.

From simple weeknight dinners to elaborate holiday feasts, this book has recipes for every occasion.
EOF
```

#### Step 2: Run the Upload Script

**Option A: Using the Provided Script** (if available)

```bash
# Make the script executable
chmod +x upload_books.sh

# Run the script
./upload_books.sh
```

**Option B: Manual Upload via API**

```bash
# First, create an account and get the auth token
# Sign up via the web interface at http://localhost:3000/signup
# Or use the API:

# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demo123"
  }'

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demo123"
  }' | jq -r '.access_token')

# Upload books
curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/adventure.txt" \
  -F "title=The Great Adventure" \
  -F "author=John Smith" \
  -F "genre=Adventure"

curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/mystery.txt" \
  -F "title=Mystery at Midnight Manor" \
  -F "author=Jane Doe" \
  -F "genre=Mystery"

curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/romance.txt" \
  -F "title=Love in Paris" \
  -F "author=Emily Rose" \
  -F "genre=Romance"

curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/scifi.txt" \
  -F "title=Journey to the Stars" \
  -F "author=Alex Chen" \
  -F "genre=Science Fiction"

curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/cooking.txt" \
  -F "title=The Art of Home Cooking" \
  -F "author=Chef Maria" \
  -F "genre=Cooking"
```

#### Step 3: Verify Upload

```bash
# List all books
curl http://localhost:8000/books | jq

# Or visit http://localhost:3000/books in your browser
```

**Note**: AI summarization runs in the background. Summaries will appear after a few seconds/minutes depending on the LLM provider.

### Testing the Full Workflow

After populating sample data, test the complete functionality:

1. **Search**: Search for "Adventure" or "Mystery"
2. **Filter**: Filter by genre (e.g., "Romance")
3. **Borrow**: Click on a book and borrow it
4. **Review**: Write a review (rating + text)
5. **Sentiment Analysis**: Check the review analysis (runs in background)
6. **Recommendations**: Visit /recommendations to see personalized suggestions

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

#### 1. Sign Up & Login

- Navigate to http://localhost:3000
- Click "Sign Up"
- Enter email and password
- Submit (you'll be automatically logged in and redirected to /books)

#### 2. Browse Books

- View all available books
- Use the **search bar** to search by title or author
- Click on any book card to see details

#### 3. Search & Filter

Test the search functionality:

- Search for "Adventure" - should find "The Great Adventure"
- Search for "John" - should find books by "John Smith"
- Filter by genre (if UI supports it)

Via API:

```bash
curl "http://localhost:8000/books?search=adventure"
curl "http://localhost:8000/books?genre=Mystery"
curl "http://localhost:8000/books?author=John"
```

#### 4. View Book Details

- Click on a book
- See book metadata (title, author, genre)
- Check AI-generated summary (may take 10-30 seconds to appear)
- View existing reviews

#### 5. Borrow a Book

- Click "Borrow Book" button
- Book status changes to "Borrowed"
- You can now write a review

#### 6. Write a Review

- Click "Write Review" button (only available after borrowing)
- Select rating (1-5 stars)
- Write review text
- Submit
- **AI sentiment analysis runs in background** - refresh after a few seconds to see sentiment

#### 7. Return a Book

- Click "Return Book" button
- Book becomes available again

#### 8. Get Recommendations

- Navigate to http://localhost:3000/recommendations
- See personalized ML-based recommendations based on:
  - Books you've borrowed
  - Genres you prefer
  - Your review history

### API Testing via Swagger UI

1. Navigate to http://localhost:8000/docs
2. Test endpoints interactively:
   - Click "Authorize" button
   - Login via `POST /auth/login` to get token
   - Copy the `access_token` from response
   - Click "Authorize" again and paste: `Bearer <token>`
3. Now you can test any protected endpoint

### Testing AI Features

#### Test Book Summarization

```bash
# Get your auth token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}' \
  | jq -r '.access_token')

# Upload a book
BOOK_ID=$(curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_books/adventure.txt" \
  -F "title=Test Book" \
  -F "author=Test Author" \
  -F "genre=Fiction" \
  | jq -r '.id')

# Wait 10-30 seconds for AI summarization
sleep 30

# Check if summary was generated
curl http://localhost:8000/books/$BOOK_ID | jq '.summary'
```

#### Test Sentiment Analysis

```bash
# Create a review
curl -X POST http://localhost:8000/books/$BOOK_ID/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "text": "This book was absolutely amazing! I loved every page."
  }'

# Wait a few seconds for sentiment analysis
sleep 5

# Check the review with sentiment
curl http://localhost:8000/books/$BOOK_ID/reviews | jq
```

#### Test Recommendations

```bash
# Get personalized recommendations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/recommendations | jq

# Get similar books to a specific book
curl http://localhost:8000/recommendations/similar/$BOOK_ID | jq
```

## Configuration Options

All configuration is managed via the `.env` file. Copy `.env.example` to `.env` and customize as needed.

### Database Configuration

```bash
# PostgreSQL connection string (async driver)
DATABASE_URL=postgresql+asyncpg://lumina:lumina_password@postgres:5432/luminalib

# Database credentials (for docker-compose)
POSTGRES_USER=lumina
POSTGRES_PASSWORD=lumina_password
POSTGRES_DB=luminalib
```

### JWT Authentication

```bash
# Secret key for JWT token signing (change in production!)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Generate a secure secret key for production:

```bash
openssl rand -hex 32
```

### Storage Providers

Choose where to store uploaded book files:

```bash
# Option 1: Local filesystem (default, good for development)
STORAGE_PROVIDER=local
STORAGE_LOCAL_PATH=/app/book_storage

# Option 2: AWS S3 (recommended for production)
STORAGE_PROVIDER=s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=luminalib-books
AWS_REGION=us-east-1
```

**Note**: MinIO support was removed in favor of simpler local/S3 options.

### LLM Providers

Choose which LLM to use for AI features (summarization, sentiment analysis):

```bash
# Option 1: Mock provider (for testing, no actual LLM calls)
LLM_PROVIDER=mock

# Option 2: Ollama (local, free, default)
LLM_PROVIDER=ollama
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://ollama:11434

# Option 3: OpenAI (requires API key)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

**Recommendations**:

- **Development**: Use `mock` for fast testing without LLM overhead
- **Local Testing**: Use `ollama` for free local LLM (requires Ollama service running)
- **Production**: Use `openai` for best quality (costs money)

### CORS Configuration

```bash
# Allowed origins for CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

Add your production frontend URL when deploying.

### API Configuration

```bash
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend Configuration

```bash
# Backend API URL (used by Next.js frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Change to your production backend URL when deploying.

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

### Docker Build Failures (Network Issues)

If you encounter network errors during `docker-compose build`:

```
failed to resolve source metadata for docker.io/library/python:3.11-slim
dial tcp: lookup registry-1.docker.io: no such host
```

**Solution**: Update running container without rebuilding:

```bash
# Copy updated files into running container
docker cp backend/app/routers/books.py luminalib-backend:/app/app/routers/books.py

# Restart the container to pick up changes
docker-compose restart backend

# Verify the changes
docker logs luminalib-backend --tail 20
```

This bypasses the need to rebuild and works even with network issues.

### Docker Desktop Not Running

If you see `zsh: command not found: docker`:

1. **Open Docker Desktop** from Applications
2. **Wait for it to fully start** (whale icon in menu bar stops animating)
3. **Verify**: `docker --version`

### Database Schema Mismatch

If you get database errors after code changes:

```bash
# Option 1: Reset database (WARNING: deletes all data)
docker-compose down
docker volume rm ils_postgres_data
docker-compose up -d

# Option 2: Run migrations (if using Alembic)
docker-compose exec backend alembic upgrade head
```

### Reviews Not Showing

If reviews don't appear on the book detail page:

1. **Check if backend has latest code**:

   ```bash
   docker logs luminalib-backend | grep "GET /books/.*/reviews"
   ```

2. **Update backend code** (if needed):

   ```bash
   docker cp backend/app/routers/books.py luminalib-backend:/app/app/routers/books.py
   docker-compose restart backend
   ```

3. **Verify endpoint works**:
   ```bash
   curl http://localhost:8000/books/1/reviews
   ```

### Search Not Working

If search returns no results:

1. **Check backend logs**:

   ```bash
   docker logs luminalib-backend -f
   ```

2. **Test search endpoint**:

   ```bash
   curl "http://localhost:8000/books?search=adventure"
   ```

3. **Update backend if needed** (see Docker Build Failures section above)

### AI Features Not Working

**Summarization not generating**:

- Check LLM provider is configured: `echo $LLM_PROVIDER`
- Check Ollama is running: `docker-compose ps ollama`
- Check backend logs: `docker logs luminalib-backend | grep -i "llm\|summary"`
- Try mock provider for testing: Set `LLM_PROVIDER=mock` in `.env`

**Sentiment analysis not working**:

- Same as above
- Check review was created after borrowing the book
- Wait 5-10 seconds for background task to complete

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
