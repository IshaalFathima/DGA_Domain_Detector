import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import AnalyzePage from './pages/AnalyzePage.jsx'
import AboutPage from './pages/AboutPage.jsx'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<AnalyzePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<AnalyzePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
