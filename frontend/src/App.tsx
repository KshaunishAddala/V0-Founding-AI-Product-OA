import { useState } from 'react'
import SummarySection from './components/SummarySection'
import ArticlesGrid from './components/ArticlesGrid'
import StockTicker from './components/StockTicker'
import './App.css'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)

  return (
    <div className="app-container">
      <div className="app">
        <header className="header">
          <h1>Tech Pulse</h1>
          <p>Your daily digest of what's happening in tech</p>
        </header>
        
        <main>
          <SummarySection onRefresh={() => setRefreshKey(k => k + 1)} />
          <ArticlesGrid key={refreshKey} />
        </main>
        
        <footer className="footer">
          <p>Powered by NewsAPI and OpenAI</p>
        </footer>
      </div>
      
      <StockTicker />
    </div>
  )
}

export default App
