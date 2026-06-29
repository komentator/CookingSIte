'use client'

import { useState } from 'react'
import { SearchBox } from '@/components/SearchBox'
import { RecipeResults } from '@/components/RecipeResults'
import { SmartSearch } from '@/components/SmartSearch'

interface FilterOptions {
  cookingTimeMax?: number
  servings?: number
  minCalories?: number
  maxCalories?: number
  fuzzy?: boolean
  fuzzyThreshold?: number
}

export default function SearchPage() {
  const [results, setResults] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [useSmartSearch, setUseSmartSearch] = useState(false)

  const [filters, setFilters] = useState<FilterOptions>({
    fuzzy: true,
    fuzzyThreshold: 0.7,
  })

  const handleSearch = async (ingredients: string[]) => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()

      if (filters.cookingTimeMax) {
        params.append('cooking_time_max', filters.cookingTimeMax.toString())
      }
      if (filters.fuzzy !== undefined) {
        params.append('fuzzy', filters.fuzzy.toString())
      }
      if (filters.fuzzyThreshold) {
        params.append('fuzzy_threshold', filters.fuzzyThreshold.toString())
      }

      const response = await fetch(
        `/api/search/by-ingredients?${params.toString()}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ingredients,
            cooking_time_max: filters.cookingTimeMax,
            servings: filters.servings,
          }),
        }
      )

      if (!response.ok) throw new Error('Search failed')

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError('Ошибка при поиске')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSmartResults = (results: any) => {
    setResults(results)
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h2 className="text-5xl font-bold text-gray-900 mb-4">
          Что можно приготовить?
        </h2>
        <p className="text-xl text-gray-600">
          Введите продукты, которые есть дома, и найдите идеальный рецепт
        </p>
      </div>

      {/* Режим поиска */}
      <div className="mb-8 flex gap-4">
        <button
          onClick={() => setUseSmartSearch(false)}
          className={`flex-1 py-3 rounded-lg font-semibold transition ${
            !useSmartSearch
              ? 'bg-orange-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📋 Список продуктов
        </button>
        <button
          onClick={() => setUseSmartSearch(true)}
          className={`flex-1 py-3 rounded-lg font-semibold transition ${
            useSmartSearch
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          🤖 Умный поиск
        </button>
      </div>

      {/* Поиск */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
        {!useSmartSearch ? (
          <SearchBox onSearch={handleSearch} loading={loading} />
        ) : (
          <SmartSearch onResults={handleSmartResults} loading={loading} />
        )}

        {/* Фильтры */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="mt-6 text-orange-600 hover:text-orange-700 font-semibold text-sm"
        >
          {showFilters ? '▼' : '▶'} Дополнительные фильтры
        </button>

        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                ⏱️ Время приготовления (мин)
              </label>
              <input
                type="number"
                value={filters.cookingTimeMax || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    cookingTimeMax: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
                placeholder="Макс минут"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🍽️ Количество порций
              </label>
              <input
                type="number"
                value={filters.servings || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    servings: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
                placeholder="Порции"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🔍 Чувствительность поиска
              </label>
              <select
                value={filters.fuzzyThreshold || 0.7}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    fuzzyThreshold: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                <option value={0.5}>Низкая (50%)</option>
                <option value={0.7}>Средняя (70%)</option>
                <option value={0.9}>Высокая (90%)</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {results && <RecipeResults results={results} />}

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
