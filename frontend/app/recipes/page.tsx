'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRecipes()
  }, [])

  const loadRecipes = async () => {
    try {
      setError(null)
      const data = await api.getRecipes()
      setRecipes(data)
    } catch (err) {
      console.error(err)
      setError('Не удалось загрузить рецепты. Проверьте, что backend API запущен на http://localhost:8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-4xl font-bold text-gray-900 mb-8">📖 Все рецепты</h2>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Загружаю рецепты...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800">{error}</p>
        </div>
      ) : recipes.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <p className="text-yellow-800">Рецепты еще не добавлены. Добавьте рецепты через API.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes.map((recipe) => (
            <Link
              key={recipe.id}
              href={`/recipes/${recipe.id}`}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl hover:-translate-y-1 transition block"
            >
              <h3 className="text-xl font-bold text-gray-900 mb-2">{recipe.title}</h3>

              {recipe.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{recipe.description}</p>
              )}

              <div className="flex gap-4 text-sm text-gray-600 mb-4 flex-wrap">
                {recipe.cooking_time && <span>⏱️ {recipe.cooking_time} мин</span>}
                {recipe.servings && <span>🍽️ {recipe.servings} порций</span>}
                {recipe.calories && <span>🔥 {recipe.calories} ккал</span>}
              </div>

              {recipe.ingredients && recipe.ingredients.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-semibold text-gray-700 mb-2">
                    Ингредиенты: {recipe.ingredients.length}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {recipe.ingredients.slice(0, 3).map((ing: any, idx: number) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
                        {ing.ingredient?.name || 'ингредиент'}
                      </span>
                    ))}
                    {recipe.ingredients.length > 3 && (
                      <span className="text-xs text-gray-600">+{recipe.ingredients.length - 3}</span>
                    )}
                  </div>
                </div>
              )}

              <span className="inline-block px-4 py-2 bg-orange-500 text-white text-sm rounded-lg">
                Открыть рецепт →
              </span>
            </Link>
          ))}
        </div>
      )}
    </main>
  )
}
