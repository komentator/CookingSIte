'use client'

import { useState } from 'react'

interface DietaryFiltersProps {
  onApply: (filters: DietaryFilterState) => void
  loading: boolean
}

interface DietaryFilterState {
  vegan: boolean
  vegetarian: boolean
  glutenFree: boolean
  dairyFree: boolean
  nutFree: boolean
  minRating: number
}

export function DietaryFilters({ onApply, loading }: DietaryFiltersProps) {
  const [filters, setFilters] = useState<DietaryFilterState>({
    vegan: false,
    vegetarian: false,
    glutenFree: false,
    dairyFree: false,
    nutFree: false,
    minRating: 0,
  })

  const handleToggle = (key: keyof DietaryFilterState, value: boolean | number) => {
    setFilters({ ...filters, [key]: value })
  }

  const handleApply = () => {
    onApply(filters)
  }

  const handleReset = () => {
    setFilters({
      vegan: false,
      vegetarian: false,
      glutenFree: false,
      dairyFree: false,
      nutFree: false,
      minRating: 0,
    })
  }

  const dietaryOptions = [
    { key: 'vegan', label: '🌱 Веганское', emoji: '🌱' },
    { key: 'vegetarian', label: '🥗 Вегетарианское', emoji: '🥗' },
    { key: 'glutenFree', label: '🌾 Без глютена', emoji: '🌾' },
    { key: 'dairyFree', label: '🥛 Без лактозы', emoji: '🥛' },
    { key: 'nutFree', label: '🥜 Без орехов', emoji: '🥜' },
  ]

  const activeCount = Object.values(filters).filter(v => v === true || (typeof v === 'number' && v > 0)).length

  return (
    <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border-2 border-green-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-gray-900">🍽️ Диетические ограничения</h3>
        {activeCount > 0 && (
          <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
            Активно: {activeCount}
          </span>
        )}
      </div>

      <div className="space-y-3 mb-6">
        {dietaryOptions.map((option) => (
          <label
            key={option.key}
            className="flex items-center gap-3 p-3 bg-white rounded-lg hover:bg-gray-50 cursor-pointer transition"
          >
            <input
              type="checkbox"
              checked={filters[option.key as keyof DietaryFilterState] === true}
              onChange={(e) =>
                handleToggle(option.key as keyof DietaryFilterState, e.target.checked)
              }
              className="w-5 h-5 rounded cursor-pointer"
              disabled={loading}
            />
            <span className="text-gray-900 font-medium">{option.label}</span>
          </label>
        ))}
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          ⭐ Минимальный рейтинг
        </label>
        <div className="flex gap-2">
          {[0, 3, 4, 4.5].map((rating) => (
            <button
              key={rating}
              onClick={() => handleToggle('minRating', rating)}
              className={`px-3 py-2 rounded-lg transition ${
                filters.minRating === rating
                  ? 'bg-orange-500 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:border-orange-500'
              }`}
              disabled={loading}
            >
              {rating === 0 ? 'Любой' : `${rating}+`}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleApply}
          disabled={loading}
          className="flex-1 px-4 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition"
        >
          {loading ? 'Поиск...' : '🔍 Применить фильтры'}
        </button>
        {activeCount > 0 && (
          <button
            onClick={handleReset}
            disabled={loading}
            className="px-4 py-3 bg-gray-300 text-gray-700 font-bold rounded-lg hover:bg-gray-400 disabled:bg-gray-200 transition"
          >
            Сбросить
          </button>
        )}
      </div>
    </div>
  )
}
