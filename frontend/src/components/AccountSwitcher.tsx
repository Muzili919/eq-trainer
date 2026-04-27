import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AccountEntry, activateAccount, getAccounts, getActiveAccount, logoutAll, removeAccount } from '../lib/utils'

const ROLE_LABEL: Record<string, string> = {
  decoration_boss: '装修老板',
  property_manager: '物业经理',
  general: '通用',
}

function AvatarCircle({ name, size = 'md' }: { name: string; size?: 'sm' | 'md' }) {
  const sz = size === 'sm' ? 'w-7 h-7 text-[11px]' : 'w-9 h-9 text-[13px]'
  return (
    <span className={`${sz} rounded-full bg-gradient-to-br from-violet-500 to-ember-500 grid place-items-center text-white font-display shadow ring-2 ring-white dark:ring-night-card shrink-0`}>
      {name.slice(0, 1)}
    </span>
  )
}

export default function AccountSwitcher() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [accounts, setAccounts] = useState<AccountEntry[]>([])
  const active = getActiveAccount()
  const ref = useRef<HTMLDivElement>(null)
  const username = active?.username ?? '朋友'

  useEffect(() => {
    setAccounts(getAccounts())
  }, [open])

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    if (open) document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [open])

  function switchTo(acc: AccountEntry) {
    // 先清旧 token，避免 reload 期间 inflight 请求带错 token
    localStorage.removeItem('eq_token')
    activateAccount(acc.username)
    setOpen(false)
    window.location.reload()
  }

  function addAccount() {
    setOpen(false)
    navigate('/login?add=1')
  }

  function logout() {
    const others = accounts.filter(a => a.username !== active?.username)
    if (active) removeAccount(active.username)
    if (others.length > 0) {
      activateAccount(others[0].username)
      window.location.reload()
    } else {
      logoutAll()
      navigate('/login', { replace: true })
    }
  }

  const others = accounts.filter(a => a.username !== active?.username)

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(v => !v)}
        className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-ember-500 grid place-items-center text-white font-display text-[13px] shadow ring-2 ring-white dark:ring-night-card active:scale-95 transition"
        aria-label="账号"
      >
        {username.slice(0, 1)}
      </button>

      {open && (
        <div className="absolute right-0 top-11 w-56 rounded-2xl bg-white dark:bg-night-card border border-violet-500/15 shadow-xl z-50 overflow-hidden animate-rise" style={{ animationDuration: '0.15s' }}>
          {/* 当前账号 */}
          <div className="px-4 py-3 border-b border-violet-500/10">
            <div className="flex items-center gap-2.5">
              <AvatarCircle name={username} />
              <div className="min-w-0">
                <div className="font-display text-[13px] tracking-wide truncate">{username}</div>
                <div className="text-[10px] text-ink-soft dark:text-violet-300/50 tracking-widest">{ROLE_LABEL[active?.role ?? 'general']}</div>
              </div>
              <svg className="ml-auto shrink-0 text-violet-500" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
          </div>

          {/* 其他账号 */}
          {others.length > 0 && (
            <div className="py-1 border-b border-violet-500/10">
              {others.map(acc => (
                <button key={acc.username} onClick={() => switchTo(acc)}
                  className="w-full flex items-center gap-2.5 px-4 py-2.5 hover:bg-violet-500/6 active:bg-violet-500/10 transition-colors">
                  <AvatarCircle name={acc.username} size="sm" />
                  <div className="min-w-0 text-left">
                    <div className="text-[13px] font-display tracking-wide truncate">{acc.username}</div>
                    <div className="text-[10px] text-ink-soft dark:text-violet-300/50 tracking-widest">{ROLE_LABEL[acc.role ?? 'general']}</div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* 操作按钮 */}
          <div className="py-1">
            <button onClick={addAccount}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 hover:bg-violet-500/6 transition-colors text-violet-600 dark:text-violet-300">
              <span className="w-7 h-7 rounded-full border border-violet-500/30 grid place-items-center text-[16px] shrink-0">＋</span>
              <span className="text-[13px] font-display tracking-wide">添加账号</span>
            </button>
            <button onClick={logout}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 hover:bg-ember-500/6 transition-colors text-ember-600 dark:text-ember-300">
              <span className="w-7 h-7 rounded-full border border-ember-500/30 grid place-items-center shrink-0">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </span>
              <span className="text-[13px] font-display tracking-wide">退出此账号</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
