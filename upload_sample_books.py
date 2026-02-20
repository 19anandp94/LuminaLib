#!/usr/bin/env python3
import requests
import time

# Login to get token
print("🔐 Logging in...")
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "testuser@example.com", "password": "testpass123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token obtained\n")

# Sample books data
books = [
    {
        "title": "The Great Adventure",
        "author": "John Smith",
        "genre": "Adventure",
        "description": "An epic journey through uncharted territories",
        "published_year": 2023,
        "total_copies": 5,
        "content": "The Great Adventure\n\nChapter 1: The Beginning\nThe sun rose over the mountains as our hero began the journey of a lifetime.\n\nChapter 2: The Challenge\nObstacles appeared at every turn, testing courage and resolve.\n\nChapter 3: The Discovery\nIn the heart of the wilderness, a profound discovery changed everything.\n\nThe End"
    },
    {
        "title": "Mystery at Midnight Manor",
        "author": "Sarah Detective",
        "genre": "Mystery",
        "description": "A thrilling detective story with unexpected twists",
        "published_year": 2024,
        "total_copies": 3,
        "content": "Mystery at Midnight Manor\n\nChapter 1: The Invitation\nDetective Sarah received a mysterious invitation to Midnight Manor.\n\nChapter 2: The Crime\nA priceless artifact had vanished without a trace.\n\nChapter 3: The Solution\nThrough careful observation and brilliant deduction, the truth finally emerged.\n\nThe End"
    },
    {
        "title": "Love in Paris",
        "author": "Emma Romance",
        "genre": "Romance",
        "description": "A heartwarming tale of love found in the City of Light",
        "published_year": 2024,
        "total_copies": 4,
        "content": "Love in Paris\n\nChapter 1: The Meeting\nTwo strangers met by chance at a café in Montmartre.\n\nChapter 2: The Connection\nAs they explored Paris together, their connection deepened.\n\nChapter 3: Forever\nUnder the Eiffel Tower at sunset, they realized they had found true love.\n\nThe End"
    },
    {
        "title": "The Science of Tomorrow",
        "author": "Dr. Tech Innovator",
        "genre": "Science Fiction",
        "description": "Exploring the possibilities of future technology",
        "published_year": 2024,
        "total_copies": 3,
        "content": "The Science of Tomorrow\n\nChapter 1: The Invention\nIn a laboratory, a breakthrough changed the course of human history.\n\nChapter 2: The Implications\nAs the invention spread, society transformed in ways both wonderful and concerning.\n\nChapter 3: The Future\nHumanity stood at a crossroads, choosing between different possible futures.\n\nThe End"
    },
    {
        "title": "Cooking with Joy",
        "author": "Chef Maria",
        "genre": "Cooking",
        "description": "Delicious recipes and culinary adventures",
        "published_year": 2023,
        "total_copies": 6,
        "content": "Cooking with Joy\n\nChapter 1: The Basics\nGreat cooking starts with understanding ingredients and techniques.\n\nChapter 2: The Recipes\nFrom simple comfort food to elegant dishes, each recipe tells a story.\n\nChapter 3: The Joy\nCooking is not just about feeding the body, but nourishing the soul.\n\nThe End"
    }
]

print("📚 Uploading sample books...\n")

for i, book in enumerate(books, 1):
    # Create a temporary file with the book content
    filename = f"/tmp/book_{i}.txt"
    with open(filename, "w") as f:
        f.write(book["content"])
    
    # Upload the book
    with open(filename, "rb") as f:
        files = {"file": (f"{book['title']}.txt", f, "text/plain")}
        data = {
            "title": book["title"],
            "author": book["author"],
            "genre": book["genre"],
            "description": book["description"],
            "published_year": book["published_year"],
            "total_copies": book["total_copies"]
        }
        
        response = requests.post(
            "http://localhost:8000/books",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            print(f"✅ {i}. {book['title']} by {book['author']} ({book['genre']})")
        else:
            print(f"❌ {i}. Failed: {book['title']} - {response.text}")
    
    time.sleep(0.5)

print("\n✅ All books uploaded successfully!\n")
print("📊 Fetching book list...\n")

# Get all books
response = requests.get("http://localhost:8000/books", headers=headers)
books_data = response.json()
print(f"Total books in library: {books_data['total']}\n")
for book in books_data['items']:
    print(f"  📖 {book['title']} by {book['author']} ({book['genre']})")

