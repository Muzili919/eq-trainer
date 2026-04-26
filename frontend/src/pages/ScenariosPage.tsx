import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LogOut, User, Briefcase, Users, Heart, Baby, Brain, LayoutGrid, ArrowRight } from 'lucide-react'

interface Scenario {
  id: string
  title: string
  category: string
  difficulty: string
  description: string
  learning_objectives: string[]
}

const CATEGORIES = [
  { key: '', label: '全部', icon: LayoutGrid },
  { key: 'WORKPLACE', label: '职场', icon: Briefcase },
  { key: 'SOCIAL', label: '社交', icon: Users },
  { key: 'INTIMATE', label: '亲密', icon: Heart },
  { key: 'PARENT_CHILD', label: '亲子', icon: Baby },
  { key: 'SELF', label: '自我', icon: Brain },
] as const

const CATEGORY_BADGE: Record<string, 'workplace' | 'social' | 'intimate' | 'parent' | 'self'> = {
  WORKPLACE: 'workplace',
  SOCIAL: 'social',
  INTIMATE: 'intimate',
  PARENT_CHILD: 'parent',
  SELF: 'self',
}

const DIFFICULTY_BADGE: Record<string, 'beginner' | 'intermediate' | 'challenge'> = {
  beginner: 'beginner',
  intermediate: 'intermediate',
  challenge: 'challenge',
}

const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: '入门',
  intermediate: '进阶',
  challenge: '挑战',
}

export default function ScenariosPage() {
  const navigate = useNavigate()
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [activeCategory, setActiveCategory] = useState('')
  const currentUser = localStorage.getItem('eq_user') || ''

  useEffect(() => {
    const params = activeCategory ? `?category=${activeCategory}` : ''
    fetch(`/api/scenarios${params}`)
      .then((r) => r.json())
      .then(setScenarios)
  }, [activeCategory])

  const handleLogout = () => {
    localStorage.removeItem('eq_user')
    navigate('/', { replace: true })
  }

  const goToPractice = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    navigate(`/practice/${id}`)
  }

  return (
    <div className="min-h-screen gradient-cool">
      {/* Header */}
      <div className="glass border-b border-white/30 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gradient">选择练习场景</h1>
            <p className="text-sm text-muted-foreground">选择一个场景，开始你的高情商沟通训练</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <User className="w-3.5 h-3.5" />
              {currentUser}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-1.5 text-muted-foreground">
              <LogOut className="w-4 h-4" />
              退出
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Category Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
          {CATEGORIES.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                activeCategory === key
                  ? 'gradient-primary text-white shadow-md shadow-violet-500/25'
                  : 'bg-white/60 backdrop-blur-sm text-muted-foreground hover:bg-white/80 border border-white/40'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Scenario Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map((s, i) => (
            <div
              key={s.id}
              role="button"
              tabIndex={0}
              className="group cursor-pointer rounded-xl border bg-white/70 backdrop-blur-sm shadow-sm transition-all hover:shadow-lg hover:shadow-violet-500/5 hover:-translate-y-0.5 border-white/40 animate-fade-in"
              style={{ animationDelay: `${i * 60}ms`, animationFillMode: 'both' }}
              onClick={goToPractice(s.id)}
              onKeyDown={(e) => { if (e.key === 'Enter') goToPractice(s.id)(e) }}
            >
              <div className="p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant={CATEGORY_BADGE[s.category] || 'secondary'}>
                    {CATEGORIES.find((c) => c.key === s.category)?.label || s.category}
                  </Badge>
                  <Badge variant={DIFFICULTY_BADGE[s.difficulty] || 'secondary'}>
                    {DIFFICULTY_LABEL[s.difficulty] || s.difficulty}
                  </Badge>
                </div>

                <h3 className="font-semibold text-foreground mb-2 group-hover:text-violet-600 transition-colors">
                  {s.title}
                </h3>

                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {s.description}
                </p>

                <div className="flex flex-wrap gap-1.5 mb-4">
                  {s.learning_objectives.slice(0, 3).map((obj, j) => (
                    <span key={j} className="text-xs px-2 py-0.5 rounded-md bg-violet-50 text-violet-600">
                      {obj}
                    </span>
                  ))}
                </div>

                <div className="flex items-center text-xs text-violet-500 font-medium group-hover:gap-2 transition-all gap-1">
                  开始练习
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
