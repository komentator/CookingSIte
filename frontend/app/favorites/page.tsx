'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Recipe {
  id: number
  title: string
  cooking_time?: number
  rating?: number
  added_at?: string
}

const DEMO_USER_ID = 1

export default function FavoritesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFavorites()
  }, [])

  const loadFavorites = async () => {
    try {
      const response = await fetch(
        `/api/user/${DEMO_USER_ID}/favorites?limit=50`
      )

      if (response.ok) {
        const data = await response.json()
        setRecipes(data.recipes)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (recipeId: number) => {
    try {
      const response = await fetch(
        `/api/user/${DEMO_USER_ID}/favorites/${recipeId}`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        setRecipes(recipes.filter(r => r.id !== recipeId))
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) {
    return (
      <main className="max-w-7xl mx-auto px-4 py-12">
        <p className="text-center text-gray-500">Загружаю избранное...</p>
      </main>
    )
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-12">❤️ Мое избранное</h1>

      {recipes.length === 0 ? (
        <div className="bg-gray-50 border-2 border-gray-300 rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg mb-6">
            У вас еще нет избранных рецептов
          </p>
          <Link
            href="/search"
            className="inline-block px-6 py-3 bg-orange-500 text-white font-bold rounded-lg hover:bg-orange-600 transition"
          >
            Найти рецепты →
          </Link>
        </div>
      ) : (
        <div>
          <p className="text-gray-600 mb-8">
            Всего: <strong>{recipes.length}</strong> рецептов
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2">
                  {recipe.title}
                </h3>

                <div className="flex gap-3 text-sm text-gray-600 mb-4">
                  {recipe.cooking_time && (
                    <span>⏱️ {recipe.cooking_time} мин</span>
                  )}
                  {recipe.rating && (
                    <span className="text-orange-600 font-semibold">
                      ⭐ {recipe.rating.toFixed(1)}
                    </span>
                  )}
                </div>

                {recipe.added_at && (
                  <p className="text-xs text-gray-500 mb-4">
                    Добавлено: {new Date(recipe.added_at).toLocaleDateString('ru-RU')}
                  </p>
                )}

                <div className="flex gap-2">
                  <Link
                    href={`/recipes#recipe-${recipe.id}`}
                    className="flex-1 px-3 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 transition text-center font-semibold"
                  >
                    Рецепт
                  </Link>
                  <button
                    onClick={() => handleRemove(recipe.id)}
                    className="px-3 py-2 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 transition font-semibold"
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  )
}
