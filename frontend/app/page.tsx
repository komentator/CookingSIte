import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-center max-w-2xl">
        <h1 className="text-6xl font-bold text-orange-600 mb-6">🍳 CookingSite</h1>
        <p className="text-2xl text-gray-700 mb-4">
          Найдите рецепты для того, что есть дома
        </p>
        <p className="text-lg text-gray-600 mb-12">
          Введите ингредиенты, выберите время приготовления и получите идеальный рецепт
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/search"
            className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-6 px-8 rounded-2xl text-xl transition transform hover:scale-105"
          >
            📋 Начать поиск
          </Link>

          <Link
            href="/recipes"
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-6 px-8 rounded-2xl text-xl transition transform hover:scale-105"
          >
            📖 Все рецепты
          </Link>

          <Link
            href="/fridge"
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-6 px-8 rounded-2xl text-xl transition transform hover:scale-105"
          >
            🧊 Мой холодильник
          </Link>

          <Link
            href="/shopping"
            className="bg-purple-500 hover:bg-purple-600 text-white font-bold py-6 px-8 rounded-2xl text-xl transition transform hover:scale-105"
          >
            📝 Список покупок
          </Link>
        </div>

        <div className="mt-16 bg-orange-50 border-2 border-orange-200 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">✨ Особенности</h2>
          <ul className="text-left space-y-3 text-gray-700">
            <li>✅ Поиск по ингредиентам с нечеткым совпадением</li>
            <li>🤖 Умный поиск на естественном языке (AI)</li>
            <li>🌡️ Фильтр по времени приготовления и калорийности</li>
            <li>🧊 Сохраните продукты в личный холодильник</li>
            <li>📝 Автоматический список покупок</li>
            <li>🔄 Замены ингредиентов и синонимы</li>
          </ul>
        </div>
      </div>
    </main>
  )
}
