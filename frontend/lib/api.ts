const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  async searchByIngredients(ingredients: string[]) {
    const response = await fetch(`${API_URL}/api/search/by-ingredients`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ingredients,
        cooking_time_max: null,
        servings: null,
      }),
    })

    if (!response.ok) {
      throw new Error('Search failed')
    }

    return response.json()
  },

  async getRecipes(skip = 0, limit = 200) {
    const response = await fetch(
      `${API_URL}/api/recipes?skip=${skip}&limit=${limit}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch recipes')
    }

    return response.json()
  },

  async getRecipe(id: number) {
    const response = await fetch(`${API_URL}/api/recipes/${id}`)

    if (!response.ok) {
      throw new Error('Failed to fetch recipe')
    }

    return response.json()
  },

  async createRecipe(recipe: any) {
    const response = await fetch(`${API_URL}/api/recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(recipe),
    })

    if (!response.ok) {
      throw new Error('Failed to create recipe')
    }

    return response.json()
  },

  async getIngredients(skip = 0, limit = 100) {
    const response = await fetch(
      `${API_URL}/api/ingredients?skip=${skip}&limit=${limit}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch ingredients')
    }

    return response.json()
  },

  async createIngredient(name: string, category?: string) {
    const response = await fetch(`${API_URL}/api/ingredients`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        category,
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to create ingredient')
    }

    return response.json()
  },

  async getFridge(userId: number) {
    const response = await fetch(`${API_URL}/api/fridge/${userId}`)

    if (!response.ok) {
      throw new Error('Failed to fetch fridge')
    }

    return response.json()
  },

  async addToFridge(userId: number, ingredients: string[]) {
    const response = await fetch(`${API_URL}/api/fridge/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ingredients),
    })

    if (!response.ok) {
      throw new Error('Failed to add to fridge')
    }

    return response.json()
  },

  async removeFromFridge(userId: number, ingredientId: number) {
    const response = await fetch(
      `${API_URL}/api/fridge/${userId}/${ingredientId}`,
      {
        method: 'DELETE',
      }
    )

    if (!response.ok) {
      throw new Error('Failed to remove from fridge')
    }

    return response.json()
  },
}
