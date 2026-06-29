'use client'

import { useState } from 'react'
import { SearchBox } from '@/components/SearchBox'
import { RecipeResults } from '@/components/RecipeResults'
import { api } from '@/lib/api'

interface Recipe {
  id: number
  title: string
  description?: string
  cooking_time?: number
  servings?: number
  calories?: number
  url?: string
  source?: string
}

interface SearchResult {
  recipe: Recipe
  match_percent: number
  matched_count: number
  missing_count: number
  missing_ingredients: string[]
}

interface SearchResponse {
  can_cook_now: SearchResult[]
  need_buy_1_2: SearchResult[]
  need_many: SearchResult[]
  total: number
}

export default function Home() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (ingredients: string[]) => {
    setLoading(true)
    setError(null)

    try {
      const response = await api.searchByIngredients(ingredients)
      setResults(response)
    } catch (err) {
      setError('Ошибка при поиске. Попробуйте позже.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h2 className="text-5xl font-bold text-gray-900 mb-4">
          Что можно приготовить?
        </h2>
        <p className="text-xl text-gray-600">
          Введите продукты, которые есть дома, и мы найдём рецепты
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-xl p-8 mb-12">
        <SearchBox onSearch={handleSearch} loading={loading} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {results && (
        <RecipeResults results={results} />
      )}

      {!results && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            Начните с введения ингредиентов, чтобы найти рецепты
          </p>
        </div>
      )}
    </main>
  )
}
