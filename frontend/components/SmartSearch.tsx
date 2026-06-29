'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

interface SmartSearchProps {
  onResults: (results: any) => void
  loading: boolean
}

export function SmartSearch({ onResults, loading }: SmartSearchProps) {
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSmartSearch = async () => {
    if (!query.trim()) return

    try {
      setError(null)
      const response = await fetch('/api/ai/smart-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) throw new Error('Smart search failed')

      const data = await response.json()
      onResults(data.results)
      setQuery('')
    } catch (err) {
      setError('Ошибка при умном поиске')
      console.error(err)
    }
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-blue-200">
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          🤖 Умный поиск (естественный язык)
        </label>
        <p className="text-sm text-gray-600 mb-3">
          Пример: "есть курица, картошка и сыр, готовить не больше 30 минут"
        </p>
      </div>

      <div className="flex gap-2">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Опишите, что вы хотите приготовить..."
          className="flex-1 px-4 py-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={3}
          disabled={loading}
        />
      </div>

      <button
        onClick={handleSmartSearch}
        disabled={loading || !query.trim()}
        className="mt-3 w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
      >
        {loading ? 'Ищу...' : '🔍 Умный поиск'}
      </button>

      {error && (
        <div className="mt-3 text-red-600 text-sm">{error}</div>
      )}
    </div>
  )
}
