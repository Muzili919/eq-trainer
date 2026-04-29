import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ScenarioListItem } from '../lib/api'

const CATEGORY_LABEL: Record<string, string> = {
  workplace: '职场',
  family: '家庭',
  social: '朋友圈',
}

const CATEGORY_COLOR: Record<string, string> = {
  workplace: 'from-violet-500 to-violet-600',
  family: 'from-ember-500 to-ember-600',
  social: 'from-violet-500/70 to-ember-500/70',
}

const DIFFICULTY_DOTS = (n: number) => '●'.repeat(n) + '○'.repeat(5 - n)

const ROLE_LABEL: Record<string, string> = {
  decoration_boss: '装修老板',
  property_manager: '物业经理',
  beauty_clinic_boss: '医美老板',
  general: '通用',
  all: '全部',
}

type FilterRole = 'auto' | 'all' | 'decoration_boss' | 'property_manager' | 'beauty_clinic_boss' | 'general'

export default function ScenariosPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<ScenarioListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [activeRole, setActiveRole] = useState<FilterRole>('auto')
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [resolvedRole, setResolvedRole] = useState<string>('')

  useEffect(() => {
    setLoading(true)
    api.listScenarios(activeRole)
      .then(d => {
        setItems(d.items)
        setResolvedRole(d.role)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [activeRole])

  function startScenario(s: ScenarioListItem) {
    if (!s.primary_skill_id) return
    navigate(`/practice/${s.primary_skill_id}?template=${s.id}`)
  }

  // 按 category 分组
  const grouped: Record<string, ScenarioListItem[]> = {}
  items.forEach(it => {
    if (activeCategory !== 'all' && it.category !== activeCategory) return
    if (!grouped[it.category]) grouped[it.category] = []
    grouped[it.category].push(it)
  })

  const categories = ['all', 'workplace', 'family', 'social']

  return (
    <div className="app-shell pb-24">
      {/* 头部 */}
      <header className="px-5 pt-4 pb-3 animate-rise">
        <div className="flex items-center gap-2 mb-1">
          <button onClick={() => navigate(-1)} className="w-8 h-8 grid place-items-center rounded-full hover:bg-violet-500/10 transition active:scale-95" aria-label="返回">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <h1 className="font-display text-[18px] tracking-wide">自由练习</h1>
          <span className="ml-auto text-[10px] text-ink-soft dark:text-violet-300/50 font-mono tracking-widest">
            {items.length} 个场景
          </span>
        </div>
        <p className="text-[12px] text-ink-soft dark:text-violet-300/55 ml-10">
          挑一个想练的——按角色或按分类筛选
        </p>
      </header>

      {/* 角色切换 */}
      <section className="px-5 mt-2 animate-rise" style={{ animationDelay: '.05s' }}>
        <p className="text-[10px] text-ink-soft/70 dark:text-violet-300/40 font-mono tracking-widest mb-2">ROLE · 角色</p>
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-5 px-5">
          {(['auto', 'decoration_boss', 'property_manager', 'beauty_clinic_boss', 'general', 'all'] as FilterRole[]).map(r => {
            const active = activeRole === r
            const label = r === 'auto' ? `我的（${ROLE_LABEL[resolvedRole] || '加载中'}）` : ROLE_LABEL[r]
            return (
              <button key={r} onClick={() => setActiveRole(r)}
                className={`shrink-0 px-3.5 py-1.5 rounded-full text-[12px] font-display tracking-wide transition-all
                  ${active
                    ? 'bg-gradient-to-r from-violet-500 to-violet-600 text-white shadow'
                    : 'bg-violet-500/8 dark:bg-violet-500/15 text-ink-soft dark:text-violet-300/70 active:scale-95'}`}>
                {label}
              </button>
            )
          })}
        </div>
      </section>

      {/* 分类筛选 */}
      <section className="px-5 mt-4 animate-rise" style={{ animationDelay: '.1s' }}>
        <p className="text-[10px] text-ink-soft/70 dark:text-violet-300/40 font-mono tracking-widest mb-2">CATEGORY · 分类</p>
        <div className="flex gap-2">
          {categories.map(c => {
            const active = activeCategory === c
            return (
              <button key={c} onClick={() => setActiveCategory(c)}
                className={`flex-1 py-1.5 rounded-lg text-[12px] font-display tracking-wide transition-all
                  ${active
                    ? 'bg-white dark:bg-night-card shadow text-violet-600 dark:text-violet-300 ring-1 ring-violet-500/30'
                    : 'bg-violet-500/8 dark:bg-violet-500/10 text-ink-soft dark:text-violet-300/60'}`}>
                {c === 'all' ? '全部' : CATEGORY_LABEL[c]}
              </button>
            )
          })}
        </div>
      </section>

      {/* 列表 */}
      {loading ? (
        <section className="px-5 mt-5 space-y-3">
          {[0, 1, 2].map(i => <div key={i} className="paper-card h-24 animate-pulse bg-violet-500/5" />)}
        </section>
      ) : items.length === 0 ? (
        <section className="px-5 mt-12 text-center">
          <div className="text-4xl mb-3">🌫️</div>
          <p className="text-[13px] text-ink-soft dark:text-violet-300/60">这里还没有场景</p>
          <p className="text-[11px] text-ink-soft/60 dark:text-violet-300/40 mt-1">试试切换角色或分类</p>
        </section>
      ) : (
        <section className="px-5 mt-5 space-y-5">
          {Object.entries(grouped).map(([cat, list], idx) => (
            <div key={cat} className="animate-rise" style={{ animationDelay: `${.15 + idx * .05}s` }}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-1 h-4 rounded-full bg-gradient-to-b ${CATEGORY_COLOR[cat] || 'from-violet-500 to-ember-500'}`} />
                <h2 className="font-display text-[14px] tracking-wide">{CATEGORY_LABEL[cat] || cat}</h2>
                <span className="text-[10px] text-ink-soft/60 dark:text-violet-300/40 font-mono">{list.length}</span>
              </div>
              <div className="space-y-2.5">
                {list.map(s => (
                  <button key={s.id} onClick={() => startScenario(s)}
                    className="w-full text-left paper-card p-4 active:scale-[.99] transition-transform group">
                    <div className="flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <h3 className="font-display text-[14px] tracking-wide truncate">{s.title}</h3>
                          <span className="text-[9px] tracking-widest text-violet-500/70 dark:text-violet-300/50 font-mono shrink-0">
                            {DIFFICULTY_DOTS(s.difficulty)}
                          </span>
                        </div>
                        <p className="text-[12px] text-ink-soft dark:text-violet-300/60 line-clamp-2 leading-relaxed mb-2">
                          {s.role_brief}
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {s.skills.map(tag => (
                            <span key={tag.id} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-violet-500/8 dark:bg-violet-500/15 text-[10px] text-violet-600 dark:text-violet-300 font-mono tracking-wide">
                              <span>{tag.icon}</span>{tag.name}
                            </span>
                          ))}
                        </div>
                      </div>
                      <svg className="text-violet-500/50 group-hover:text-violet-500 transition-colors shrink-0 mt-1" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
