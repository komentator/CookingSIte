'use client'

import { useState, useEffect } from 'react'
import { DietaryFilters } from '@/components/DietaryFilters'

interface Recipe {
  id: number
  title: string
  cooking_time?: number
  calories?: number
  rating?: number
  reviews_count?: number
  dietary_tags?: {
    vegan: boolean
    vegetarian: boolean
    gluten_free: boolean
    dairy_free: boolean
    nut_free: boolean
  }
}

interface DietaryFilterState {
  vegan: boolean
  vegetarian: boolean
  glutenFree: boolean
  dairyFree: boolean
  nutFree: boolean
  minRating: number
}

export default function DietaryPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(false)
  const [activeFilters, setActiveFilters] = useState<DietaryFilterState | null>(null)

  const handleApplyFilters = async (filters: DietaryFilterState) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('vegan', filters.vegan.toString())
      params.append('vegetarian', filters.vegetarian.toString())
      params.append('gluten_free', filters.glutenFree.toString())
      params.append('dairy_free', filters.dairyFree.toString())
      params.append('nut_free', filters.nutFree.toString())
      params.append('min_rating', filters.minRating.toString())
      params.append('limit', '20')

      const response = await fetch(`/api/recipes/filter/dietary?${params.toString()}`)

      if (response.ok) {
        const data = await response.json()
        setRecipes(data.recipes)
        setActiveFilters(filters)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getDietaryBadges = (recipe: Recipe) => {
    if (!recipe.dietary_tags) return []

    const badges = []
    if (recipe.dietary_tags.vegan) badges.push({ text: 'Веган', color: 'bg-green-100 text-green-800' })
    if (recipe.dietary_tags.vegetarian) badges.push({ text: 'Вегетарианское', color: 'bg-green-100 text-green-800' })
    if (recipe.dietary_tags.gluten_free) badges.push({ text: 'Без глютена', color: 'bg-yellow-100 text-yellow-800' })
    if (recipe.dietary_tags.dairy_free) badges.push({ text: 'Без лактозы', color: 'bg-blue-100 text-blue-800' })
    if (recipe.dietary_tags.nut_free) badges.push({ text: 'Без орехов', color: 'bg-red-100 text-red-800' })
    return badges
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-12">
        🍽️ Диетические рецепты
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
        <div>
          <DietaryFilters onApply={handleApplyFilters} loading={loading} />
        </div>

        <div className="lg:col-span-3">
          {!activeFilters ? (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-8 text-center">
              <p className="text-blue-800 text-lg font-semibold">
                👈 Выберите диетические ограничения слева
              </p>
            </div>
          ) : recipes.length === 0 ? (
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-8 text-center">
              <p className="text-yellow-800 text-lg font-semibold">
                😞 Рецепты с такими ограничениями не найдены
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Найдено рецептов: {recipes.length}
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recipes.map((recipe) => (
                  <div
                    key={recipe.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
                  >
                    <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                      {recipe.title}
                    </h3>

                    {/* Диетические метки */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {getDietaryBadges(recipe).map((badge, idx) => (
                        <span
                          key={idx}
                          className={`text-xs font-semibold px-2 py-1 rounded ${badge.color}`}
                        >
                          {badge.text}
                        </span>
                      ))}
                    </div>

                    {/* Информация */}
                    <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-4">
                      {recipe.cooking_time && (
                        <span>⏱️ {recipe.cooking_time} мин</span>
                      )}
                      {recipe.calories && (
                        <span>🔥 {recipe.calories} ккал</span>
                      )}
                      {recipe.rating && (
                        <span className="text-orange-600 font-semibold">
                          ⭐ {recipe.rating.toFixed(1)} ({recipe.reviews_count})
                        </span>
                      )}
                    </div>

                    <a
                      href={`/recipes#recipe-${recipe.id}`}
                      className="inline-block px-3 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 transition font-semibold"
                    >
                      Подробнее →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
