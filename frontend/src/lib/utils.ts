export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

// ── Single-token helpers (kept for backward compat) ──────────────────────
export function saveToken(token: string) {
  localStorage.setItem('eq_token', token)
}

export function clearToken() {
  localStorage.removeItem('eq_token')
  localStorage.removeItem('eq_user')
}

export function getUsername(): string {
  return localStorage.getItem('eq_username') ?? '朋友'
}

export function saveUsername(name: string) {
  localStorage.setItem('eq_username', name)
}

// ── Multi-account helpers ─────────────────────────────────────────────────
export interface AccountEntry {
  username: string
  token: string
  role: string       // decoration_boss | property_manager | general
  last_seen: number  // unix timestamp ms
}

export function getAccounts(): AccountEntry[] {
  try { return JSON.parse(localStorage.getItem('eq_accounts') ?? '[]') } catch { return [] }
}

function setAccounts(accounts: AccountEntry[]) {
  localStorage.setItem('eq_accounts', JSON.stringify(accounts))
}

export function upsertAccount(entry: AccountEntry) {
  const accounts = getAccounts().filter(a => a.username !== entry.username)
  accounts.unshift(entry) // most recently used first
  setAccounts(accounts)
}

export function activateAccount(username: string): boolean {
  const accounts = getAccounts()
  const account = accounts.find(a => a.username === username)
  if (!account) return false
  saveToken(account.token)
  saveUsername(account.username)
  // bubble to top
  const updated = [account, ...accounts.filter(a => a.username !== username)]
  updated[0].last_seen = Date.now()
  setAccounts(updated)
  return true
}

export function removeAccount(username: string) {
  const accounts = getAccounts().filter(a => a.username !== username)
  setAccounts(accounts)
}

export function getActiveAccount(): AccountEntry | null {
  const token = localStorage.getItem('eq_token')
  if (!token) return null
  return getAccounts().find(a => a.token === token) ?? null
}

export function logoutAll() {
  localStorage.removeItem('eq_token')
  localStorage.removeItem('eq_username')
  localStorage.removeItem('eq_accounts')
}

// Dark mode toggle
export function isDark(): boolean {
  return document.documentElement.classList.contains('dark')
}
export function toggleDark() {
  const html = document.documentElement
  html.classList.toggle('dark')
  localStorage.setItem('eq_theme', html.classList.contains('dark') ? 'dark' : 'light')
}
export function initTheme() {
  const saved = localStorage.getItem('eq_theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  if (saved === 'dark' || (!saved && prefersDark)) {
    document.documentElement.classList.add('dark')
  }
}

// Format date
export function formatDate(d: Date = new Date()): string {
  return `${d.getFullYear()}·${String(d.getMonth()+1).padStart(2,'0')}·${String(d.getDate()).padStart(2,'0')}`
}

// Get weekday label
export function weekdayLabel(d: Date): string {
  return ['日','一','二','三','四','五','六'][d.getDay()]
}
