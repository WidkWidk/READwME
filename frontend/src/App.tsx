import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { HomePage } from './pages/HomePage'
import { ReadingPage } from './pages/ReadingPage'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/read/:sessionId" element={<ReadingPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
