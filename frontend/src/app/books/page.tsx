/**
 * Books Page
 * 
 * Main books listing page with search and filtering.
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useBooks } from '@/lib/hooks/useBooks';
import { BookList } from '@/components/books/BookList';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import type { Book } from '@/lib/api/types';

export default function BooksPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  
  const { data, isLoading } = useBooks({ page, search: searchQuery });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(search);
    setPage(1);
  };

  const handleBookClick = (book: Book) => {
    router.push(`/books/${book.id}`);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Browse Books</h1>
        
        <form onSubmit={handleSearch} className="flex gap-4 max-w-2xl">
          <Input
            type="text"
            placeholder="Search by title or author..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1"
          />
          <Button type="submit">Search</Button>
        </form>
      </div>

      <BookList
        books={data?.items || []}
        isLoading={isLoading}
        onBookClick={handleBookClick}
      />

      {data && data.pages > 1 && (
        <div className="mt-8 flex justify-center gap-2">
          <Button
            variant="secondary"
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </Button>
          <span className="px-4 py-2 text-gray-700">
            Page {page} of {data.pages}
          </span>
          <Button
            variant="secondary"
            disabled={page === data.pages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

