import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, HomeSummary } from '../lib/api'
import AccountSwitcher from '../components/AccountSwitcher'
import { formatDate, getUsername, toggleDark, weekdayLabel } from '../lib/utils'

const STAGE_HINT: Record<string, string> = {
  basic: '基础',
  mid: '中阶 · 掌握',
  advanced: '高阶',
  master: '最高阶',
}

const STYLE_DOT: Record<string, string> = {
  huangbo: 'bg-violet-500',
  xuzhisheng: 'bg-ember-500',
  lixueqin: 'bg-ink',
  hejiong: 'bg-violet-500/40',
}

const STYLE_BAR: Record<string, string> = {
  huangbo: 'bg-gradient-to-r from-violet-500 to-violet-600',
  xuzhisheng: 'bg-gradient-to-r from-ember-500 to-ember-600',
  lixueqin: 'bg-gradient-to-r from-ink to-violet-900',
  hejiong: 'bg-gradient-to-r from-violet-500/50 to-violet-500/60',
}

function levelToPercent(level: number): number {
  return Math.min(100, Math.max(8, level * 20))
}

export default function HomePage() {
  const navigate = useNavigate()
  const username = getUsername()
  const [data, setData] = useState<HomeSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const today = new Date()

  useEffect(() => {
    api.homeSummary()
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  function startBlindBox() {
    if (!data || data.today_blind_box.scenes.length === 0) return
    const first = data.today_blind_box.scenes[0]
    navigate(`/practice/${first.skill_id}`)
  }

  if (loading || !data) {
    return (
      <div className="app-shell">
        <header className="px-5 pt-4 pb-3 flex items-center gap-3 animate-rise">
          <div className="w-7 h-7 rounded-full bg-violet-500/10 animate-pulse" />
          <div className="ml-auto h-6 w-16 rounded-full bg-violet-500/10 animate-pulse" />
          <div className="w-8 h-8 rounded-full bg-violet-500/10 animate-pulse" />
          <div className="w-8 h-8 rounded-full bg-violet-500/10 animate-pulse" />
        </header>
        <section className="px-5 mt-2 space-y-4">
          <div className="paper-card h-28 animate-pulse bg-violet-500/5" />
          <div className="paper-card h-40 animate-pulse bg-violet-500/5" />
          <div className="paper-card h-64 animate-pulse bg-violet-500/5" />
        </section>
      </div>
    )
  }

  const dayCount = String(data.streak.day_count).padStart(3, '0')
  const firstScene = data.today_blind_box.scenes[0]
  const focusSkillName = firstScene?.skill_name ?? '幽默破冰'

  return (
    <div className="app-shell">
      {/* ============ 顶部状态条 ============ */}
      <header className="px-5 pt-4 pb-3 flex items-center gap-3 animate-rise">
        <div className="flex items-center gap-2">
          <svg width="30" height="30" viewBox="0 0 40 40">
            <defs>
              <linearGradient id="lg" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0" stopColor="#7C3AED" /><stop offset="1" stopColor="#F97316" />
              </linearGradient>
            </defs>
            <path d="M20 3 L23.5 14 L35 17 L26 24 L29 36 L20 29 L11 36 L14 24 L5 17 L16.5 14 Z" fill="url(#lg)" />
          </svg>
          <div className="font-display text-[15px] tracking-wider leading-none">
            EQ<br /><span className="text-[9px] tracking-[.3em] text-ink-soft dark:text-violet-300/55">TRAINER</span>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-ember-500/10 border border-ember-500/30 text-ember-600 dark:text-ember-300">
          <span className="animate-flicker text-[14px]">🔥</span>
          <span className="font-display text-[13px]">
            {data.streak.current}<span className="text-[10px] ml-0.5 tracking-widest">天</span>
          </span>
        </div>

        <button onClick={toggleDark} className="w-9 h-9 rounded-full border border-violet-500/25 grid place-items-center active:scale-95 transition" aria-label="toggle theme">
          <svg className="dark:hidden" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4 12H2M22 12h-2M5 5l1.4 1.4M17.6 17.6 19 19M5 19l1.4-1.4M17.6 6.4 19 5" />
          </svg>
          <svg className="hidden dark:block" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
          </svg>
        </button>

        <AccountSwitcher />
      </header>

      {/* ============ 吉祥物 + 思考泡 ============ */}
      <section className="px-5 pt-2 animate-rise" style={{ animationDelay: '.06s' }}>
        <div className="flex items-start gap-4">
          <div className="relative shrink-0">
            <svg className="absolute -top-2 -right-2 animate-twinkle z-10" width="16" height="16" viewBox="0 0 24 24" fill="#F97316">
              <path d="M12 0 14 10 24 12 14 14 12 24 10 14 0 12 10 10z" />
            </svg>
            <svg className="absolute -bottom-1 left-2 animate-twinkle z-10" style={{ animationDelay: '1s' }} width="10" height="10" viewBox="0 0 24 24" fill="#7C3AED">
              <path d="M12 0 14 10 24 12 14 14 12 24 10 14 0 12 10 10z" />
            </svg>
            <div className="w-[88px] h-[88px] rounded-full bg-gradient-to-br from-violet-500/15 to-ember-500/10 grid place-items-center animate-float overflow-hidden">
              <img src="/star-sea.png" alt="星海" className="w-full h-full object-contain drop-shadow-[0_8px_16px_rgba(124,58,237,.35)]" />
            </div>
          </div>
          <div className="pt-1 min-w-0 flex-1">
            <div className="flex items-center gap-1.5 text-[10.5px] text-ink-soft dark:text-violet-300/60 font-mono">
              <span>{formatDate()}</span><span>·</span><span>周{weekdayLabel(today)}</span>
              <span className="deco-stamp ml-1 text-violet-500 dark:text-violet-300 text-[9px]">DAY {dayCount}</span>
            </div>
            <h1 className="font-display text-[26px] leading-[1.18] mt-2 tracking-wide">
              {username}，<br />
              <span className="underline-brush">今天又来练话术了？</span>
            </h1>
          </div>
        </div>

        <div className="thought-bubble mt-5 ml-6 text-[13px] text-ink dark:text-violet-300/90">
          <span className="text-[10px] font-mono text-violet-500 dark:text-violet-300 tracking-widest">STAR SEA · 星海</span>
          <div className="mt-1 leading-relaxed">
            我昨夜偷看了你的进度——<b className="text-violet-600 dark:text-violet-300">「{focusSkillName}」</b>还欠点火候，今天我们悄悄练一下。
          </div>
        </div>
      </section>

      {/* ============ 7 日打卡条带 ============ */}
      <section className="px-5 mt-5 animate-rise" style={{ animationDelay: '.1s' }}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-[11px] font-mono text-ink-soft dark:text-violet-300/60">
            <span className="font-display text-violet-600 dark:text-violet-300 tracking-[.2em]">STREAK</span>
            <span>· 本周</span>
          </div>
          <div className="text-[11px] text-ink-soft dark:text-violet-300/65">
            <b className="font-display text-violet-600 dark:text-violet-300 text-[14px]">{data.streak.current}</b> 天连击
            · 本周 <b className="font-display text-ember-500">{data.streak.week_done}</b>/7
          </div>
        </div>
        <div className="streak-strip">
          {data.streak.week.map(d => (
            <div key={d.date} className={`streak-cell ${d.done ? 'done' : ''} ${d.today ? 'today' : ''}`}>
              <span>{d.day}</span>
              <span className="text-[9px] opacity-60 mt-0.5 font-mono">{d.weekday}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ============ 你最像谁（统计卡） ============ */}
      <section className="px-5 mt-6 animate-rise" style={{ animationDelay: '.16s' }}>
        <div className="paper-card p-5 relative overflow-hidden">
          <div className="tape" style={{ left: '50%', transform: 'translateX(-50%) rotate(-6deg)' }} />
          <div className="flex items-center justify-between gap-2">
            <div>
              <div className="font-display text-[10.5px] tracking-[.3em] text-violet-600 dark:text-violet-300">YOUR STYLE</div>
              <h3 className="font-display text-[20px] mt-0.5">你最像谁</h3>
            </div>
            <div className="text-right text-[10px] text-ink-soft dark:text-violet-300/55 font-mono leading-tight">
              基于<br />
              <b className="font-display text-violet-600 dark:text-violet-300 text-[15px]">{data.style_stats.total_count}</b> 次评分
            </div>
          </div>

          <ul className="mt-4 space-y-2.5 text-[13px]">
            {data.style_stats.distribution.map(item => (
              <li key={item.key} className="flex items-center gap-3">
                <span className="flex items-center gap-1.5 w-[88px] shrink-0">
                  <span className={`w-1.5 h-1.5 rounded-full ${STYLE_DOT[item.key] ?? 'bg-violet-500'}`} />
                  {item.name}
                </span>
                <div className="flex-1 h-1.5 rounded-full bg-violet-500/15 overflow-hidden">
                  <div
                    className={`h-full ${STYLE_BAR[item.key] ?? 'bg-violet-500'}`}
                    style={{ width: `${item.pct}%` }}
                  />
                </div>
                <span className="font-mono text-[11px] text-violet-600 dark:text-violet-300 w-9 text-right">{item.pct}%</span>
              </li>
            ))}
          </ul>

          <div className="mt-3 pt-3 border-t border-dashed border-violet-500/25 text-[11.5px] text-ink-soft dark:text-violet-300/60 leading-relaxed">
            {data.style_stats.total_count === 0
              ? '开始练习后，这里会显示你的风格分布'
              : data.style_stats.top_recent
                ? <>最近 7 天略偏 <span className="match-chip ml-0.5 inline-block">{data.style_stats.distribution.find(x => x.key === data.style_stats.top_recent)?.name ?? ''}</span></>
                : '继续练习，让风格画像更清晰'}
          </div>
        </div>
      </section>

      {/* ============ 今日盲盒 hero ============ */}
      <section className="px-5 mt-6 animate-rise" style={{ animationDelay: '.22s' }}>
        <div className="paper-card overflow-hidden relative active:translate-y-[-2px] transition-transform">
          <div className="absolute -top-12 -right-10 w-[200px] h-[200px] rounded-full opacity-60 pointer-events-none"
            style={{ background: 'radial-gradient(circle, rgba(249,115,22,.45) 0%, transparent 65%)' }} />
          <div className="absolute -bottom-16 -left-8 w-[180px] h-[180px] rounded-full opacity-50 pointer-events-none"
            style={{ background: 'radial-gradient(circle, rgba(124,58,237,.5) 0%, transparent 65%)' }} />

          <div className="relative p-5 pt-6">
            <div className="flex items-center gap-2">
              <span className="deco-stamp text-ember-600 dark:text-ember-300 text-[10px]">TODAY · 今日</span>
              <span className="text-[11px] font-mono text-ink-soft dark:text-violet-300/60">
                {data.today_blind_box.minutes_estimate} 分钟 · {data.today_blind_box.total} 道场景
              </span>
            </div>

            <h2 className="font-display text-[26px] leading-[1.15] mt-3">
              打开盲盒，<br />
              <span className="text-ember-600 dark:text-ember-300">今日场景题</span>
            </h2>

            {data.today_blind_box.skills_label && (
              <p className="mt-2.5 text-[13px] text-ink-soft dark:text-violet-300/70 leading-relaxed">
                今天涉及 <b className="text-ink dark:text-violet-300/95">{data.today_blind_box.skills_label}</b>。
              </p>
            )}

            {/* 堆叠卡 */}
            {firstScene && (
              <div className="relative h-[150px] mt-5">
                <div className="absolute right-2 top-3 w-[80%] h-[80%] rounded-2xl bg-violet-500/20 rotate-6"></div>
                <div className="absolute right-5 top-1 w-[80%] h-[80%] rounded-2xl bg-ember-500/25 -rotate-3"></div>
                <div className="absolute right-8 top-5 w-[80%] h-[80%] rounded-2xl bg-gradient-to-br from-violet-500 to-ink p-4 text-white flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="font-display text-[10px] tracking-[.3em] opacity-70">SCENE · 01</div>
                    <div className="mt-1.5 text-[12.5px] leading-relaxed opacity-95 line-clamp-3">
                      {firstScene.scenario_title
                        ? `「${firstScene.scenario_title}」 ${firstScene.scenario_setup ?? ''}`
                        : firstScene.scene_brief}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[10px] opacity-85 font-mono">
                    <span>{firstScene.skill_id} · {firstScene.skill_name}</span>
                    <span className="px-1.5 py-0.5 border border-white/40 rounded-full">
                      {'★'.repeat(Math.max(1, firstScene.difficulty))}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* 进度刻度 */}
            <div className="mt-5 flex items-center gap-2 text-[12px]">
              <div className="flex-1 h-1.5 rounded-full bg-violet-500/15 overflow-hidden relative">
                <div
                  className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-violet-500 via-ember-500 to-ember-300"
                  style={{ width: `${(1 / Math.max(1, data.today_blind_box.total)) * 100}%` }}
                />
                <div className="absolute inset-y-0 left-1/3 w-px bg-white/80" />
                <div className="absolute inset-y-0 left-2/3 w-px bg-white/80" />
              </div>
              <span className="font-display text-violet-600 dark:text-violet-300 text-[11px]">
                1<span className="text-ink-soft dark:text-violet-300/60">/{data.today_blind_box.total}</span>
              </span>
            </div>

            <button
              onClick={startBlindBox}
              disabled={!firstScene}
              className="mt-5 w-full inline-flex items-center justify-center gap-3 px-5 py-3.5 rounded-full bg-ink text-white font-display tracking-[.18em] active:translate-y-[1px] transition disabled:opacity-50"
              style={{ boxShadow: '0 10px 30px -10px rgba(249,115,22,.55), inset 0 1px 0 rgba(255,255,255,.35)' }}
            >
              <span>开 启 今 日 训 练</span>
              <span className="w-6 h-6 rounded-full bg-ember-500 grid place-items-center">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round">
                  <path d="M5 12h14M13 5l7 7-7 7" />
                </svg>
              </span>
            </button>
          </div>
        </div>
      </section>

      {/* ============ 苏格拉底引导泡 ============ */}
      <section className="px-5 mt-6 animate-rise" style={{ animationDelay: '.28s' }}>
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500/15 to-ember-500/10 grid place-items-center shrink-0 animate-float overflow-hidden">
            <img src="/star-sea.png" alt="" className="w-9 h-9 object-contain" />
          </div>
          <div className="thought-bubble flex-1 text-[13px] leading-relaxed">
            <span className="text-[10px] font-mono text-violet-500 dark:text-violet-300 tracking-widest">SOCRATIC · 苏格拉底</span>
            <div className="mt-1.5 italic">
              "ta 这话背后真正想说的是什么？"
              <br />
              <span className="not-italic text-[12px] text-ink-soft dark:text-violet-300/60">—— 想想再开始也不迟</span>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 12 拼图 ============ */}
      <section className="mt-7 animate-rise" style={{ animationDelay: '.32s' }}>
        <div className="px-5 flex items-end justify-between gap-3 mb-3">
          <div>
            <div className="font-display text-[10.5px] tracking-[.3em] text-violet-600 dark:text-violet-300">SKILLS · 拼图</div>
            <h2 className="font-display text-[20px] mt-0.5">
              {data.skills.total} 块拼图，已点亮 <span className="text-ember-600 dark:text-ember-300">{data.skills.lit}</span>
            </h2>
          </div>
          <button onClick={() => navigate('/skills')} className="text-[11.5px] text-violet-600 dark:text-violet-300 inline-flex items-center gap-0.5">
            全部 <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M9 6l6 6-6 6" /></svg>
          </button>
        </div>

        <div className="flex gap-3 overflow-x-auto px-5 pb-3 -mx-0" style={{ scrollSnapType: 'x mandatory', scrollbarWidth: 'none' }}>
          {data.skills.items.slice(0, 5).map(skill => {
            const pct = levelToPercent(skill.level)
            const isToday = firstScene?.skill_id === skill.id
            return (
              <button
                key={skill.id}
                onClick={() => navigate(`/practice/${skill.id}`)}
                className={`paper-card p-4 text-left shrink-0 active:translate-y-[-3px] transition-transform ${isToday ? 'ring-2 ring-ember-500/50' : ''}`}
                style={{ flex: '0 0 64%', scrollSnapAlign: 'start' }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[22px]">{skill.icon}</span>
                  <span className="text-[9.5px] font-mono tracking-widest text-ink-soft dark:text-violet-300/55">{skill.id}</span>
                </div>
                <div className="mt-2.5">
                  <div className="font-display text-[15px]">{skill.name}</div>
                  <div className={`text-[11px] mt-0.5 ${isToday ? 'text-ember-600 dark:text-ember-300' : 'text-ink-soft dark:text-violet-300/60'}`}>
                    {STAGE_HINT[skill.stage] ?? skill.stage}{isToday ? ' · 今日主推' : ''}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-3">
                  <div
                    className="grid place-items-center relative rounded-full"
                    style={{
                      width: 42,
                      height: 42,
                      background: `conic-gradient(#7C3AED ${pct}%, rgba(124,58,237,.12) 0)`,
                    }}
                  >
                    <div className="absolute inset-[4px] rounded-full bg-[#FFFDF8] dark:bg-night-card" />
                    <span className="relative font-display text-[11px] text-violet-600 dark:text-violet-300">{skill.level}/5</span>
                  </div>
                  <span className="text-[10px] font-mono text-ember-600">
                    {skill.level >= 5 ? '✦ 精通' : skill.level >= 3 ? '↗ 提升' : skill.level >= 1 ? '● 复习' : '起步'}
                  </span>
                </div>
              </button>
            )
          })}

          <button
            onClick={() => navigate('/skills')}
            className="paper-card p-4 flex flex-col items-center justify-center gap-2 text-violet-600 dark:text-violet-300 shrink-0"
            style={{ flex: '0 0 38%', scrollSnapAlign: 'start' }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><path d="M9 9l6 6M15 9l-6 6" />
            </svg>
            <div className="font-display text-[12px] tracking-widest">还有 {Math.max(0, data.skills.total - 5)} 块</div>
            <div className="text-[10px] text-ink-soft dark:text-violet-300/55">技能地图</div>
          </button>
        </div>
      </section>

      {/* ============ 昨日高光 ============ */}
      {data.highlight && (
        <section className="px-5 mt-6 animate-rise" style={{ animationDelay: '.4s' }}>
          <div className="paper-card p-5 relative">
            <div className="tape" style={{ left: '24px' }} />
            <div className="flex items-center gap-2">
              <span className="deco-stamp text-ember-600 dark:text-ember-300 text-[10px]">HIGHLIGHT · 昨日高光</span>
            </div>
            <p className="text-[11px] font-mono text-ink-soft dark:text-violet-300/60 mt-1.5">你的这一句，我想裱起来</p>

            <div className="mt-4 space-y-3">
              {data.highlight.their_words && (
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 rounded-full bg-ink text-white grid place-items-center text-[11px] font-display shrink-0">对</div>
                  <div className="max-w-[85%] px-3 py-2 rounded-[16px] rounded-tl-sm bg-violet-500/8 dark:bg-white/5 border border-violet-500/15 text-[12.5px] leading-relaxed">
                    {data.highlight.their_words}
                  </div>
                </div>
              )}
              <div className="flex items-start gap-2 justify-end">
                <div className="max-w-[85%] px-3 py-2 rounded-[16px] rounded-tr-sm bg-gradient-to-br from-violet-500 to-violet-600 text-white text-[12.5px] leading-relaxed shadow-md">
                  {data.highlight.my_response}
                </div>
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-ember-500 text-white grid place-items-center text-[11px] font-display shrink-0">
                  {username.slice(0, 1)}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-dashed border-violet-500/25">
              <div className="grid grid-cols-4 gap-2 text-center">
                <div>
                  <div className="font-display text-[18px] text-violet-600 dark:text-violet-300">{data.highlight.scores.decency ?? '-'}</div>
                  <div className="text-[9.5px] text-ink-soft dark:text-violet-300/60">得体</div>
                </div>
                <div>
                  <div className="font-display text-[18px] text-violet-600 dark:text-violet-300">{data.highlight.scores.defusion ?? '-'}</div>
                  <div className="text-[9.5px] text-ink-soft dark:text-violet-300/60">化解</div>
                </div>
                <div>
                  <div className="font-display text-[18px] text-ember-500">{data.highlight.scores.humor ?? '-'}</div>
                  <div className="text-[9.5px] text-ink-soft dark:text-violet-300/60">幽默</div>
                </div>
                <div>
                  <div className="font-display text-[18px] text-ember-500">{data.highlight.scores.style_match ?? '-'}</div>
                  <div className="text-[9.5px] text-ink-soft dark:text-violet-300/60">风格</div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className="match-chip ink">最像 {data.highlight.top_style_name}</span>
                <button onClick={() => navigate('/skills')} className="text-[11px] text-violet-600 dark:text-violet-300">完整对话 →</button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ============ 探索更多三联 ============ */}
      <section className="px-5 mt-6 animate-rise" style={{ animationDelay: '.46s' }}>
        <div className="font-display text-[10.5px] tracking-[.3em] text-violet-600 dark:text-violet-300 mb-3">EXPLORE · 探索更多</div>
        <div className="grid grid-cols-1 gap-3">
          <button
            onClick={() => navigate('/diary')}
            className="paper-card p-4 flex items-center gap-3 text-left active:translate-y-[-2px] transition"
          >
            <div className="w-11 h-11 rounded-xl bg-violet-500/10 grid place-items-center shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 4h12l4 4v12a2 2 0 0 1-2 2H4zM14 4v6h6" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display text-[15px]">真实场景日记</div>
              <div className="text-[11.5px] text-ink-soft dark:text-violet-300/60 mt-0.5">今天遇到的对话——我帮你拆，顺便做成明天的题</div>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-violet-500 shrink-0">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </button>

          <button
            onClick={async () => {
              try {
                const skills = await api.skills()
                if (skills.length > 0) {
                  const random = skills[Math.floor(Math.random() * skills.length)]
                  navigate(`/practice/${random.id}`)
                  return
                }
              } catch { /* ignore */ }
              navigate('/skills')
            }}
            className="paper-card p-4 flex items-center gap-3 text-left active:translate-y-[-2px] transition"
          >
            <div className="w-11 h-11 rounded-xl bg-ember-500/10 grid place-items-center shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12c0 4-4 7-9 7-1.5 0-3-.3-4.3-.8L3 20l1.8-4.7C3.7 13.9 3 12 3 10c0-4 4-7 9-7s9 3 9 7z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display text-[15px]">自由对练</div>
              <div className="text-[11.5px] text-ink-soft dark:text-violet-300/60 mt-0.5">选个对手定个场合，8 轮内见真章</div>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-ember-500 shrink-0">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </button>

          <button
            onClick={() => navigate('/skills')}
            className="paper-card p-4 flex items-center gap-3 text-left active:translate-y-[-2px] transition"
          >
            <div className="w-11 h-11 rounded-xl bg-ink/10 dark:bg-white/5 grid place-items-center shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#1E1B4B" className="dark:fill-violet-300">
                <path d="M12 2 L14 9 L21 11 L14 13 L12 20 L10 13 L3 11 L10 9 Z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display text-[15px]">技能树全景</div>
              <div className="text-[11.5px] text-ink-soft dark:text-violet-300/60 mt-0.5">7 大类 · {data.skills.total} 技能 · 5 级熟练度</div>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-ink dark:text-violet-300 shrink-0">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </button>
        </div>
      </section>

      {/* ============ Footer ============ */}
      <footer className="px-5 pt-8 pb-4 text-center text-[10.5px] text-ink-soft dark:text-violet-300/45 font-mono leading-relaxed">
        EQ Trainer · v0.1.0 · by 穆<br />
        <span className="text-ember-500">每天 10 分钟 · 练成想得到的那种人</span>
      </footer>
    </div>
  )
}
