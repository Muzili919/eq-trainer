import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api, StartPracticeResp, TurnResp } from '../lib/api'

interface Message {
  from: 'them' | 'me' | 'socratic'
  text: string
  emotion?: string
  responseMs?: number
}

const SCORE_LABELS: Record<string, string> = {
  decency: '得体度', defusion: '化解力', humor: '幽默指数', style_match: '风格匹配',
}

function speedLabel(ms: number): { icon: string; label: string; color: string } {
  const s = ms / 1000
  if (s < 3)   return { icon: '⚡', label: `${s.toFixed(1)}s 抢答`, color: 'text-amber-500' }
  if (s <= 15)  return { icon: '✨', label: `${s.toFixed(1)}s 自然`, color: 'text-violet-500' }
  if (s <= 30)  return { icon: '🤔', label: `${s.toFixed(1)}s 推敲`, color: 'text-ink-soft dark:text-violet-300/60' }
  return { icon: '🐢', label: `${s.toFixed(1)}s 卡壳`, color: 'text-ember-500' }
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-[11.5px] mb-1">
        <span className="text-ink-soft dark:text-violet-300/70">{label}</span>
        <span className="font-mono text-violet-600 dark:text-violet-300">{value}</span>
      </div>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

// ── TTS hook ──────────────────────────────────────────────────────────────
function useTTS() {
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window

  const speak = useCallback((text: string) => {
    if (!supported) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'zh-CN'
    u.rate = 1.05
    // prefer a Chinese voice if available
    const voices = window.speechSynthesis.getVoices()
    const zh = voices.find(v => v.lang.startsWith('zh'))
    if (zh) u.voice = zh
    window.speechSynthesis.speak(u)
  }, [supported])

  const stop = useCallback(() => {
    if (supported) window.speechSynthesis.cancel()
  }, [supported])

  return { speak, stop, supported }
}

// ── Speech input hook ─────────────────────────────────────────────────────
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

function useSpeechInput(onResult: (text: string) => void) {
  const recogRef = useRef<SpeechRecognition | null>(null)
  const [recording, setRecording] = useState(false)
  const supported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const startRecording = useCallback(() => {
    if (!supported) return
    const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition
    const r = new SR()
    r.lang = 'zh-CN'
    r.continuous = false
    r.interimResults = false
    r.onresult = (e) => {
      const text = e.results[0]?.[0]?.transcript ?? ''
      if (text) onResult(text)
    }
    r.onend = () => setRecording(false)
    r.onerror = () => setRecording(false)
    recogRef.current = r
    r.start()
    setRecording(true)
  }, [supported, onResult])

  const stopRecording = useCallback(() => {
    recogRef.current?.stop()
    setRecording(false)
  }, [])

  return { recording, supported, startRecording, stopRecording }
}

// ── Countdown ring component ──────────────────────────────────────────────
function CountdownRing({ elapsed, limit = 30 }: { elapsed: number; limit?: number }) {
  const remaining = Math.max(limit - elapsed, 0)
  const pct = Math.min(elapsed / limit, 1)
  const r = 16, circ = 2 * Math.PI * r
  const dash = circ * (1 - pct)
  const urgent = remaining < 5
  const color = remaining > 15 ? '#7C3AED' : remaining > 5 ? '#F97316' : '#EF4444'

  return (
    <div className={`relative w-10 h-10 flex items-center justify-center ${urgent ? 'animate-pulse' : ''}`}>
      <svg width="40" height="40" viewBox="0 0 40 40" className="-rotate-90">
        <circle cx="20" cy="20" r={r} fill="none" stroke="rgba(124,58,237,.12)" strokeWidth="3"/>
        <circle cx="20" cy="20" r={r} fill="none" stroke={color} strokeWidth="3"
          strokeDasharray={circ} strokeDashoffset={dash}
          strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.2s, stroke 0.5s' }}/>
      </svg>
      <span className="absolute font-mono text-[11px]" style={{ color }}>
        {Math.ceil(remaining)}
      </span>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────
export default function PracticePage() {
  const { skillId } = useParams<{ skillId: string }>()
  const [searchParams] = useSearchParams()
  const templateIdParam = searchParams.get('template')
  const templateId = templateIdParam ? parseInt(templateIdParam, 10) : undefined
  const diaryIdParam = searchParams.get('diary')
  const diaryId = diaryIdParam ? parseInt(diaryIdParam, 10) : undefined
  const navigate = useNavigate()

  const [scenario, setScenario] = useState<StartPracticeResp | null>(null)
  const [phase, setPhase] = useState<'loading' | 'intro' | 'chat'>('loading')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [sheet, setSheet] = useState<{ resp: TurnResp; responseMs: number } | null>(null)
  const [ended, setEnded] = useState(false)
  const [practiceId, setPracticeId] = useState<number | null>(null)
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('voice')

  // timer
  const [timerActive, setTimerActive] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  const bottomRef = useRef<HTMLDivElement>(null)
  const { speak, stop: stopTTS } = useTTS()

  const { recording, supported: voiceSupported, startRecording, stopRecording } =
    useSpeechInput((text) => setInput(prev => prev ? prev + ' ' + text : text))

  // load scenario
  useEffect(() => {
    if (!skillId) return
    api.startPractice(skillId, undefined, templateId, diaryId).then(s => {
      setScenario(s)
      setPracticeId(s.practice_id)
      setPhase('intro')
    }).catch(() => navigate(-1))
  }, [skillId])

  // auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // timer tick
  useEffect(() => {
    if (timerActive) {
      startTimeRef.current = Date.now()
      setElapsed(0)
      timerRef.current = setInterval(() => {
        setElapsed((Date.now() - startTimeRef.current) / 1000)
      }, 100)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [timerActive])

  function startChat() {
    if (!scenario) return
    setPhase('chat')
    const msg: Message = { from: 'them', text: scenario.initial_message, emotion: scenario.ai_emotion }
    setMessages([msg])
    speak(scenario.initial_message)
    // start timer after TTS has a moment to begin
    setTimeout(() => setTimerActive(true), 400)
  }

  async function send(text?: string) {
    const userText = (text ?? input).trim()
    if (!userText || !practiceId || sending) return

    // capture elapsed time
    const responseMs = timerActive ? Math.round((Date.now() - startTimeRef.current)) : 0
    setTimerActive(false)
    stopTTS()
    setInput('')
    setSending(true)
    setMessages(m => [...m, { from: 'me', text: userText, responseMs }])

    try {
      const resp = await api.submitTurn(practiceId, userText)
      const newMsgs: Message[] = []
      if (resp.socratic_question) {
        newMsgs.push({ from: 'socratic', text: resp.socratic_question })
      }
      newMsgs.push({ from: 'them', text: resp.ai_message, emotion: resp.ai_emotion })
      setMessages(m => [...m, ...newMsgs])
      setSheet({ resp, responseMs })

      if (!resp.should_end && resp.turn_number < 8) {
        speak(resp.ai_message)
        setTimeout(() => setTimerActive(true), 400)
      } else {
        setEnded(true)
      }
    } catch (err: any) {
      setMessages(m => [...m, { from: 'socratic', text: `出错了：${err.message}` }])
      setTimerActive(true)
    } finally {
      setSending(false)
    }
  }

  function handleVoiceRelease() {
    stopRecording()
    // give STT a moment to fire onresult before we send
    setTimeout(() => {
      setInput(prev => {
        if (prev.trim()) send(prev.trim())
        return ''
      })
    }, 300)
  }

  async function finish() {
    if (!practiceId) return
    try { await api.completePractice(practiceId) } finally {
      navigate('/', { replace: true })
    }
  }

  // ── Loading ──
  if (phase === 'loading') return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-3">
        <div className="text-4xl animate-float">🦭</div>
        <p className="font-display text-[14px] tracking-widest text-violet-500">星海出题中…</p>
      </div>
    </div>
  )

  // ── Intro card ──
  if (phase === 'intro' && scenario) return (
    <div className="min-h-screen flex flex-col items-center justify-center px-5 py-10">
      <div className="w-full max-w-[440px] space-y-5 animate-rise">
        <div className="text-center">
          <span className="skill-badge primary">{skillId}</span>
          <h2 className="font-display text-[22px] mt-3">{scenario.title}</h2>
        </div>

        <div className="paper-card p-5 text-[13.5px] leading-relaxed relative overflow-hidden">
          <div className="tape" style={{ left: '50%', transform: 'translateX(-50%) rotate(-3deg)' }} />
          <p className="mt-1">{scenario.scenario_setup}</p>
        </div>

        <div className="paper-card p-4 border-dashed border-violet-500/40">
          <div className="text-[10px] font-mono tracking-widest text-violet-500 mb-2">规则</div>
          <ul className="space-y-1.5 text-[12.5px] text-ink-soft dark:text-violet-300/70">
            <li>⚡️ AI 说完立刻开始计时，越快回复加分越多</li>
            <li>🎤 默认语音模式，按住说话松开自动发送</li>
            <li>✏️ 点麦克风图标可切换到文字输入</li>
            <li>⭐ 4-6 轮后练习结束，查看综合评分</li>
          </ul>
        </div>

        <button onClick={startChat}
          className="w-full py-4 rounded-2xl font-display text-[14px] tracking-widest
            bg-gradient-to-r from-violet-500 to-violet-600 text-white
            shadow-[0_10px_28px_-8px_rgba(124,58,237,.6)] active:scale-[.98] transition-transform">
          开始练习
        </button>
      </div>
    </div>
  )

  // ── Chat ──
  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="sticky top-0 z-30 backdrop-blur-md bg-paper/88 dark:bg-night-deeper/85
        border-b border-violet-500/10 px-4 py-2.5 flex items-center gap-3 max-w-[480px] mx-auto">
        <button onClick={() => navigate(-1)} className="icon-btn w-8 h-8">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
        <div className="flex-1 min-w-0">
          <div className="font-display text-[13px] tracking-wide truncate">{scenario?.title}</div>
          <div className="text-[10px] font-mono text-ink-soft dark:text-violet-300/60 tracking-widest">{skillId}</div>
        </div>

        {/* Timer ring */}
        {timerActive && !ended && (
          <CountdownRing elapsed={elapsed} />
        )}

        {ended && (
          <button onClick={finish}
            className="px-3 py-1.5 rounded-xl font-display text-[11px] tracking-widest
              bg-gradient-to-r from-violet-500 to-violet-600 text-white">
            完成
          </button>
        )}
      </div>

      {/* Chat stream */}
      <div className="max-w-[480px] mx-auto px-4 pt-3 pb-36 space-y-4">
        {messages.map((msg, i) => (
          <div key={i}
            className={`flex ${msg.from === 'me' ? 'justify-end' : 'justify-start'} animate-rise`}
            style={{ animationDelay: `${Math.min(i * .04, .3)}s` }}>
            {msg.from === 'socratic' ? (
              <div className="bubble-socratic">{msg.text}</div>
            ) : msg.from === 'them' ? (
              <div className="space-y-1.5 max-w-[85%]">
                {msg.emotion && (
                  <div className="flex items-center gap-2 text-[11px] text-ink-soft dark:text-violet-300/60 pl-1">
                    <span className="w-5 h-5 rounded-full bg-ink/80 dark:bg-night-card flex items-center justify-center text-white font-display text-[9px]">AI</span>
                    <span className="px-2 py-0.5 rounded-full bg-ember-500/12 text-ember-600 dark:text-ember-300 font-display text-[10px]">{msg.emotion}</span>
                  </div>
                )}
                <div className="bubble-them">{msg.text}</div>
              </div>
            ) : (
              <div className="space-y-1">
                <div className="bubble-me">{msg.text}</div>
                {msg.responseMs !== undefined && msg.responseMs > 0 && (
                  <div className={`text-right text-[10.5px] font-mono pr-1 ${speedLabel(msg.responseMs).color}`}>
                    {speedLabel(msg.responseMs).icon} {speedLabel(msg.responseMs).label}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex justify-start">
            <div className="bubble-them flex gap-1 items-center px-4 py-3">
              {[0,1,2].map(i => (
                <span key={i} className="w-1.5 h-1.5 rounded-full bg-violet-500/40 animate-wave-jump"
                  style={{ animationDelay: `${i * .15}s` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input dock */}
      {!ended && (
        <div className="input-dock">
          <div className="flex gap-2 items-center max-w-[480px] mx-auto">
            {/* Mode toggle */}
            <button onClick={() => setInputMode(m => m === 'text' ? 'voice' : 'text')}
              className="icon-btn flex-shrink-0" title={inputMode === 'text' ? '切换语音' : '切换文字'}>
              {inputMode === 'voice' ? (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/>
                  <line x1="12" y1="4" x2="12" y2="20"/>
                </svg>
              ) : (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
                </svg>
              )}
            </button>

            {inputMode === 'voice' ? (
              /* ── Voice mode ── */
              <button
                className={`flex-1 h-[46px] rounded-full font-display text-[13px] tracking-widest
                  flex items-center justify-center gap-2 select-none transition-all
                  ${recording
                    ? 'bg-gradient-to-r from-ember-500 to-ember-600 text-white shadow-[0_8px_24px_-6px_rgba(249,115,22,.65)]'
                    : timerActive
                      ? 'bg-gradient-to-r from-violet-500/15 to-ember-500/10 border-2 border-violet-500/60 text-violet-600 dark:text-violet-300'
                      : 'bg-violet-500/8 border border-dashed border-violet-500/35 text-violet-500/70 dark:text-violet-300/60'
                  }`}
                onPointerDown={(e) => {
                  e.currentTarget.setPointerCapture(e.pointerId)
                  stopTTS()
                  setTimerActive(false)
                  startRecording()
                }}
                onPointerUp={handleVoiceRelease}
                onPointerCancel={() => { stopRecording(); setTimerActive(false) }}
              >
                {recording ? (
                  <>
                    <span className="flex gap-[3px] items-center h-4">
                      {[40,70,100,70,40,80,50].map((h, i) => (
                        <span key={i} className="w-[2.5px] bg-white rounded-full animate-wave-jump"
                          style={{ height: `${h}%`, animationDelay: `${i * .08}s` }} />
                      ))}
                    </span>
                    <span>松开发送</span>
                  </>
                ) : (
                  <>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
                    </svg>
                    <span>{timerActive ? '按住说话' : '等待 AI 出招'}</span>
                  </>
                )}
              </button>
            ) : (
              /* ── Text mode ── */
              <>
                <textarea
                  className="text-input resize-none leading-relaxed py-2.5 flex-1"
                  placeholder="你想怎么回应…"
                  rows={1}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
                  style={{ minHeight: 42, maxHeight: 100 }}
                  autoFocus
                />
                <button onClick={() => send()} disabled={!input.trim() || sending}
                  className="icon-btn send flex-shrink-0 disabled:opacity-50">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2 21L23 12 2 3v7l15 2-15 2v7z"/>
                  </svg>
                </button>
              </>
            )}
          </div>

          {/* Transcription preview */}
          {inputMode === 'voice' && input && !recording && (
            <div className="mt-2 mx-auto max-w-[480px] flex items-center gap-2 px-1">
              <span className="text-[12px] text-ink-soft dark:text-violet-300/70 flex-1 truncate">"{input}"</span>
              <button onClick={() => send()} className="font-display text-[11px] tracking-widest text-violet-500 dark:text-violet-300">发送</button>
              <button onClick={() => setInput('')} className="font-display text-[11px] tracking-widest text-ember-500">清除</button>
            </div>
          )}
        </div>
      )}

      {/* Score sheet */}
      {sheet && (
        <div className="scrim" onClick={() => setSheet(null)}>
          <div className="sheet" onClick={e => e.stopPropagation()}>
            {/* Narrative — 主角 */}
            {sheet.resp.narrative && (
              <div className="mb-4 p-4 rounded-xl bg-gradient-to-br from-violet-500/8 to-ember-500/8 dark:from-violet-500/12 dark:to-ember-500/12">
                <p className="text-[14px] leading-relaxed">{sheet.resp.narrative}</p>
              </div>
            )}

            {/* Score + speed + skills */}
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300">SCORE</div>
                <div className="font-display text-[28px] leading-none mt-0.5">
                  {sheet.resp.total_score}
                  <span className="text-[12px] text-ink-soft dark:text-violet-300/60 ml-1">/ 100</span>
                </div>
              </div>
              <div className="text-right space-y-1.5">
                {sheet.responseMs > 0 && (() => {
                  const sp = speedLabel(sheet.responseMs)
                  return (
                    <div className={`font-mono text-[11px] ${sp.color}`}>
                      {sp.icon} {sp.label}
                    </div>
                  )
                })()}
                <div className="flex gap-1 flex-wrap justify-end">
                  {sheet.resp.well_used.map(s => <span key={s} className="skill-badge primary text-[9px] px-2 py-0.5">{s}</span>)}
                </div>
                {sheet.resp.missing.length > 0 && (
                  <div className="flex gap-1 flex-wrap justify-end">
                    {sheet.resp.missing.map(s => <span key={s} className="skill-badge text-[9px] px-2 py-0.5">{s}</span>)}
                  </div>
                )}
              </div>
            </div>

            {/* Score bars — 缩小显示 */}
            <div className="space-y-2 mb-3 opacity-70">
              {Object.entries(sheet.resp.scores).map(([k, v]) => (
                <ScoreBar key={k} label={SCORE_LABELS[k] ?? k} value={v} />
              ))}
            </div>

            {/* Rewrite */}
            {sheet.resp.rewrite_suggestion && (
              <div className="mb-3 p-3 rounded-xl border border-dashed border-violet-500/30">
                <div className="font-display text-[10px] tracking-widest text-ink-soft dark:text-violet-300/70 mb-1">改写示范</div>
                <p className="text-[12.5px] leading-relaxed italic">{sheet.resp.rewrite_suggestion}</p>
              </div>
            )}

            <button onClick={() => setSheet(null)}
              className="w-full mt-1 py-3 rounded-2xl font-display text-[12px] tracking-widest
                bg-gradient-to-r from-violet-500 to-violet-600 text-white
                shadow-[0_8px_20px_-6px_rgba(124,58,237,.5)]">
              继续对话
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
