#!/bin/bash

echo "📚 Starting book upload process..."
echo ""

# Login and get token
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"testpass123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token obtained"
echo ""

# Create book files
echo "📝 Creating book files..."

cat > /tmp/book1.txt << 'EOF'
The Great Adventure

Chapter 1: The Beginning
The sun rose over the mountains as our hero began the journey of a lifetime.
With nothing but a backpack and determination, the path ahead was uncertain but exciting.

Chapter 2: The Challenge
Obstacles appeared at every turn, testing courage and resolve. But with each challenge 
overcome, strength grew and wisdom deepened.

Chapter 3: The Discovery
In the heart of the wilderness, a profound discovery changed everything. The journey 
was not just about reaching the destination, but about the transformation along the way.

The End
EOF

cat > /tmp/book2.txt << 'EOF'
Mystery at Midnight Manor

Chapter 1: The Invitation
Detective Sarah received a mysterious invitation to Midnight Manor. Something felt wrong 
from the very beginning.

Chapter 2: The Crime
A priceless artifact had vanished without a trace. The suspects all had alibis, but 
someone was lying.

Chapter 3: The Solution
Through careful observation and brilliant deduction, the truth finally emerged. The 
culprit was the least expected person.

The End
EOF

cat > /tmp/book3.txt << 'EOF'
Love in Paris

Chapter 1: The Meeting
Two strangers met by chance at a café in Montmartre. Their eyes met, and something 
magical happened.

Chapter 2: The Connection
As they explored Paris together, their connection deepened. Every moment felt like 
a scene from a movie.

Chapter 3: Forever
Under the Eiffel Tower at sunset, they realized they had found something rare and 
beautiful - true love.

The End
EOF

cat > /tmp/book4.txt << 'EOF'
The Science of Tomorrow

Chapter 1: The Invention
In a laboratory, a breakthrough changed the course of human history. Technology had 
finally caught up with imagination.

Chapter 2: The Implications
As the invention spread, society transformed in ways both wonderful and concerning. 
Progress always comes with responsibility.

Chapter 3: The Future
Humanity stood at a crossroads, choosing between different possible futures. The 
decisions made today would echo through generations.

The End
EOF

cat > /tmp/book5.txt << 'EOF'
Cooking with Joy

Chapter 1: The Basics
Great cooking starts with understanding ingredients and techniques. Master the 
fundamentals and creativity will follow.

Chapter 2: The Recipes
From simple comfort food to elegant dishes, each recipe tells a story. Food is 
love made visible.

Chapter 3: The Joy
Cooking is not just about feeding the body, but nourishing the soul. Share your 
creations and spread happiness.

The End
EOF

echo "✅ Book files created"
echo ""
echo "📤 Uploading books..."
echo ""

# Upload books
curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/book1.txt" \
  -F "title=The Great Adventure" \
  -F "author=John Smith" \
  -F "genre=Adventure" \
  -F "description=An epic journey through uncharted territories" \
  -F "published_year=2023" \
  -F "total_copies=5" > /tmp/upload1.json
echo "✅ 1. The Great Adventure - uploaded"

sleep 1

curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/book2.txt" \
  -F "title=Mystery at Midnight Manor" \
  -F "author=Sarah Detective" \
  -F "genre=Mystery" \
  -F "description=A thrilling detective story with unexpected twists" \
  -F "published_year=2024" \
  -F "total_copies=3" > /tmp/upload2.json
echo "✅ 2. Mystery at Midnight Manor - uploaded"

sleep 1

curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/book3.txt" \
  -F "title=Love in Paris" \
  -F "author=Emma Romance" \
  -F "genre=Romance" \
  -F "description=A heartwarming tale of love found in the City of Light" \
  -F "published_year=2024" \
  -F "total_copies=4" > /tmp/upload3.json
echo "✅ 3. Love in Paris - uploaded"

sleep 1

curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/book4.txt" \
  -F "title=The Science of Tomorrow" \
  -F "author=Dr. Tech Innovator" \
  -F "genre=Science Fiction" \
  -F "description=Exploring the possibilities of future technology" \
  -F "published_year=2024" \
  -F "total_copies=3" > /tmp/upload4.json
echo "✅ 4. The Science of Tomorrow - uploaded"

sleep 1

curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/book5.txt" \
  -F "title=Cooking with Joy" \
  -F "author=Chef Maria" \
  -F "genre=Cooking" \
  -F "description=Delicious recipes and culinary adventures" \
  -F "published_year=2023" \
  -F "total_copies=6" > /tmp/upload5.json
echo "✅ 5. Cooking with Joy - uploaded"

echo ""
echo "✅ All books uploaded successfully!"
echo ""
echo "📊 Fetching book list..."
curl -s http://localhost:8000/books -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

