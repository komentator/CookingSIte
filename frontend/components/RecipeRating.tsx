'use client'

import { useState } from 'react'

interface RecipeRatingProps {
  recipeId: number
  initialRating: number
  reviewsCount: number
  onReviewAdded?: () => void
}

interface Review {
  rating: number
  comment?: string
}

export function RecipeRating({
  recipeId,
  initialRating,
  reviewsCount,
  onReviewAdded,
}: RecipeRatingProps) {
  const [rating, setRating] = useState(initialRating)
  const [userRating, setUserRating] = useState(0)
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmitReview = async () => {
    if (userRating === 0) return

    setIsSubmitting(true)
    try {
      const response = await fetch(
        `/api/recipes/${recipeId}/reviews`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 1, // Demo user
            rating: userRating,
            comment: comment || null,
          }),
        }
      )

      if (response.ok) {
        setSubmitted(true)
        setUserRating(0)
        setComment('')
        setTimeout(() => {
          setShowReviewForm(false)
          setSubmitted(false)
          onReviewAdded?.()
        }, 1500)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const StarRating = ({ value, onRate, interactive = false }: any) => (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => interactive && onRate(star)}
          className={`text-2xl transition ${
            star <= value ? 'text-yellow-400' : 'text-gray-300'
          } ${interactive ? 'cursor-pointer hover:scale-110' : 'cursor-default'}`}
        >
          ★
        </button>
      ))}
    </div>
  )

  return (
    <div className="bg-white rounded-lg p-6 shadow-md">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">⭐ Оценка рецепта</h3>
          <div className="flex items-center gap-4">
            <div>
              <StarRating value={Math.round(rating)} />
              <p className="text-2xl font-bold text-gray-900 mt-2">
                {rating.toFixed(1)}
              </p>
            </div>
            <div className="text-gray-600">
              <p className="text-sm">на основе</p>
              <p className="text-xl font-bold">{reviewsCount} отзывов</p>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowReviewForm(!showReviewForm)}
          className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-semibold"
        >
          ✍️ Написать отзыв
        </button>
      </div>

      {showReviewForm && (
        <div className="border-t pt-6 mt-6">
          {submitted ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <p className="text-green-800 font-semibold">✅ Спасибо за отзыв!</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Ваша оценка:
                </label>
                <StarRating value={userRating} onRate={setUserRating} interactive={true} />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Ваш комментарий (опционально):
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Поделитесь своим мнением о рецепте..."
                  maxLength={500}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                  rows={3}
                  disabled={isSubmitting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {comment.length}/500
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSubmitReview}
                  disabled={userRating === 0 || isSubmitting}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition font-semibold"
                >
                  {isSubmitting ? 'Отправка...' : '✅ Отправить отзыв'}
                </button>
                <button
                  onClick={() => setShowReviewForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                >
                  ✕
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
