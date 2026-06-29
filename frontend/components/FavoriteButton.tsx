'use client'

import { useState } from 'react'

interface FavoriteButtonProps {
  recipeId: number
  isFavorite?: boolean
  onToggle?: (isFav: boolean) => void
}

const DEMO_USER_ID = 1

export function FavoriteButton({
  recipeId,
  isFavorite: initialIsFavorite = false,
  onToggle,
}: FavoriteButtonProps) {
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite)
  const [loading, setLoading] = useState(false)

  const handleToggle = async () => {
    setLoading(true)

    try {
      const url = `/api/user/${DEMO_USER_ID}/favorites/${recipeId}`
      const method = isFavorite ? 'DELETE' : 'POST'

      const response = await fetch(url, { method })

      if (response.ok) {
        setIsFavorite(!isFavorite)
        onToggle?.(!isFavorite)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`px-4 py-2 rounded-lg font-semibold transition ${
        isFavorite
          ? 'bg-red-500 text-white hover:bg-red-600'
          : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
      } disabled:opacity-50`}
    >
      {loading ? '...' : isFavorite ? '❤️ В избранном' : '🤍 В избранное'}
    </button>
  )
}
