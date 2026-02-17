/**
 * BookCard Component
 * 
 * Displays a book in card format with key information.
 */
import React from 'react';
import { Card } from '../ui/Card';
import type { Book } from '@/lib/api/types';

interface BookCardProps {
  book: Book;
  onClick?: () => void;
}

export const BookCard: React.FC<BookCardProps> = ({ book, onClick }) => {
  return (
    <Card onClick={onClick}>
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
          {book.title}
        </h3>
        <p className="text-sm text-gray-600">by {book.author}</p>
        
        {book.genre && (
          <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded">
            {book.genre}
          </span>
        )}
        
        {book.description && (
          <p className="text-sm text-gray-700 line-clamp-3 mt-2">
            {book.description}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-4 pt-4 border-t">
          <span className="text-sm text-gray-600">
            {book.available_copies} / {book.total_copies} available
          </span>
          {book.published_year && (
            <span className="text-sm text-gray-500">{book.published_year}</span>
          )}
        </div>
      </div>
    </Card>
  );
};

