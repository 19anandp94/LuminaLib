/**
 * Home Page
 * 
 * Landing page with SSR support.
 */
'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/Button';

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="text-center">
      <h1 className="text-5xl font-bold text-gray-900 mb-4">
        Welcome to LuminaLib
      </h1>
      <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        Your intelligent library system powered by AI. Discover books, get personalized
        recommendations, and join a community of readers.
      </p>
      
      {isAuthenticated ? (
        <div className="space-x-4">
          <Link href="/books">
            <Button size="lg">Browse Books</Button>
          </Link>
          <Link href="/recommendations">
            <Button variant="secondary" size="lg">
              Get Recommendations
            </Button>
          </Link>
        </div>
      ) : (
        <div className="space-x-4">
          <Link href="/signup">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/login">
            <Button variant="secondary" size="lg">
              Login
            </Button>
          </Link>
        </div>
      )}
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        <div className="p-6">
          <div className="text-4xl mb-4">📚</div>
          <h3 className="text-lg font-semibold mb-2">Vast Collection</h3>
          <p className="text-gray-600">
            Access thousands of books across various genres
          </p>
        </div>
        <div className="p-6">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-lg font-semibold mb-2">AI-Powered</h3>
          <p className="text-gray-600">
            Get intelligent summaries and personalized recommendations
          </p>
        </div>
        <div className="p-6">
          <div className="text-4xl mb-4">⭐</div>
          <h3 className="text-lg font-semibold mb-2">Community Reviews</h3>
          <p className="text-gray-600">
            Read and share reviews with sentiment analysis
          </p>
        </div>
      </div>
    </div>
  );
}

