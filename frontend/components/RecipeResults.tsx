'use client'

interface Recipe {
  id: number
  title: string
  description?: string
  cooking_time?: number
  servings?: number
  calories?: number
  url?: string
  source?: string
}

interface SearchResult {
  recipe: Recipe
  match_percent: number
  matched_count: number
  missing_count: number
  missing_ingredients: string[]
}

interface RecipeResultsProps {
  results: {
    can_cook_now: SearchResult[]
    need_buy_1_2: SearchResult[]
    need_many: SearchResult[]
    total: number
  }
}

function RecipeCard({ result }: { result: SearchResult }) {
  const { recipe, match_percent, missing_ingredients } = result

  const getMatchColor = (percent: number) => {
    if (percent === 100) return 'bg-green-50 border-green-200'
    if (percent >= 50) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  const getMatchBadge = (percent: number) => {
    if (percent === 100) return '✅ Готово'
    if (percent >= 50) return '🟡 Докупить'
    return '🔴 Много не хватает'
  }

  return (
    <div className={`border-2 rounded-lg p-6 ${getMatchColor(match_percent)}`}>
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xl font-bold text-gray-900">{recipe.title}</h3>
        <span className="text-sm font-bold bg-white px-3 py-1 rounded-full">
          {Math.round(match_percent)}%
        </span>
      </div>

      {recipe.description && (
        <p className="text-gray-600 mb-4 line-clamp-2">{recipe.description}</p>
      )}

      <div className="flex gap-4 mb-4 flex-wrap">
        {recipe.cooking_time && (
          <span className="text-sm text-gray-600">⏱️ {recipe.cooking_time} мин</span>
        )}
        {recipe.servings && (
          <span className="text-sm text-gray-600">🍽️ {recipe.servings} порций</span>
        )}
        {recipe.calories && (
          <span className="text-sm text-gray-600">🔥 {recipe.calories} ккал</span>
        )}
        {recipe.source && (
          <span className="text-sm text-gray-600">📌 {recipe.source}</span>
        )}
      </div>

      <div className="mb-4">
        <span className="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-white">
          {getMatchBadge(match_percent)}
        </span>
      </div>

      {missing_ingredients.length > 0 && (
        <div className="bg-white rounded p-3 mb-4">
          <p className="text-sm font-semibold text-gray-700 mb-2">
            Не хватает: {missing_ingredients.length}
          </p>
          <div className="flex flex-wrap gap-2">
            {missing_ingredients.slice(0, 3).map((ing, idx) => (
              <span key={idx} className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                {ing}
              </span>
            ))}
            {missing_ingredients.length > 3 && (
              <span className="text-xs text-gray-600">
                и ещё {missing_ingredients.length - 3}
              </span>
            )}
          </div>
        </div>
      )}

      {recipe.url && (
        <a
          href={recipe.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition text-sm font-semibold"
        >
          Посмотреть рецепт →
        </a>
      )}
    </div>
  )
}

export function RecipeResults({ results }: RecipeResultsProps) {
  const hasAnyResults =
    results.can_cook_now.length > 0 ||
    results.need_buy_1_2.length > 0 ||
    results.need_many.length > 0

  if (!hasAnyResults) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Рецепты не найдены. Попробуйте другие продукты.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {results.can_cook_now.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-green-700 mb-4">
            ✅ Можно приготовить сейчас ({results.can_cook_now.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.can_cook_now.map((result) => (
              <RecipeCard key={result.recipe.id} result={result} />
            ))}
          </div>
        </section>
      )}

      {results.need_buy_1_2.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-yellow-700 mb-4">
            🟡 Нужно докупить 1-2 продукта ({results.need_buy_1_2.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.need_buy_1_2.map((result) => (
              <RecipeCard key={result.recipe.id} result={result} />
            ))}
          </div>
        </section>
      )}

      {results.need_many.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-red-700 mb-4">
            🔴 Не хватает много ингредиентов ({results.need_many.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.need_many.map((result) => (
              <RecipeCard key={result.recipe.id} result={result} />
            ))}
          </div>
        </section>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-8">
        <p className="text-blue-800">
          📊 Всего найдено рецептов: <strong>{results.total}</strong>
        </p>
      </div>
    </div>
  )
}
