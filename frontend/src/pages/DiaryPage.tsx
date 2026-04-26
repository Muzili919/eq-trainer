import { useState } from 'react'
import { api, DiaryResp } from '../lib/api'

type Step = 'form' | 'loading' | 'result'

export default function DiaryPage() {
  const [step, setStep] = useState<Step>('form')
  const [form, setForm] = useState({ context: '', other_party: '', their_words: '', my_response: '', outcome: '' })
  const [result, setResult] = useState<DiaryResp | null>(null)
  const [rewrite, setRewrite] = useState<string | null>(null)
  const [loadingRewrite, setLoadingRewrite] = useState(false)
  const [error, setError] = useState('')

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.their_words.trim() || !form.my_response.trim()) {
      setError('至少填写"对方说了什么"和"你是怎么回的"')
      return
    }
    setStep('loading')
    try {
      const res = await api.createDiary({
        context: form.context || '日常对话',
        other_party: form.other_party || '对方',
        their_words: form.their_words,
        my_response: form.my_response,
        outcome: form.outcome || '未记录',
      })
      setResult(res)
      setStep('result')
    } catch (err: any) {
      setError(err.message ?? '提交失败，再试一次')
      setStep('form')
    }
  }

  async function fetchRewrite() {
    if (!result) return
    setLoadingRewrite(true)
    try {
      const { rewrite_suggestion } = await api.getRewrite(result.diary_id)
      setRewrite(rewrite_suggestion)
    } catch {
      setRewrite('暂时无法获取改写示范')
    } finally {
      setLoadingRewrite(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="px-5 pt-5 pb-3">
        <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300">DIARY</div>
        <h1 className="font-display text-[22px] mt-0.5">真实场景日记</h1>
        <p className="text-[12px] text-ink-soft dark:text-violet-300/60 mt-1">把今天发生的对话记下来，星海帮你复盘</p>
      </header>

      {step === 'form' && (
        <form onSubmit={submit} className="px-5 space-y-4 pb-6 animate-rise">
          <Field label="场景背景（可选）" placeholder="在哪里发生的？什么情况？" value={form.context} onChange={v => setForm(f => ({...f, context: v}))} />
          <Field label="对方是谁（可选）" placeholder="朋友、同事、家人…" value={form.other_party} onChange={v => setForm(f => ({...f, other_party: v}))} />
          <Field label="对方说了什么 *" placeholder="把对方原话（或大意）写下来" value={form.their_words} onChange={v => setForm(f => ({...f, their_words: v}))} multiline />
          <Field label="你是怎么回的 *" placeholder="你当时说了什么" value={form.my_response} onChange={v => setForm(f => ({...f, my_response: v}))} multiline />
          <Field label="结果如何（可选）" placeholder="气氛怎么了？对方什么反应？" value={form.outcome} onChange={v => setForm(f => ({...f, outcome: v}))} />
          {error && <p className="text-[12px] text-ember-600 dark:text-ember-300">{error}</p>}
          <button type="submit"
            className="w-full py-3.5 rounded-2xl font-display text-[13px] tracking-widest bg-gradient-to-r from-violet-500 to-violet-600 text-white shadow-[0_8px_20px_-6px_rgba(124,58,237,.5)] active:scale-[.98] transition-transform">
            提交给星海复盘
          </button>
        </form>
      )}

      {step === 'loading' && (
        <div className="flex flex-col items-center justify-center py-24 gap-4 animate-rise">
          <div className="text-5xl animate-float">🦭</div>
          <p className="font-display text-[14px] tracking-widest text-violet-500">星海思考中…</p>
        </div>
      )}

      {step === 'result' && result && (
        <div className="px-5 space-y-4 pb-6 animate-rise">
          {/* Identified skills */}
          <div className="paper-card p-4">
            <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300 mb-3">识别到的技能缺口</div>
            <div className="flex flex-wrap gap-2">
              {result.identified_skills.map(s => (
                <span key={s} className="skill-badge">{s}</span>
              ))}
              {result.identified_skills.length === 0 && <span className="text-[12px] text-ink-soft">暂无（说明你做得还不错）</span>}
            </div>
          </div>

          {/* Diagnosis */}
          <div className="paper-card p-4">
            <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300 mb-2">星海的观察</div>
            <p className="text-[13px] leading-relaxed">{result.diagnosis_brief}</p>
          </div>

          {/* Socratic questions */}
          <div className="paper-card p-4 space-y-3">
            <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300">反思问题</div>
            {result.socratic_questions.map((q, i) => (
              <div key={i} className="flex gap-3 text-[13px] leading-relaxed">
                <span className="font-display text-violet-500 shrink-0 text-[15px]">{i+1}.</span>
                <span>{q}</span>
              </div>
            ))}
          </div>

          {/* Rewrite */}
          {rewrite ? (
            <div className="paper-card p-4 border-dashed border-violet-500/40">
              <div className="font-display text-[10px] tracking-[.3em] text-violet-600 dark:text-violet-300 mb-2">改写示范</div>
              <p className="text-[13px] leading-relaxed italic">{rewrite}</p>
            </div>
          ) : (
            <button onClick={fetchRewrite} disabled={loadingRewrite}
              className="w-full py-3 rounded-2xl font-display text-[12px] tracking-widest border border-dashed border-violet-500/50 text-violet-500 dark:text-violet-300 active:scale-[.98] transition disabled:opacity-60">
              {loadingRewrite ? '生成中…' : '我想看看怎么说更好'}
            </button>
          )}

          <button onClick={() => { setStep('form'); setForm({context:'',other_party:'',their_words:'',my_response:'',outcome:''}); setResult(null); setRewrite(null) }}
            className="w-full py-3 rounded-2xl font-display text-[12px] tracking-widest bg-gradient-to-r from-violet-500 to-violet-600 text-white shadow-[0_8px_20px_-6px_rgba(124,58,237,.5)]">
            再记一条
          </button>
        </div>
      )}
    </div>
  )
}

function Field({ label, placeholder, value, onChange, multiline }: {
  label: string; placeholder: string; value: string;
  onChange: (v: string) => void; multiline?: boolean
}) {
  const cls = "text-input w-full"
  return (
    <div>
      <label className="block text-[11.5px] font-display tracking-widest text-ink-soft dark:text-violet-300/70 mb-1.5">{label}</label>
      {multiline ? (
        <textarea className={cls} placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)} rows={3} style={{borderRadius:16, resize:'none'}} />
      ) : (
        <input className={cls} placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)} />
      )}
    </div>
  )
}
