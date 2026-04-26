import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { ArrowLeft, RotateCcw, Grid3X3, CheckCircle2, TrendingUp, Lightbulb, BookOpen, MessageSquare, Sparkles } from 'lucide-react'

interface Summary {
  total_score: number
  dimension_averages: Record<string, number>
  strengths: string[]
  improvements: string[]
  best_turn: number
  worst_turn: number
  overall_feedback: string
}

interface Socratic {
  opening: string
  questions: string[]
  hint: string
}

const DIMENSION_META: Record<string, { icon: string; color: string }> = {
  '共情力': { icon: '💖', color: 'bg-pink-500' },
  '倾听力': { icon: '👂', color: 'bg-blue-500' },
  '情绪管理': { icon: '🧘', color: 'bg-violet-500' },
  '表达力': { icon: '💬', color: 'bg-emerald-500' },
  '关系维护': { icon: '🤝', color: 'bg-amber-500' },
  '幽默化解': { icon: '😄', color: 'bg-orange-500' },
}

function getScoreLabel(score: number) {
  if (score >= 4.5) return { label: '出色', color: 'text-emerald-600' }
  if (score >= 4) return { label: '优秀', color: 'text-emerald-600' }
  if (score >= 3) return { label: '良好', color: 'text-amber-600' }
  if (score >= 2) return { label: '待提升', color: 'text-red-600' }
  return { label: '需要加强', color: 'text-red-600' }
}

export default function SummaryPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [searchParams] = useSearchParams()
  const scenarioId = searchParams.get('scenario')
  const navigate = useNavigate()
  const [summary, setSummary] = useState<Summary | null>(null)
  const [socratic, setSocratic] = useState<Socratic | null>(null)
  const [referenceAnswers, setReferenceAnswers] = useState<string[]>([])
  const [theoryTags, setTheoryTags] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [socraticAnswer, setSocraticAnswer] = useState('')
  const [showHint, setShowHint] = useState(false)

  useEffect(() => {
    if (!sessionId) return
    fetch(`/api/end/${sessionId}`)
      .then((r) => {
        if (!r.ok) throw new Error('获取总结失败')
        return r.json()
      })
      .then((data) => {
        setSummary(data.summary)
        setSocratic(data.socratic)
        setReferenceAnswers(data.reference_answers || [])
        setTheoryTags(data.theory_tags || [])
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [sessionId])

  if (loading) {
    return (
      <div className="min-h-screen gradient-cool flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl gradient-primary flex items-center justify-center shadow-lg shadow-violet-500/30 animate-pulse-soft">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <p className="text-muted-foreground">正在分析你的表现...</p>
        </div>
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="min-h-screen gradient-cool flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button variant="outline" onClick={() => navigate('/scenarios')}>
            返回场景列表
          </Button>
        </div>
      </div>
    )
  }

  const scoreInfo = getScoreLabel(summary.total_score)

  return (
    <div className="min-h-screen gradient-cool">
      {/* Header */}
      <div className="glass border-b border-white/30 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/scenarios')}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <h1 className="font-semibold text-gradient">练习总结</h1>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
        {/* Total Score */}
        <Card className="bg-white/80 backdrop-blur-sm border-white/50 shadow-lg text-center animate-fade-in">
          <CardContent className="p-8">
            <div className={`text-6xl font-bold mb-1 ${scoreInfo.color}`}>
              {summary.total_score.toFixed(1)}
            </div>
            <div className="text-sm text-muted-foreground mb-4">{scoreInfo.label}</div>
            <p className="text-sm text-muted-foreground max-w-md mx-auto leading-relaxed">
              {summary.overall_feedback}
            </p>
          </CardContent>
        </Card>

        {/* Dimension Radar (CSS-based) */}
        <Card className="bg-white/80 backdrop-blur-sm border-white/50 shadow-lg animate-fade-in" style={{ animationDelay: '100ms' }}>
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-5">各维度表现</h3>
            <div className="space-y-4">
              {Object.entries(summary.dimension_averages).map(([dim, score]: [string, any]) => {
                const meta = DIMENSION_META[dim] || { icon: '·', color: 'bg-gray-500' }
                return (
                  <div key={dim} className="flex items-center gap-3">
                    <span className="text-lg w-6 text-center">{meta.icon}</span>
                    <span className="text-sm text-foreground w-16 shrink-0">{dim}</span>
                    <div className="flex-1">
                      <Progress
                        value={score}
                        max={5}
                        indicatorClassName={meta.color}
                      />
                    </div>
                    <span className={`text-sm font-bold w-8 text-right ${
                      score >= 4 ? 'text-emerald-600' : score >= 3 ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {score.toFixed(1)}
                    </span>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Strengths & Improvements */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-emerald-50/80 backdrop-blur-sm border-emerald-100/50 animate-slide-in-right" style={{ animationDelay: '200ms' }}>
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <h3 className="font-semibold text-emerald-700">做得好的</h3>
              </div>
              <ul className="space-y-2">
                {summary.strengths.map((s, i) => (
                  <li key={i} className="text-sm text-emerald-800 flex gap-2">
                    <span className="text-emerald-400 shrink-0">+</span>
                    {s}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-amber-50/80 backdrop-blur-sm border-amber-100/50 animate-slide-in-right" style={{ animationDelay: '300ms' }}>
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-4 h-4 text-amber-600" />
                <h3 className="font-semibold text-amber-700">可以更好的</h3>
              </div>
              <ul className="space-y-2">
                {summary.improvements.map((s, i) => (
                  <li key={i} className="text-sm text-amber-800 flex gap-2">
                    <span className="text-amber-400 shrink-0">^</span>
                    {s}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Socratic Reflection */}
        {socratic && (
          <Card className="bg-violet-50/80 backdrop-blur-sm border-violet-100/50 shadow-lg animate-fade-in" style={{ animationDelay: '400ms' }}>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-violet-600" />
                <h3 className="font-semibold text-violet-700">反思时刻</h3>
              </div>
              <p className="text-sm text-violet-800 mb-4">{socratic.opening}</p>
              <div className="space-y-3 mb-4">
                {socratic.questions.map((q, i) => (
                  <div key={i} className="bg-white rounded-xl p-4 border border-violet-100">
                    <p className="text-sm text-foreground font-medium">{q}</p>
                  </div>
                ))}
              </div>
              <textarea
                value={socraticAnswer}
                onChange={(e) => setSocraticAnswer(e.target.value)}
                placeholder="写下你的思考..."
                className="w-full px-4 py-3 border border-violet-200 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none resize-none bg-white text-sm"
                rows={3}
              />
              {!showHint ? (
                <button
                  onClick={() => setShowHint(true)}
                  className="text-xs text-violet-400 hover:text-violet-600 mt-2 transition-colors"
                >
                  想不出来？看看提示
                </button>
              ) : (
                <div className="mt-2 bg-white rounded-lg p-3 border border-violet-100">
                  <p className="text-xs text-violet-600">{socratic.hint}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Theory Tags */}
        {theoryTags.length > 0 && (
          <Card className="bg-white/80 backdrop-blur-sm border-white/50 animate-fade-in" style={{ animationDelay: '500ms' }}>
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-4 h-4 text-violet-500" />
                <h3 className="font-semibold text-foreground">本场景涉及的理论</h3>
              </div>
              <div className="space-y-2">
                {theoryTags.map((t, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="font-medium text-violet-600">{t.source}</span>
                    <span className="text-muted-foreground/40">·</span>
                    <span className="text-muted-foreground">{t.framework}</span>
                    <span className="text-muted-foreground/40">—</span>
                    <span className="text-muted-foreground">{t.technique}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Reference Answers */}
        {referenceAnswers.length > 0 && (
          <Card className="bg-white/80 backdrop-blur-sm border-white/50 animate-fade-in" style={{ animationDelay: '600ms' }}>
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-4 h-4 text-emerald-500" />
                <h3 className="font-semibold text-foreground">参考答案</h3>
              </div>
              <div className="space-y-3">
                {referenceAnswers.map((ans, i) => (
                  <div key={i} className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
                    <p className="text-sm text-emerald-700 leading-relaxed">{ans}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-2 pb-8 animate-fade-in" style={{ animationDelay: '700ms' }}>
          <Button
            onClick={() => navigate(scenarioId ? `/practice/${scenarioId}` : '/scenarios')}
            className="flex-1 gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            再练一次
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate('/scenarios')}
            className="flex-1 gap-2"
          >
            <Grid3X3 className="w-4 h-4" />
            换个场景
          </Button>
        </div>
      </div>
    </div>
  )
}
