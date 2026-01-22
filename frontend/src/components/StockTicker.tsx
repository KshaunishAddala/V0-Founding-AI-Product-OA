import { useEffect, useState } from 'react'

interface Stock {
  symbol: string
  price: number
  change: number
  change_percent: number
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function StockTicker() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await fetch(`${API_URL}/api/stocks`)
        if (!res.ok) throw new Error('Failed to fetch')
        const data = await res.json()
        setStocks(data.stocks)
      } catch {
        console.error('Could not load stocks')
      } finally {
        setLoading(false)
      }
    }

    fetchStocks()
    const interval = setInterval(fetchStocks, 60000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <aside className="stock-sidebar">
        <h3>AI Stocks</h3>
        <p className="stock-loading">Loading...</p>
      </aside>
    )
  }

  return (
    <aside className="stock-sidebar">
      <h3>AI Stocks</h3>
      <div className="stock-list">
        {stocks.map(stock => (
          <div key={stock.symbol} className="stock-item">
            <div className="stock-info">
              <span className="stock-symbol">{stock.symbol}</span>
              <span className="stock-price">${stock.price.toLocaleString()}</span>
            </div>
            <span className={`stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
              {stock.change >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </aside>
  )
}
