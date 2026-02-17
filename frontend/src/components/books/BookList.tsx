/**
 * BookList Component
 * 
 * Displays a grid of books with loading and empty states.
 */
import React from 'react';
import { BookCard } from './BookCard';
import type { Book } from '@/lib/api/types';

interface BookListProps {
  books: Book[];
  isLoading?: boolean;
  onBookClick?: (book: Book) => void;
}

export const BookList: React.FC<BookListProps> = ({ books, isLoading, onBookClick }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (books.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No books found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {books.map((book) => (
        <BookCard
          key={book.id}
          book={book}
          onClick={() => onBookClick?.(book)}
        />
      ))}
    </div>
  );
};

