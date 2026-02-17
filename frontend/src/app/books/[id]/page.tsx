/**
 * Book Detail Page
 * 
 * Displays detailed book information with borrow/return and reviews.
 */
'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useBook, useBorrowBook, useReturnBook } from '@/lib/hooks/useBooks';
import { useReviews, useCreateReview } from '@/lib/hooks/useReviews';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';

export default function BookDetailPage() {
  const params = useParams();
  const bookId = parseInt(params.id as string);
  
  const { data: book, isLoading } = useBook(bookId);
  const { data: reviews } = useReviews(bookId);
  const borrowMutation = useBorrowBook();
  const returnMutation = useReturnBook();
  const createReviewMutation = useCreateReview();
  
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState('');

  const handleBorrow = async () => {
    try {
      await borrowMutation.mutateAsync(bookId);
      alert('Book borrowed successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to borrow book');
    }
  };

  const handleReturn = async () => {
    try {
      await returnMutation.mutateAsync(bookId);
      alert('Book returned successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to return book');
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createReviewMutation.mutateAsync({
        bookId,
        data: { rating, review_text: reviewText },
      });
      setShowReviewModal(false);
      setReviewText('');
      setRating(5);
      alert('Review submitted successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit review');
    }
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (!book) {
    return <div className="text-center py-12">Book not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">{book.title}</h1>
        <p className="text-xl text-gray-600 mb-4">by {book.author}</p>
        
        <div className="flex gap-4 mb-6">
          {book.genre && (
            <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
              {book.genre}
            </span>
          )}
          {book.published_year && (
            <span className="text-gray-600">{book.published_year}</span>
          )}
        </div>

        {book.description && (
          <p className="text-gray-700 mb-6">{book.description}</p>
        )}

        {book.ai_summary && (
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">AI Summary</h3>
            <p className="text-gray-700">{book.ai_summary}</p>
          </div>
        )}

        <div className="flex gap-4 mb-6">
          <Button onClick={handleBorrow} disabled={book.available_copies === 0}>
            Borrow Book ({book.available_copies} available)
          </Button>
          <Button variant="secondary" onClick={handleReturn}>
            Return Book
          </Button>
          <Button variant="secondary" onClick={() => setShowReviewModal(true)}>
            Write Review
          </Button>
        </div>
      </Card>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Reviews</h2>
        {reviews && reviews.length > 0 ? (
          <div className="space-y-4">
            {reviews.map((review) => (
              <Card key={review.id}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-yellow-500">{'⭐'.repeat(review.rating)}</span>
                  {review.sentiment_label && (
                    <span className="text-sm text-gray-600">({review.sentiment_label})</span>
                  )}
                </div>
                {review.review_text && <p className="text-gray-700">{review.review_text}</p>}
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No reviews yet</p>
        )}
      </div>

      <Modal isOpen={showReviewModal} onClose={() => setShowReviewModal(false)} title="Write a Review">
        <form onSubmit={handleSubmitReview} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Rating</label>
            <select
              value={rating}
              onChange={(e) => setRating(parseInt(e.target.value))}
              className="w-full px-3 py-2 border rounded-lg"
            >
              {[1, 2, 3, 4, 5].map((r) => (
                <option key={r} value={r}>
                  {r} Star{r > 1 ? 's' : ''}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Review (optional)"
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Share your thoughts..."
          />
          <Button type="submit" className="w-full" isLoading={createReviewMutation.isPending}>
            Submit Review
          </Button>
        </form>
      </Modal>
    </div>
  );
}

