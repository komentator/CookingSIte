'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

const DEMO_USER_ID = 1

export default function FridgePage() {
  const [ingredients, setIngredients] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadFridge()
  }, [])

  const loadFridge = async () => {
    try {
      const data = await api.getFridge(DEMO_USER_ID)
      setIngredients(data.ingredients || [])
    } catch (err) {
      console.error(err)
    }
  }

  const handleAdd = async () => {
    if (!input.trim()) return

    setLoading(true)
    try {
      await api.addToFridge(DEMO_USER_ID, [input.trim()])
      setInput('')
      await loadFridge()
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (ingredientId: number) => {
    try {
      await api.removeFromFridge(DEMO_USER_ID, ingredientId)
      await loadFridge()
    } catch (err) {
      console.error(err)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAdd()
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-4xl font-bold text-gray-900 mb-8">🧊 Мой холодильник</h2>

      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Добавьте продукт..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={handleAdd}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition"
          >
            Добавить
          </button>
        </div>

        {ingredients.length > 0 && (
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Продукты:</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {ingredients.map((ing) => (
                <div
                  key={ing.id}
                  className="flex items-center justify-between bg-blue-50 p-3 rounded-lg border border-blue-200"
                >
                  <span className="text-sm font-medium text-gray-900">{ing.name}</span>
                  <button
                    onClick={() => handleRemove(ing.id)}
                    className="text-red-500 hover:text-red-700 font-bold"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {ingredients.length === 0 && (
          <p className="text-gray-500 text-center py-8">Холодильник пуст. Добавьте продукты.</p>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800">
          💡 Совет: Сохраняйте продукты, которые всегда есть дома, чтобы быстро искать рецепты
        </p>
      </div>
    </main>
  )
}
