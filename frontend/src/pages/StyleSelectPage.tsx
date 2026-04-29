import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, StyleInfo } from '../lib/api'

export default function StyleSelectPage() {
  const navigate = useNavigate()
  const [styles, setStyles] = useState<StyleInfo[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [expanded, setExpanded] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedFlash, setSavedFlash] = useState(false)

  useEffect(() => {
    // 同时拉风格列表 + 用户已选，让进入页面时能预填上次的选择
    Promise.all([api.getStyles(), api.me().catch(() => null)])
      .then(([r, me]) => {
        setStyles(r.styles)
        if (me && Array.isArray(me.target_styles) && me.target_styles.length > 0) {
          setSelected(new Set(me.target_styles))
        }
      })
      .catch(() => setError('加载风格列表失败，请刷新重试'))
  }, [])

  function toggle(id: string) {
    setError(null)
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else if (next.size < 3) {
        next.add(id)
      }
      return next
    })
  }

  async function confirm() {
    if (selected.size === 0 || saving) return
    setSaving(true); setError(null)
    try {
      await api.saveStyles([...selected])
      // 显示成功反馈再跳，避免"瞬间消失"让用户怀疑没生效
      setSavedFlash(true)
      setTimeout(() => navigate('/', { replace: true }), 700)
    } catch (err: any) {
      setError(err?.message ?? '保存失败，请重试')
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-paper dark:bg-night-deeper px-4 py-8">
      <div className="max-w-[520px] mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="font-display text-[22px] tracking-wide">选择你的风格路线</h1>
          <p className="text-[13px] text-ink-soft dark:text-violet-300/60">
            选择最多 3 位你想学习的高情商风格，后续可以随时修改
          </p>
          <p className="text-[12px] font-mono text-violet-500">
            已选 {selected.size} / 3
          </p>
        </div>

        {/* Style grid */}
        <div className="grid grid-cols-2 gap-3">
          {styles.map(s => {
            const isSelected = selected.has(s.id)
            const isExpanded = expanded === s.id
            return (
              <div key={s.id}
                className={`rounded-2xl border-2 transition-all overflow-hidden ${
                  isSelected
                    ? 'border-violet-500 bg-violet-500/6 shadow-[0_4px_20px_-4px_rgba(124,58,237,.25)]'
                    : 'border-violet-500/15 bg-white dark:bg-night-card'
                }`}
              >
                {/* Card header */}
                <button
                  className="w-full text-left p-4"
                  onClick={() => toggle(s.id)}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl shrink-0">{s.icon}</span>
                    <div className="min-w-0 flex-1">
                      <div className="font-display text-[14px] tracking-wide">{s.name}</div>
                      <div className="text-[11px] text-violet-500 dark:text-violet-300 font-mono mt-0.5">
                        {s.school}
                      </div>
                    </div>
                    {isSelected && (
                      <span className="w-5 h-5 rounded-full bg-violet-500 text-white grid place-items-center text-[11px] shrink-0">
                        ✓
                      </span>
                    )}
                  </div>
                </button>

                {/* Expand toggle */}
                <button
                  className="w-full px-4 pb-2 text-[10px] text-violet-500/70 dark:text-violet-300/50 text-left"
                  onClick={(e) => { e.stopPropagation(); setExpanded(isExpanded ? null : s.id) }}
                >
                  {isExpanded ? '收起 ▲' : '了解更多 ▼'}
                </button>

                {/* Expanded detail */}
                {isExpanded && (
                  <div className="px-4 pb-4 space-y-3 animate-rise" style={{ animationDuration: '0.15s' }}>
                    <div className="text-[12px] text-ink-soft dark:text-violet-300/70 italic leading-relaxed">
                      "{s.philosophy}"
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-violet-500 tracking-widest mb-1">代表名场面</div>
                      <div className="text-[11.5px] leading-relaxed">{s.famous_scene}</div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-violet-500 tracking-widest mb-1">你会学到</div>
                      <div className="flex flex-wrap gap-1">
                        {s.learn.map(t => (
                          <span key={t} className="px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-600 dark:text-violet-300 text-[10px]">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-[11px] text-ink-soft dark:text-violet-300/60">
                      适合：{s.for_who}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="text-[12px] text-ember-600 dark:text-ember-300 text-center py-2 px-3 rounded-xl bg-ember-500/10 border border-ember-500/30">
            {error}
          </div>
        )}

        {/* 成功反馈 */}
        {savedFlash && (
          <div className="flex items-center justify-center gap-2 py-3 rounded-2xl bg-violet-500/10 border border-violet-500/30 animate-rise" style={{ animationDuration: '0.2s' }}>
            <span className="w-6 h-6 rounded-full bg-violet-500 text-white grid place-items-center text-[13px]">✓</span>
            <span className="text-[13px] font-display text-violet-600 dark:text-violet-300 tracking-wide">已保存，正在返回首页…</span>
          </div>
        )}

        {/* Confirm button */}
        {!savedFlash && (
          <button
            onClick={confirm}
            disabled={selected.size === 0 || saving}
            className="w-full py-4 rounded-2xl font-display text-[14px] tracking-widest
              bg-gradient-to-r from-violet-500 to-violet-600 text-white
              shadow-[0_10px_28px_-8px_rgba(124,58,237,.6)] active:scale-[.98] transition-transform
              disabled:opacity-40 disabled:shadow-none"
          >
            {saving
              ? '保存中…'
              : selected.size === 0
                ? '至少选择 1 个风格'
                : selected.size === 3
                  ? '保存这 3 个风格'
                  : `保存（已选 ${selected.size}/3，可继续选）`}
          </button>
        )}
      </div>
    </div>
  )
}
