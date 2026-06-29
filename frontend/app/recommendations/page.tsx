'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Recipe {
  id: number
  title: string
  cooking_time?: number
  calories?: number
  servings?: number
  match_percent?: number
  type: string
}

interface Stats {
  total_recipes: number
  total_ingredients: number
  avg_cooking_time_minutes: number
  avg_calories: number
  by_cooking_time: {
    quick_30min: number
    medium_30_60min: number
    long_over_60min: number
  }
}

const DEMO_USER_ID = 1

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<string>('personalized')

  useEffect(() => {
    loadRecommendations()
    loadStats()
  }, [])

  const loadRecommendations = async () => {
    try {
      const response = await fetch(
        `/api/recommendations/for-user/${DEMO_USER_ID}`
      )
      if (response.ok) {
        const data = await response.json()
        setRecommendations(data.recommendations)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/recommendations/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const RecipeCard = ({ recipe }: { recipe: Recipe }) => (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition">
      <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">{recipe.title}</h3>

      <div className="flex flex-wrap gap-2 text-sm text-gray-600 mb-3">
        {recipe.cooking_time && (
          <span>⏱️ {recipe.cooking_time} мин</span>
        )}
        {recipe.calories && (
          <span>🔥 {recipe.calories} ккал</span>
        )}
        {recipe.servings && (
          <span>🍽️ {recipe.servings} порций</span>
        )}
        {recipe.match_percent && (
          <span className="font-semibold text-orange-600">
            ✓ {recipe.match_percent}%
          </span>
        )}
      </div>

      <Link
        href={`/recipes#recipe-${recipe.id}`}
        className="inline-block px-3 py-1 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 transition"
      >
        Подробнее
      </Link>
    </div>
  )

  if (loading) {
    return (
      <main className="max-w-7xl mx-auto px-4 py-12">
        <p className="text-center text-gray-500">Загружаю рекомендации...</p>
      </main>
    )
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-12">⭐ Рекомендации</h1>

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <p className="text-sm text-blue-600 font-semibold">Всего рецептов</p>
            <p className="text-3xl font-bold text-blue-900">
              {stats.total_recipes}
            </p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <p className="text-sm text-green-600 font-semibold">Ингредиентов</p>
            <p className="text-3xl font-bold text-green-900">
              {stats.total_ingredients}
            </p>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <p className="text-sm text-orange-600 font-semibold">
              Ср. время (мин)
            </p>
            <p className="text-3xl font-bold text-orange-900">
              {Math.round(stats.avg_cooking_time_minutes)}
            </p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <p className="text-sm text-purple-600 font-semibold">Ср. калории</p>
            <p className="text-3xl font-bold text-purple-900">
              {Math.round(stats.avg_calories)}
            </p>
          </div>
        </div>
      )}

      {/* Разбор по времени */}
      {stats && (
        <div className="mb-12 bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Рецепты по времени приготовления
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <p className="text-sm text-green-600 font-semibold">Быстро</p>
              <p className="text-3xl font-bold text-green-900">
                {stats.by_cooking_time.quick_30min}
              </p>
              <p className="text-xs text-gray-600 mt-1">до 30 минут</p>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg text-center">
              <p className="text-sm text-yellow-600 font-semibold">Среднее</p>
              <p className="text-3xl font-bold text-yellow-900">
                {stats.by_cooking_time.medium_30_60min}
              </p>
              <p className="text-xs text-gray-600 mt-1">30-60 минут</p>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg text-center">
              <p className="text-sm text-orange-600 font-semibold">Долгое</p>
              <p className="text-3xl font-bold text-orange-900">
                {stats.by_cooking_time.long_over_60min}
              </p>
              <p className="text-xs text-gray-600 mt-1">более 60 минут</p>
            </div>
          </div>
        </div>
      )}

      {/* Вкладки с рекомендациями */}
      {recommendations && (
        <div>
          <div className="flex gap-2 mb-6 flex-wrap">
            {Object.keys(recommendations).map((key) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`px-4 py-2 rounded-lg font-semibold transition ${
                  activeTab === key
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {key === 'personalized' && '👤 Для вас'}
                {key === 'quick' && '⚡ Быстрые'}
                {key === 'protein' && '💪 Белковые'}
              </button>
            ))}
          </div>

          {recommendations[activeTab] && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                {activeTab === 'personalized' && '👤 Рекомендовано для вас'}
                {activeTab === 'quick' && '⚡ Быстрые рецепты'}
                {activeTab === 'protein' && '💪 Рецепты с белком'}
              </h2>

              {recommendations[activeTab].length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  Рецептов не найдено
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations[activeTab].map((recipe: Recipe) => (
                    <RecipeCard key={recipe.id} recipe={recipe} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="mt-12 bg-orange-50 border border-orange-200 rounded-lg p-6">
        <h3 className="font-bold text-gray-900 mb-2">💡 Совет</h3>
        <p className="text-gray-700">
          Добавьте продукты в{' '}
          <Link href="/fridge" className="text-orange-600 hover:underline font-semibold">
            холодильник
          </Link>
          , чтобы получить персонализированные рекомендации!
        </p>
      </div>
    </main>
  )
}
