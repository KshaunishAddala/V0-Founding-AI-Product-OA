import { useEffect, useState } from 'react'
import ArticleCard from './ArticleCard'

interface Article {
  title: string
  description: string | null
  url: string
  thumbnail: string | null
  published_at: string
  source: string
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ARTICLES_PER_PAGE = 9

export default function ArticlesGrid() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const res = await fetch(`${API_URL}/api/articles`)
        if (!res.ok) throw new Error('Failed to fetch')
        const data = await res.json()
        setArticles(data.articles)
      } catch {
        setError('Could not load articles')
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
  }, [])

  const totalPages = Math.ceil(articles.length / ARTICLES_PER_PAGE)
  const startIndex = (currentPage - 1) * ARTICLES_PER_PAGE
  const currentArticles = articles.slice(startIndex, startIndex + ARTICLES_PER_PAGE)

  const goToPage = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: document.querySelector('.articles-section')?.getBoundingClientRect().top! + window.scrollY - 100, behavior: 'smooth' })
  }

  if (loading) return <section className="articles-section"><p className="loading">Loading articles...</p></section>
  if (error) return <section className="articles-section"><p className="error">{error}</p></section>

  return (
    <section className="articles-section">
      <h2>Latest Tech News</h2>
      <div className="articles-grid">
        {currentArticles.map((article, idx) => (
          <ArticleCard key={idx} article={article} />
        ))}
      </div>
      
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            onClick={() => goToPage(currentPage - 1)} 
            disabled={currentPage === 1}
            aria-label="Previous page"
          >
            ‹
          </button>
          <span>{currentPage} of {totalPages}</span>
          <button 
            onClick={() => goToPage(currentPage + 1)} 
            disabled={currentPage === totalPages}
            aria-label="Next page"
          >
            ›
          </button>
        </div>
      )}
    </section>
  )
}
