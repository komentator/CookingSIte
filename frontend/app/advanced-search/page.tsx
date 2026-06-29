'use client'

import { useState } from 'react'
import { AdvancedSearch, AdvancedFilters } from '@/components/AdvancedSearch'
import { RecipeResults } from '@/components/RecipeResults'

interface RecipeFromAdvanced {
  id: number
  title: string
  cooking_time?: number
  servings?: number
  calories?: number
  rating?: number
  reviews_count?: number
  description?: string
  dietary_tags?: any
}

export default function AdvancedSearchPage() {
  const [results, setResults] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (filters: AdvancedFilters) => {
    setLoading(true)
    setError(null)

    try {
      // Формируем URL с параметрами
      const params = new URLSearchParams()

      if (filters.title) params.append('title', filters.title)
      if (filters.minCookingTime) params.append('min_cooking_time', filters.minCookingTime.toString())
      if (filters.maxCookingTime) params.append('max_cooking_time', filters.maxCookingTime.toString())
      if (filters.minCalories) params.append('min_calories', filters.minCalories.toString())
      if (filters.maxCalories) params.append('max_calories', filters.maxCalories.toString())
      if (filters.minRating) params.append('min_rating', filters.minRating.toString())
      if (filters.servings) params.append('servings', filters.servings.toString())
      if (filters.vegan) params.append('vegan', 'true')
      if (filters.vegetarian) params.append('vegetarian', 'true')
      if (filters.glutenFree) params.append('gluten_free', 'true')

      // Если есть диетические фильтры, используем их endpoint
      if (filters.vegan || filters.vegetarian || filters.glutenFree) {
        const response = await fetch(
          `/api/recipes/filter/dietary?${params.toString()}`
        )

        if (response.ok) {
          const data = await response.json()
          setResults({
            can_cook_now: [],
            need_buy_1_2: [],
            need_many: data.recipes || [],
            total: data.count || 0
          })
        }
      } else {
        // Обычный поиск по всем рецептам
        const response = await fetch('/api/recipes?limit=100')

        if (response.ok) {
          let recipes = await response.json()

          // Фильтруем по полученным параметрам
          if (filters.title) {
            recipes = recipes.filter((r: any) =>
              r.title.toLowerCase().includes(filters.title!.toLowerCase())
            )
          }
          if (filters.minCookingTime) {
            recipes = recipes.filter((r: any) => r.cooking_time >= filters.minCookingTime!)
          }
          if (filters.maxCookingTime) {
            recipes = recipes.filter((r: any) => r.cooking_time <= filters.maxCookingTime!)
          }
          if (filters.minCalories) {
            recipes = recipes.filter((r: any) => r.calories >= filters.minCalories!)
          }
          if (filters.maxCalories) {
            recipes = recipes.filter((r: any) => r.calories <= filters.maxCalories!)
          }
          if (filters.minRating) {
            recipes = recipes.filter((r: any) => r.rating >= filters.minRating!)
          }

          setResults({
            can_cook_now: [],
            need_buy_1_2: [],
            need_many: recipes,
            total: recipes.length
          })
        }
      }
    } catch (err) {
      setError('Ошибка при поиске')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">🔎 Расширенный поиск</h1>
      <p className="text-gray-600 mb-12">
        Найдите рецепты по специфическим критериям
      </p>

      <div className="mb-12">
        <AdvancedSearch onSearch={handleSearch} loading={loading} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {results && results.total > 0 ? (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            📊 Найдено рецептов: {results.total}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.need_many.map((recipe: RecipeFromAdvanced) => (
              <div
                key={recipe.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                  {recipe.title}
                </h3>

                <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-4">
                  {recipe.cooking_time && (
                    <span>⏱️ {recipe.cooking_time} мин</span>
                  )}
                  {recipe.calories && (
                    <span>🔥 {recipe.calories} ккал</span>
                  )}
                  {recipe.servings && (
                    <span>🍽️ {recipe.servings} порций</span>
                  )}
                  {recipe.rating && (
                    <span className="text-orange-600 font-semibold">
                      ⭐ {recipe.rating.toFixed(1)}
                    </span>
                  )}
                </div>

                <a
                  href={`/recipes#recipe-${recipe.id}`}
                  className="inline-block px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-semibold"
                >
                  Подробнее →
                </a>
              </div>
            ))}
          </div>
        </div>
      ) : !results && !loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            Используйте фильтры выше для поиска рецептов
          </p>
        </div>
      ) : loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Ищу рецепты...</p>
        </div>
      ) : (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-8 text-center">
          <p className="text-yellow-800 text-lg font-semibold">
            😞 Рецепты не найдены
          </p>
        </div>
      )}

      <div className="mt-12 bg-indigo-50 border-2 border-indigo-200 rounded-lg p-6">
        <h3 className="font-bold text-gray-900 mb-3">💡 Советы поиска</h3>
        <ul className="space-y-2 text-gray-700 text-sm">
          <li>• Оставьте поля пустыми, чтобы не применять ограничения</li>
          <li>• Диетические ограничения работают в комбинации</li>
          <li>• Рейтинг показывает среднюю оценку от пользователей</li>
          <li>• Используйте название для поиска по ключевым словам</li>
        </ul>
      </div>
    </main>
  )
}
