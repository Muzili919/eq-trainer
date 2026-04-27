import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { AccountEntry, getAccounts, saveToken, saveUsername, upsertAccount } from '../lib/utils'

const ROLE_OPTIONS = [
  { value: 'decoration_boss', label: '装修公司老板', hint: '客户、工头、供应商' },
  { value: 'property_manager', label: '物业项目经理', hint: '甲方、业主、保安保洁' },
  { value: 'general', label: '通用', hint: '家庭 + 朋友圈场景' },
]

export default function LoginPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const isAdding = params.get('add') === '1'

  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('general')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [knownAccounts, setKnownAccounts] = useState<AccountEntry[]>([])

  useEffect(() => {
    setKnownAccounts(getAccounts())
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!username.trim() || !password.trim()) { setError('请填写用户名和密码'); return }
    setLoading(true); setError('')
    try {
      let access_token: string
      let resolvedRole = role

      if (mode === 'login') {
        const res = await api.login(username.trim(), password)
        access_token = res.access_token
        // Fetch role from server
        saveToken(access_token)
        try {
          const me = await api.me()
          resolvedRole = me.target_role
        } catch { /* use default */ }
      } else {
        const res = await api.register(username.trim(), password, role)
        access_token = res.access_token
      }

      saveToken(access_token)
      saveUsername(username.trim())
      upsertAccount({ username: username.trim(), token: access_token, role: resolvedRole, last_seen: Date.now() })
      navigate('/', { replace: true })
    } catch (err: any) {
      setError(err.message ?? '出错了，再试一次')
    } finally {
      setLoading(false)
    }
  }

  async function quickSwitch(acc: AccountEntry) {
    saveToken(acc.token)
    saveUsername(acc.username)
    upsertAccount({ ...acc, last_seen: Date.now() })
    try {
      await api.me()
      navigate('/', { replace: true })
    } catch {
      localStorage.removeItem('eq_token')
      localStorage.removeItem('eq_username')
      setError('登录已过期，请重新登录')
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-12">
      {/* Mascot */}
      <div className="relative mb-6 animate-float">
        <svg className="absolute -top-2 -right-2 animate-twinkle" width="16" height="16" viewBox="0 0 24 24" fill="#F97316">
          <path d="M12 0 14 10 24 12 14 14 12 24 10 14 0 12 10 10z"/>
        </svg>
        <svg className="absolute -bottom-1 left-1 animate-twinkle" style={{animationDelay:'1s'}} width="10" height="10" viewBox="0 0 24 24" fill="#7C3AED">
          <path d="M12 0 14 10 24 12 14 14 12 24 10 14 0 12 10 10z"/>
        </svg>
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-violet-500/15 to-ember-500/10 flex items-center justify-center text-5xl">
          🦭
        </div>
      </div>

      <h1 className="font-display text-[28px] tracking-wide text-center mb-1">EQ Trainer</h1>
      <p className="text-[13px] text-ink-soft dark:text-violet-300/60 font-mono tracking-widest mb-8">
        {isAdding ? '添加另一个账号' : '高情商沟通练习场'}
      </p>

      {/* 已知账号快捷切换（非添加模式时显示） */}
      {!isAdding && knownAccounts.length > 0 && (
        <div className="w-full max-w-sm mb-4 space-y-2">
          <p className="text-[11px] text-ink-soft/60 dark:text-violet-300/40 font-mono text-center tracking-widest mb-2">快速切换</p>
          {knownAccounts.map(acc => (
            <button key={acc.username} onClick={() => quickSwitch(acc)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl border border-violet-500/20 bg-white dark:bg-night-card active:scale-[.98] transition-transform">
              <span className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-ember-500 grid place-items-center text-white font-display text-[13px] shadow shrink-0">
                {acc.username.slice(0, 1)}
              </span>
              <div className="text-left">
                <div className="font-display text-[13px] tracking-wide">{acc.username}</div>
                <div className="text-[10px] text-ink-soft dark:text-violet-300/50 tracking-widest">
                  {{ decoration_boss: '装修老板', property_manager: '物业经理', general: '通用' }[acc.role] ?? ''}
                </div>
              </div>
              <svg className="ml-auto text-violet-500/50" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          ))}
          <div className="flex items-center gap-3 my-3">
            <div className="flex-1 h-px bg-violet-500/10" />
            <span className="text-[10px] text-ink-soft/50 font-mono tracking-widest">或登录其他账号</span>
            <div className="flex-1 h-px bg-violet-500/10" />
          </div>
        </div>
      )}

      <form onSubmit={submit} className="paper-card w-full max-w-sm p-6 space-y-4">
        <div className="flex gap-2 p-1 rounded-xl bg-violet-500/8 dark:bg-violet-500/10 mb-2">
          {(['login', 'register'] as const).map(m => (
            <button key={m} type="button"
              onClick={() => { setMode(m); setError('') }}
              className={`flex-1 py-1.5 rounded-lg font-display text-[12px] tracking-widest transition-all
                ${mode === m ? 'bg-white dark:bg-night-card shadow text-violet-600 dark:text-violet-300' : 'text-ink-soft dark:text-violet-300/60'}`}>
              {m === 'login' ? '登录' : '注册'}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <input
            className="text-input w-full"
            placeholder="用户名"
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoComplete="username"
          />
          <input
            className="text-input w-full"
            type="password"
            placeholder="密码"
            value={password}
            onChange={e => setPassword(e.target.value)}
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          />
        </div>

        {/* 注册时显示角色选择 */}
        {mode === 'register' && (
          <div className="space-y-2">
            <p className="text-[11px] text-ink-soft dark:text-violet-300/50 tracking-widest font-mono">选择你的主要场景</p>
            {ROLE_OPTIONS.map(opt => (
              <label key={opt.value}
                className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all
                  ${role === opt.value
                    ? 'border-violet-500/60 bg-violet-500/6'
                    : 'border-violet-500/15 hover:border-violet-500/30'}`}>
                <input type="radio" className="sr-only" name="role" value={opt.value}
                  checked={role === opt.value} onChange={() => setRole(opt.value)} />
                <div className={`w-4 h-4 rounded-full border-2 grid place-items-center shrink-0 transition-all
                  ${role === opt.value ? 'border-violet-500' : 'border-ink-soft/30'}`}>
                  {role === opt.value && <div className="w-2 h-2 rounded-full bg-violet-500" />}
                </div>
                <div>
                  <div className="text-[13px] font-display tracking-wide">{opt.label}</div>
                  <div className="text-[10px] text-ink-soft dark:text-violet-300/50 tracking-widest">{opt.hint}</div>
                </div>
              </label>
            ))}
          </div>
        )}

        {error && (
          <p className="text-[12px] text-ember-600 dark:text-ember-300 text-center">{error}</p>
        )}

        <button type="submit" disabled={loading}
          className="w-full py-3 rounded-2xl font-display text-[13px] tracking-widest
            bg-gradient-to-r from-violet-500 to-violet-600 text-white
            shadow-[0_8px_20px_-6px_rgba(124,58,237,.55)]
            active:scale-[.98] transition-transform disabled:opacity-60">
          {loading ? '请稍候…' : mode === 'login' ? '进入练习场' : '创建账号'}
        </button>
      </form>

      <p className="mt-6 text-[11px] text-ink-soft/60 dark:text-violet-300/40 font-mono text-center">
        STAR SEA · 星海 在等你
      </p>
    </div>
  )
}
