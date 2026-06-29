'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Ingredient {
  ingredient?: { name: string }
  quantity?: string | null
  unit?: string | null
  is_required?: boolean
}

interface Instruction {
  step_number: number
  description: string
}

interface Recipe {
  id: number
  title: string
  description?: string
  source?: string
  url?: string
  cooking_time?: number
  servings?: number
  calories?: number
  rating?: number
  reviews_count?: number
  is_vegan?: boolean
  is_vegetarian?: boolean
  is_gluten_free?: boolean
  is_dairy_free?: boolean
  is_nut_free?: boolean
  ingredients?: Ingredient[]
  instructions?: Instruction[]
}

export default function RecipeDetailPage({ params }: { params: { id: string } }) {
  const [recipe, setRecipe] = useState<Recipe | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getRecipe(Number(params.id))
        setRecipe(data)
      } catch (e) {
        console.error(e)
        setError('Не удалось загрузить рецепт.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [params.id])

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p className="text-gray-500 text-center">Загружаю рецепт...</p>
      </main>
    )
  }

  if (error || !recipe) {
    return (
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800">{error || 'Рецепт не найден'}</p>
        </div>
        <Link href="/recipes" className="mt-4 inline-block text-orange-600 hover:underline">
          ← Все рецепты
        </Link>
      </main>
    )
  }

  const diet: string[] = []
  if (recipe.is_vegan) diet.push('Веганское')
  else if (recipe.is_vegetarian) diet.push('Вегетарианское')
  if (recipe.is_gluten_free) diet.push('Без глютена')
  if (recipe.is_dairy_free) diet.push('Без лактозы')
  if (recipe.is_nut_free) diet.push('Без орехов')

  const sortedSteps = (recipe.instructions || [])
    .slice()
    .sort((a, b) => (a.step_number || 0) - (b.step_number || 0))

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link href="/recipes" className="text-orange-600 hover:underline mb-4 inline-block">
        ← Все рецепты
      </Link>

      <div className="bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">{recipe.title}</h1>

        {recipe.description && (
          <p className="text-gray-600 mb-6">{recipe.description}</p>
        )}

        <div className="flex gap-6 text-gray-700 mb-6 flex-wrap">
          {recipe.cooking_time && <span>⏱️ {recipe.cooking_time} мин</span>}
          {recipe.servings && <span>🍽️ {recipe.servings} порций</span>}
          {recipe.calories && <span>🔥 {recipe.calories} ккал</span>}
          {recipe.source && (
            <span className="text-sm text-gray-500">Источник: {recipe.source}</span>
          )}
        </div>

        {diet.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {diet.map((d) => (
              <span
                key={d}
                className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded"
              >
                {d}
              </span>
            ))}
          </div>
        )}

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ингредиенты</h2>
          {recipe.ingredients && recipe.ingredients.length > 0 ? (
            <ul className="space-y-2">
              {recipe.ingredients.map((ing, idx) => (
                <li
                  key={idx}
                  className="flex justify-between border-b border-gray-100 pb-2"
                >
                  <span className="text-gray-800">
                    {ing.ingredient?.name || 'ингредиент'}
                  </span>
                  <span className="text-gray-600">
                    {[ing.quantity, ing.unit].filter(Boolean).join(' ')}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">Ингредиенты не указаны</p>
          )}
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Приготовление</h2>
          {sortedSteps.length > 0 ? (
            <ol className="space-y-4">
              {sortedSteps.map((step) => (
                <li key={step.step_number} className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold">
                    {step.step_number}
                  </span>
                  <p className="text-gray-700 flex-1">{step.description}</p>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-gray-500">Шаги не указаны</p>
          )}
        </section>

        {recipe.url && (
          <a
            href={recipe.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Оригинал на сайте источника ↗
          </a>
        )}
      </div>
    </main>
  )
}
