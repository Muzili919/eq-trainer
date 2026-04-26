import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, SkillItem } from '../lib/api'

const CATEGORY_LABELS: Record<string, string> = {
  listening: '倾听', expression: '表达', empathy: '共情',
  boundary: '边界', resolution: '化解', humor: '幽默进阶',
}
const CATEGORY_EMOJI: Record<string, string> = {
  listening: '👂', expression: '💬', empathy: '💜',
  boundary: '🛡️', resolution: '🤝', humor: '✨',
}

export default function SkillsPage() {
  const navigate = useNavigate()
  const [skills, setSkills] = useState<SkillItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.skills().then(s => { setSkills(s); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const grouped = skills.reduce<Record<string, SkillItem[]>>((acc, s) => {
    if (!acc[s.category]) acc[s.category] = []
    acc[s.category].push(s)
    return acc
  }, {})

  return (
    <div className="app-shell">
      <header className="px-5 pt-5 pb-3">
        <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300">SKILL TREE</div>
        <h1 className="font-display text-[22px] mt-0.5">技能树</h1>
        <p className="text-[12px] text-ink-soft dark:text-violet-300/60 mt-1">12 项高情商沟通技能，按 SRS 推进</p>
      </header>

      {loading ? (
        <div className="px-5 space-y-3">
          {[1,2,3].map(i => <div key={i} className="paper-card h-32 animate-pulse" />)}
        </div>
      ) : (
        <div className="px-5 space-y-6 pb-4">
          {Object.entries(CATEGORY_LABELS).map(([cat, label]) => {
            const items = grouped[cat] ?? []
            if (!items.length) return null
            return (
              <section key={cat} className="animate-rise">
                <div className="flex items-center gap-2 mb-3">
                  <span>{CATEGORY_EMOJI[cat]}</span>
                  <h2 className="font-display text-[12px] tracking-[.2em] text-ink dark:text-violet-50">{label}</h2>
                  <div className="flex-1 h-px bg-violet-500/15" />
                </div>
                <div className="space-y-2.5">
                  {items.map(skill => (
                    <button
                      key={skill.id}
                      onClick={() => navigate(`/practice/${skill.id}`)}
                      className="paper-card w-full p-4 text-left flex items-center gap-4 active:scale-[.99] transition-transform"
                    >
                      <div className="shrink-0">
                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-500/15 to-ember-500/10 flex items-center justify-center font-display text-[12px] text-violet-600 dark:text-violet-300">
                          {skill.id}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-display text-[13px]">{skill.name}</span>
                          <span className="font-mono text-[10px] text-violet-500/70">Lv.{skill.level}</span>
                        </div>
                        <p className="text-[11.5px] text-ink-soft dark:text-violet-300/60 mt-0.5 leading-relaxed line-clamp-1">
                          {skill.description}
                        </p>
                        <div className="score-bar-track mt-2" style={{height:4}}>
                          <div className="score-bar-fill" style={{width:`${skill.level * 20}%`, height:'100%'}} />
                        </div>
                      </div>
                      <div className="shrink-0 flex flex-col items-end gap-1">
                        <div className="flex gap-0.5">
                          {[1,2,3,4,5].map(s => (
                            <span key={s} className={s <= skill.level ? 'text-ember-500' : 'text-violet-500/20'} style={{fontSize:9}}>★</span>
                          ))}
                        </div>
                        {skill.next_review_at ? (
                          <span className="font-mono text-[9px] text-violet-500/60">待复习</span>
                        ) : (
                          <span className="font-mono text-[9px] text-ember-500/70">练吧</span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </section>
            )
          })}
        </div>
      )}
    </div>
  )
}
