import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Brain, LogIn, UserPlus } from 'lucide-react'

export default function ConfigPage() {
  const navigate = useNavigate()
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async () => {
    if (!username || !password) return
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const endpoint = isRegister ? '/api/register' : '/api/login'
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || '操作失败')
      }
      if (isRegister) {
        setSuccess('注册成功！请登录')
        setIsRegister(false)
        setPassword('')
      } else {
        localStorage.setItem('eq_user', username)
        navigate('/scenarios', { replace: true })
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-cool flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl gradient-primary shadow-lg shadow-violet-500/30 mb-6">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3">
            <span className="text-gradient">EQ Trainer</span>
          </h1>
          <p className="text-lg text-muted-foreground mb-2">高情商沟通训练器</p>
          <p className="text-sm text-muted-foreground/70">
            场景化刻意练习 · 即时多维评分 · 苏格拉底反思
          </p>
        </div>

        <Card className="glass border-white/30 shadow-xl">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              {isRegister ? <UserPlus className="w-4 h-4" /> : <LogIn className="w-4 h-4" />}
              {isRegister ? '注册新账号' : '登录账号'}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">用户名</label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="输入用户名"
                className="h-11"
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">密码</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="输入密码"
                className="h-11"
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-100 text-red-600 rounded-lg text-sm">{error}</div>
            )}
            {success && (
              <div className="p-3 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-lg text-sm">{success}</div>
            )}

            <Button onClick={handleSubmit} disabled={!username || !password || loading} size="lg" className="w-full mt-2">
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {isRegister ? '注册中...' : '登录中...'}
                </span>
              ) : isRegister ? '注册' : '登录'}
            </Button>

            <div className="text-center">
              <button
                onClick={() => { setIsRegister(!isRegister); setError(''); setSuccess('') }}
                className="text-sm text-muted-foreground hover:text-violet-600 transition-colors"
              >
                {isRegister ? '已有账号？去登录' : '没有账号？注册一个'}
              </button>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground/50 mt-8">
          练 → 评 → 悟 · 三步循环 · 让高情商成为肌肉记忆
        </p>
      </div>
    </div>
  )
}
