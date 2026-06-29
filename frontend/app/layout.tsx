import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CookingSite - Поиск рецептов по продуктам',
  description: 'Найдите рецепты, которые можно приготовить из имеющихся продуктов',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>
        <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
          <header className="bg-white shadow-sm">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-orange-600">🍳 CookingSite</h1>
                <ul className="flex gap-6">
                  <li><a href="/" className="text-gray-600 hover:text-orange-600">Главная</a></li>
                  <li><a href="/search" className="text-gray-600 hover:text-orange-600">Поиск</a></li>
                  <li><a href="/recipes" className="text-gray-600 hover:text-orange-600">Рецепты</a></li>
                  <li><a href="/fridge" className="text-gray-600 hover:text-orange-600">Холодильник</a></li>
                  <li><a href="/shopping" className="text-gray-600 hover:text-orange-600">Покупки</a></li>
                </ul>
              </div>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
