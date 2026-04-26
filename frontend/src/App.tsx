import { useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { initTheme } from './lib/utils'
import TabBar from './components/TabBar'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import PracticePage from './pages/PracticePage'
import DiaryPage from './pages/DiaryPage'
import SkillsPage from './pages/SkillsPage'
import ScenariosPage from './pages/ScenariosPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('eq_token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

const HIDE_TABBAR = ['/login', '/practice']

export default function App() {
  const location = useLocation()
  const showTab = !HIDE_TABBAR.some(p => location.pathname.startsWith(p))

  useEffect(() => { initTheme() }, [])

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<RequireAuth><HomePage /></RequireAuth>} />
        <Route path="/practice/:skillId" element={<RequireAuth><PracticePage /></RequireAuth>} />
        <Route path="/diary" element={<RequireAuth><DiaryPage /></RequireAuth>} />
        <Route path="/skills" element={<RequireAuth><SkillsPage /></RequireAuth>} />
        <Route path="/scenarios" element={<RequireAuth><ScenariosPage /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      {showTab && <TabBar />}
    </>
  )
}
