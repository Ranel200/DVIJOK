import { mockOk } from '@dvijok/shared/api/mock.js'
import { mockBlogArticles } from '@/constants/blog.js'
import { mockFaqItems } from '@/constants/faq.js'

export const faqApi = {
  async list({ limit } = {}) {
    const items = mockFaqItems.map(item => ({ ...item }))
    return mockOk(limit ? items.slice(0, limit) : items)
  }
}

export const blogApi = {
  async list({ limit } = {}) {
    const items = mockBlogArticles.map(item => structuredClone(item))
    const sorted = items.sort((a, b) => b.date.localeCompare(a.date))
    return mockOk(limit ? sorted.slice(0, limit) : sorted)
  },

  async getById(id) {
    const articleId = Number(id)
    if (!Number.isFinite(articleId)) return mockOk(null)

    const article = mockBlogArticles.find(item => item.id === articleId) ?? null
    return mockOk(article ? structuredClone(article) : null)
  }
}
