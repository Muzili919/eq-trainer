import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

const tabs = [
  {
    key: 'home',
    path: '/',
    label: '今日',
    icon: (active: boolean) => (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12l9-9 9 9"/>
        <path d="M5 10v10h14V10"/>
      </svg>
    ),
  },
  {
    key: 'diary',
    path: '/diary',
    label: '日记',
    icon: (active: boolean) => (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    ),
  },
  {
    key: 'free',
    path: '/free',
    label: '自由',
    icon: (active: boolean) => (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8} strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12c0 4-4 7-9 7-1.5 0-3-.3-4.3-.8L3 20l1.8-4.7C3.7 13.9 3 12 3 10c0-4 4-7 9-7s9 3 9 7z"/>
      </svg>
    ),
  },
  {
    key: 'skills',
    path: '/skills',
    label: '技能',
    icon: (active: boolean) => (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8} strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    ),
  },
]

export default function TabBar() {
  const location = useLocation()
  const navigate = useNavigate()

  async function handleClick(key: string, path: string) {
    if (key === 'free') {
      // 自由对练：随机抽一个技能进入练习
      try {
        const skills = await api.skills()
        if (skills.length > 0) {
          const random = skills[Math.floor(Math.random() * skills.length)]
          navigate(`/practice/${random.id}`)
          return
        }
      } catch {
        // 失败兜底
      }
      navigate('/skills')
      return
    }
    navigate(path)
  }

  return (
    <nav className="tabbar">
      {tabs.map(tab => {
        const active = tab.key === 'free'
          ? false
          : location.pathname === tab.path
        return (
          <button
            key={tab.key}
            className={`flex-1 flex flex-col items-center justify-center gap-1 text-[10.5px] font-display tracking-widest relative transition-colors
              ${active ? 'text-violet-600 dark:text-violet-300' : 'text-ink-soft dark:text-violet-300/60'}`}
            onClick={() => handleClick(tab.key, tab.path)}
          >
            {active && (
              <span className="absolute top-1.5 left-1/2 -translate-x-1/2 w-8 h-[3px] rounded-full bg-gradient-to-r from-violet-500 to-ember-500" />
            )}
            {tab.icon(active)}
            {tab.label}
          </button>
        )
      })}
    </nav>
  )
}
