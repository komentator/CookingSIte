'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface SearchRecord {
  id: number
  query: string
  ingredients: string[]
  results_count: number
  created_at: string
}

const DEMO_USER_ID = 1

export default function HistoryPage() {
  const [history, setHistory] = useState<SearchRecord[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response = await fetch(
        `/api/user/${DEMO_USER_ID}/search-history?limit=50`
      )

      if (response.ok) {
        const data = await response.json()
        setHistory(data.searches)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (historyId: number) => {
    try {
      const response = await fetch(
        `/api/user/${DEMO_USER_ID}/search-history/${historyId}`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        setHistory(history.filter(h => h.id !== historyId))
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleClearAll = async () => {
    if (!confirm('Очистить всю историю поиска?')) return

    try {
      const response = await fetch(
        `/api/user/${DEMO_USER_ID}/search-history`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        setHistory([])
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleSearch = (ingredients: string[]) => {
    // Переход на страницу поиска с выбранными ингредиентами
    const params = new URLSearchParams()
    ingredients.forEach(ing => params.append('ing', ing))
    window.location.href = `/search?${params.toString()}`
  }

  if (loading) {
    return (
      <main className="max-w-7xl mx-auto px-4 py-12">
        <p className="text-center text-gray-500">Загружаю историю...</p>
      </main>
    )
  }

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900">📜 История поиска</h1>
        {history.length > 0 && (
          <button
            onClick={handleClearAll}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-semibold"
          >
            Очистить всё
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="bg-gray-50 border-2 border-gray-300 rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg mb-6">
            История поиска пуста
          </p>
          <Link
            href="/search"
            className="inline-block px-6 py-3 bg-orange-500 text-white font-bold rounded-lg hover:bg-orange-600 transition"
          >
            Начать поиск →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((record) => (
            <div
              key={record.id}
              className="bg-white rounded-lg shadow p-4 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 text-lg mb-2">
                    {record.query}
                  </h3>

                  {record.ingredients.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-3">
                      {record.ingredients.map((ing, idx) => (
                        <span
                          key={idx}
                          className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded"
                        >
                          {ing}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>📊 Найдено: {record.results_count} рецептов</span>
                    <span>🕐 {new Date(record.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleSearch(record.ingredients)}
                  className="flex-1 px-3 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 transition font-semibold"
                >
                  Повторить поиск
                </button>
                <button
                  onClick={() => handleDelete(record.id)}
                  className="px-3 py-2 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 transition"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-12 bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
        <h2 className="font-bold text-gray-900 mb-2">💡 Совет</h2>
        <p className="text-gray-700">
          История поиска помогает быстро вернуться к интересующим вас рецептам. Просто нажмите "Повторить поиск" для любого поиска из истории.
        </p>
      </div>
    </main>
  )
}
