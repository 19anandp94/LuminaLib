/**
 * Recommendations Page
 * 
 * Displays ML-based personalized book recommendations.
 */
'use client';

import { useRouter } from 'next/navigation';
import { useRecommendations } from '@/lib/hooks/useRecommendations';
import { BookList } from '@/components/books/BookList';
import type { Book } from '@/lib/api/types';

export default function RecommendationsPage() {
  const router = useRouter();
  const { data: recommendations, isLoading } = useRecommendations(12);

  const handleBookClick = (book: Book) => {
    router.push(`/books/${book.id}`);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Recommended for You
        </h1>
        <p className="text-gray-600">
          Personalized book recommendations based on your reading history and preferences
        </p>
      </div>

      <BookList
        books={recommendations || []}
        isLoading={isLoading}
        onBookClick={handleBookClick}
      />
    </div>
  );
}

