'use client'

import { useState } from 'react'

interface AdvancedSearchProps {
  onSearch: (filters: AdvancedFilters) => void
  loading: boolean
}

export interface AdvancedFilters {
  title?: string
  minCookingTime?: number
  maxCookingTime?: number
  minCalories?: number
  maxCalories?: number
  minRating?: number
  servings?: number
  vegan?: boolean
  vegetarian?: boolean
  glutenFree?: boolean
}

export function AdvancedSearch({ onSearch, loading }: AdvancedSearchProps) {
  const [filters, setFilters] = useState<AdvancedFilters>({})
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleInputChange = (key: keyof AdvancedFilters, value: any) => {
    setFilters({
      ...filters,
      [key]: value === '' ? undefined : value
    })
  }

  const handleSearch = () => {
    onSearch(filters)
  }

  const handleReset = () => {
    setFilters({})
  }

  const hasFilters = Object.values(filters).some(v => v !== undefined && v !== '')

  return (
    <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6 border-2 border-indigo-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-gray-900">🔎 Расширенный поиск</h3>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-indigo-600 hover:text-indigo-700 font-semibold text-sm"
        >
          {showAdvanced ? '▼' : '▶'} {showAdvanced ? 'Скрыть' : 'Показать'}
        </button>
      </div>

      {showAdvanced && (
        <div className="space-y-4 mb-6">
          {/* Название рецепта */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              📝 Название рецепта
            </label>
            <input
              type="text"
              value={filters.title || ''}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="Например: борщ, паста, салат..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={loading}
            />
          </div>

          {/* Время приготовления */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                ⏱️ Мин время (мин)
              </label>
              <input
                type="number"
                value={filters.minCookingTime || ''}
                onChange={(e) =>
                  handleInputChange('minCookingTime', e.target.value ? parseInt(e.target.value) : '')
                }
                min="0"
                placeholder="Минимум"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Макс время (мин)
              </label>
              <input
                type="number"
                value={filters.maxCookingTime || ''}
                onChange={(e) =>
                  handleInputChange('maxCookingTime', e.target.value ? parseInt(e.target.value) : '')
                }
                min="0"
                placeholder="Максимум"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
          </div>

          {/* Калории */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🔥 Мин ккал
              </label>
              <input
                type="number"
                value={filters.minCalories || ''}
                onChange={(e) =>
                  handleInputChange('minCalories', e.target.value ? parseInt(e.target.value) : '')
                }
                min="0"
                placeholder="Минимум"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Макс ккал
              </label>
              <input
                type="number"
                value={filters.maxCalories || ''}
                onChange={(e) =>
                  handleInputChange('maxCalories', e.target.value ? parseInt(e.target.value) : '')
                }
                min="0"
                placeholder="Максимум"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
          </div>

          {/* Рейтинг и порции */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                ⭐ Мин рейтинг
              </label>
              <input
                type="number"
                value={filters.minRating || ''}
                onChange={(e) =>
                  handleInputChange('minRating', e.target.value ? parseFloat(e.target.value) : '')
                }
                min="0"
                max="5"
                step="0.1"
                placeholder="0-5"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🍽️ Порции
              </label>
              <input
                type="number"
                value={filters.servings || ''}
                onChange={(e) =>
                  handleInputChange('servings', e.target.value ? parseInt(e.target.value) : '')
                }
                min="1"
                placeholder="Кол-во"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={loading}
              />
            </div>
          </div>

          {/* Диетические флаги */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              🌱 Диетические ограничения
            </label>
            <div className="flex flex-wrap gap-3">
              {[
                { key: 'vegan', label: '🌱 Веганское' },
                { key: 'vegetarian', label: '🥗 Вегетарианское' },
                { key: 'glutenFree', label: '🌾 Без глютена' }
              ].map((option) => (
                <label key={option.key} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={filters[option.key as keyof AdvancedFilters] === true}
                    onChange={(e) =>
                      handleInputChange(option.key as keyof AdvancedFilters, e.target.checked)
                    }
                    disabled={loading}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm text-gray-700">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={handleSearch}
          disabled={loading}
          className="flex-1 px-4 py-3 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 transition"
        >
          {loading ? 'Поиск...' : '🔍 Расширенный поиск'}
        </button>
        {hasFilters && (
          <button
            onClick={handleReset}
            disabled={loading}
            className="px-4 py-3 bg-gray-300 text-gray-700 font-bold rounded-lg hover:bg-gray-400 disabled:bg-gray-200 transition"
          >
            Сбросить
          </button>
        )}
      </div>

      {hasFilters && (
        <p className="text-xs text-gray-600 mt-3">
          ✓ Активных фильтров: {Object.values(filters).filter(v => v !== undefined && v !== '').length}
        </p>
      )}
    </div>
  )
}
