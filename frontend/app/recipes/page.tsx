'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Category {
  name: string
  count: number
}

interface Recipe {
  id: number
  title: string
  description?: string
  cooking_time?: number
  servings?: number
  calories?: number
  category?: string
  ingredients?: any[]
}

const SORTS: { value: string; label: string }[] = [
  { value: 'title', label: 'По названию' },
  { value: 'cooking_time', label: 'По времени' },
  { value: 'calories', label: 'По калориям' },
  { value: 'category', label: 'По категории' },
]

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [sort, setSort] = useState('title')
  const [groupByCategory, setGroupByCategory] = useState(true)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .getRecipes({ category: selectedCategory || undefined, sort })
      .then(setRecipes)
      .catch((e) => {
        console.error(e)
        setError('Не удалось загрузить рецепты. Проверьте, что backend API запущен на http://localhost:8000.')
      })
      .finally(() => setLoading(false))
  }, [selectedCategory, sort])

  const grouped = useMemo(() => {
    if (!groupByCategory || selectedCategory) return null
    const map = new Map<string, Recipe[]>()
    for (const r of recipes) {
      const cat = r.category || 'Без категории'
      if (!map.has(cat)) map.set(cat, [])
      map.get(cat)!.push(r)
    }
    return Array.from(map.entries()).sort((a, b) => b[1].length - a[1].length)
  }, [recipes, groupByCategory, selectedCategory])

  const totalForChip = (catName: string) =>
    categories.find((c) => c.name === catName)?.count ?? 0

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-4xl font-bold text-gray-900 mb-6">📖 Все рецепты</h2>

      <div className="bg-white rounded-2xl shadow p-6 mb-8">
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              selectedCategory === null
                ? 'bg-orange-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Все ({categories.reduce((s, c) => s + c.count, 0)})
          </button>
          {categories.map((c) => (
            <button
              key={c.name}
              onClick={() =>
                setSelectedCategory(c.name === selectedCategory ? null : c.name)
              }
              className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                selectedCategory === c.name
                  ? 'bg-orange-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {c.name} ({c.count})
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm">
          <label className="text-gray-700">
            Сортировка:
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="ml-2 border border-gray-300 rounded px-2 py-1"
            >
              {SORTS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2 text-gray-700">
            <input
              type="checkbox"
              checked={groupByCategory}
              onChange={(e) => setGroupByCategory(e.target.checked)}
            />
            Группировать по категориям
          </label>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Загружаю рецепты...</div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800">{error}</p>
        </div>
      ) : recipes.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <p className="text-yellow-800">Нет рецептов в выбранной категории.</p>
        </div>
      ) : grouped ? (
        grouped.map(([cat, items]) => (
          <section key={cat} className="mb-10">
            <h3 className="text-2xl font-bold text-gray-900 mb-4 border-b border-gray-200 pb-2">
              {cat}{' '}
              <span className="text-base font-normal text-gray-500">
                ({items.length})
              </span>
            </h3>
            <RecipeGrid recipes={items} />
          </section>
        ))
      ) : (
        <RecipeGrid recipes={recipes} />
      )}
    </main>
  )
}

function RecipeGrid({ recipes }: { recipes: Recipe[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {recipes.map((recipe) => (
        <Link
          key={recipe.id}
          href={`/recipes/${recipe.id}`}
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl hover:-translate-y-1 transition block"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-2">{recipe.title}</h3>

          {recipe.category && (
            <span className="inline-block text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded mb-3">
              {recipe.category}
            </span>
          )}

          {recipe.description && (
            <p className="text-gray-600 text-sm mb-4 line-clamp-2">{recipe.description}</p>
          )}

          <div className="flex gap-4 text-sm text-gray-600 mb-4 flex-wrap">
            {recipe.cooking_time && <span>⏱️ {recipe.cooking_time} мин</span>}
            {recipe.servings && <span>🍽️ {recipe.servings} порций</span>}
            {recipe.calories && <span>🔥 {recipe.calories} ккал</span>}
          </div>

          {recipe.ingredients && recipe.ingredients.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-2">
                Ингредиенты: {recipe.ingredients.length}
              </p>
              <div className="flex flex-wrap gap-2">
                {recipe.ingredients.slice(0, 3).map((ing: any, idx: number) => (
                  <span
                    key={idx}
                    className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded"
                  >
                    {ing.ingredient?.name || 'ингредиент'}
                  </span>
                ))}
                {recipe.ingredients.length > 3 && (
                  <span className="text-xs text-gray-600">
                    +{recipe.ingredients.length - 3}
                  </span>
                )}
              </div>
            </div>
          )}

          <span className="inline-block px-4 py-2 bg-orange-500 text-white text-sm rounded-lg">
            Открыть рецепт →
          </span>
        </Link>
      ))}
    </div>
  )
}
