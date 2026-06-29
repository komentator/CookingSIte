'use client'

import { useState } from 'react'

interface ShoppingItem {
  name: string
  category: string
  checked: boolean
}

export default function ShoppingPage() {
  const [items, setItems] = useState<ShoppingItem[]>([])
  const [input, setInput] = useState('')

  const handleGenerateList = async (ingredients: string[]) => {
    if (ingredients.length === 0) return

    try {
      const response = await fetch('/api/ai/shopping-list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ingredients),
      })

      if (!response.ok) throw new Error('Failed to generate list')

      const data = await response.json()
      setItems(data.items || [])
    } catch (err) {
      console.error(err)
    }
  }

  const handleAddItem = () => {
    if (!input.trim()) return

    setItems([
      ...items,
      {
        name: input.trim(),
        category: 'other',
        checked: false,
      },
    ])
    setInput('')
  }

  const handleToggleItem = (index: number) => {
    const updated = [...items]
    updated[index].checked = !updated[index].checked
    setItems(updated)
  }

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const groupedItems = items.reduce(
    (acc, item) => {
      if (!acc[item.category]) acc[item.category] = []
      acc[item.category].push(item)
      return acc
    },
    {} as Record<string, ShoppingItem[]>
  )

  const categoryEmoji: Record<string, string> = {
    vegetables: '🥬',
    dairy: '🧀',
    meat: '🥩',
    pantry: '🥫',
    spices: '🌶️',
    other: '🛍️',
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-4xl font-bold text-gray-900 mb-8">📝 Список покупок</h2>

      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
            placeholder="Добавить товар вручную..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <button
            onClick={handleAddItem}
            className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition"
          >
            Добавить
          </button>
        </div>

        {items.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            Список покупок пуст. Добавьте товары или используйте результаты поиска рецептов.
          </p>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedItems).map(([category, categoryItems]) => (
              <div key={category}>
                <h3 className="text-lg font-bold text-gray-900 mb-3">
                  {categoryEmoji[category] || '🛍️'} {category}
                </h3>
                <div className="space-y-2">
                  {categoryItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                    >
                      <input
                        type="checkbox"
                        checked={item.checked}
                        onChange={() =>
                          handleToggleItem(
                            items.findIndex((i) => i.name === item.name && i.category === item.category)
                          )
                        }
                        className="w-5 h-5 rounded cursor-pointer"
                      />
                      <span
                        className={`flex-1 ${
                          item.checked
                            ? 'line-through text-gray-500'
                            : 'text-gray-900'
                        }`}
                      >
                        {item.name}
                      </span>
                      <button
                        onClick={() =>
                          handleRemoveItem(
                            items.findIndex((i) => i.name === item.name && i.category === item.category)
                          )
                        }
                        className="text-red-500 hover:text-red-700 font-bold"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="pt-4 border-t mt-6">
              <p className="text-sm text-gray-600">
                Куплено: {items.filter((i) => i.checked).length} из {items.length}
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{
                    width: `${Math.round((items.filter((i) => i.checked).length / items.length) * 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <p className="text-orange-800">
          💡 Совет: Скопируйте недостающие ингредиенты из результатов поиска рецептов, чтобы быстро создать список покупок.
        </p>
      </div>
    </main>
  )
}
