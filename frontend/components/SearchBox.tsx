'use client'

import { useState } from 'react'

interface SearchBoxProps {
  onSearch: (ingredients: string[]) => void
  loading: boolean
}

export function SearchBox({ onSearch, loading }: SearchBoxProps) {
  const [input, setInput] = useState('')
  const [ingredients, setIngredients] = useState<string[]>([])

  const handleAddIngredient = () => {
    if (input.trim()) {
      const normalized = input.trim().toLowerCase()
      if (!ingredients.includes(normalized)) {
        setIngredients([...ingredients, normalized])
      }
      setInput('')
    }
  }

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddIngredient()
    }
  }

  const handleSearch = () => {
    if (ingredients.length > 0) {
      onSearch(ingredients)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Например: курица, картошка, лук..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          disabled={loading}
        />
        <button
          onClick={handleAddIngredient}
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-400 transition"
        >
          Добавить
        </button>
      </div>

      {ingredients.length > 0 && (
        <div>
          <div className="flex flex-wrap gap-2 mb-4">
            {ingredients.map((ing, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 bg-orange-100 text-orange-800 px-4 py-2 rounded-full"
              >
                <span>{ing}</span>
                <button
                  onClick={() => handleRemoveIngredient(idx)}
                  disabled={loading}
                  className="text-orange-600 hover:text-orange-900 font-bold"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full px-6 py-3 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 disabled:bg-gray-400 transition text-lg"
          >
            {loading ? 'Ищу рецепты...' : '🔍 Найти рецепты'}
          </button>
        </div>
      )}

      <div className="text-sm text-gray-600 mt-2">
        Добавлено продуктов: {ingredients.length}
      </div>
    </div>
  )
}
