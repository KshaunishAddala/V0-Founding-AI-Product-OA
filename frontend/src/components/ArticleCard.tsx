interface Article {
  title: string
  description: string | null
  url: string
  thumbnail: string | null
  published_at: string
  source: string
}

interface Props {
  article: Article
}

export default function ArticleCard({ article }: Props) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <a href={article.url} target="_blank" rel="noopener noreferrer" className="article-card">
      <div className="article-thumbnail">
        {article.thumbnail ? (
          <img src={article.thumbnail} alt="" loading="lazy" />
        ) : (
          <div className="no-thumbnail">
            <span>📰</span>
          </div>
        )}
      </div>
      <div className="article-content">
        <h3>{article.title}</h3>
        {article.description && <p>{article.description}</p>}
        <div className="article-meta">
          <span className="source">{article.source}</span>
          <span className="date">{formatDate(article.published_at)}</span>
        </div>
      </div>
    </a>
  )
}
