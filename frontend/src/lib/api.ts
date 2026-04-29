const BASE = import.meta.env.VITE_API_URL ?? ''

function getToken(): string | null {
  return localStorage.getItem('eq_token')
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('eq_token')
      localStorage.removeItem('eq_username')
      window.location.href = '/login'
      throw new Error('登录已过期')
    }
    if (res.status === 502 || res.status === 504) {
      throw new Error('服务器响应超时，请稍后再试')
    }
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? '请求失败')
  }
  return res.json()
}

export const api = {
  // Auth
  login: (username: string, password: string) =>
    req<{ access_token: string }>('POST', '/api/v1/auth/login', { username, password }),
  register: (username: string, password: string, target_role = 'general') =>
    req<{ access_token: string }>('POST', '/api/v1/auth/register', { username, password, target_role }),
  me: () => req<{ id: number; username: string; target_style: string; target_styles: string[]; humor_weight: number; target_role: string }>('GET', '/api/v1/auth/me'),

  // Skills
  skills: () => req<SkillItem[]>('GET', '/api/v1/skills'),
  skill: (id: string) => req<SkillDetail>('GET', `/api/v1/skills/${id}`),

  // Practice
  startPractice: (skill_id: string, difficulty?: number, scenario_template_id?: number, diary_id?: number) =>
    req<StartPracticeResp>('POST', '/api/v1/practice/start', {
      skill_id,
      difficulty: difficulty ?? 3,
      ...(scenario_template_id ? { scenario_template_id } : {}),
      ...(diary_id ? { diary_id } : {}),
    }),
  submitTurn: (practice_id: number, user_input: string, input_mode?: string, mode?: string, socratic_question?: string) =>
    req<TurnResp>('POST', `/api/v1/practice/${practice_id}/turn`, {
      user_input, input_mode: input_mode ?? 'text',
      ...(mode ? { mode } : {}),
      ...(socratic_question ? { socratic_question } : {}),
    }),
  completePractice: (practice_id: number) =>
    req<{ ok: boolean; avg_score: number; skill_level: number }>('POST', `/api/v1/practice/${practice_id}/complete`),

  // Diary
  createDiary: (data: DiaryInput) => req<DiaryResp>('POST', '/api/v1/diary', data),
  listDiaries: () => req<DiaryListItem[]>('GET', '/api/v1/diary'),
  getRewrite: (diary_id: number) => req<{ rewrite_suggestion: string }>('GET', `/api/v1/diary/${diary_id}/rewrite`),

  // Home aggregate
  homeSummary: () => req<HomeSummary>('GET', '/api/v1/home/summary'),

  // Scenario library
  listScenarios: (role: 'auto' | 'all' | 'decoration_boss' | 'property_manager' | 'beauty_clinic_boss' | 'general' = 'auto') =>
    req<ScenarioListResp>('GET', `/api/v1/scenarios?role=${role}`),

  // Styles
  getStyles: () => req<{ styles: StyleInfo[] }>('GET', '/api/v1/auth/styles'),
  saveStyles: (target_styles: string[]) =>
    req<{ ok: boolean; target_styles: string[] }>('PUT', '/api/v1/auth/styles', { target_styles }),

  // Practice reflect (Socratic)
  reflect: (practice_id: number, user_reflection: string, socratic_question: string, round_number: number) =>
    req<ReflectResp>('POST', `/api/v1/practice/${practice_id}/reflect`, { user_reflection, socratic_question, round_number }),

  // TTS
  tts: async (text: string, emotion = 'neutral'): Promise<Blob | null> => {
    const headers: Record<string, string> = {}
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
    try {
      const res = await fetch(`${BASE}/api/v1/tts?text=${encodeURIComponent(text)}&emotion=${emotion}`, { headers })
      if (res.status === 204) return null
      if (!res.ok) return null
      return await res.blob()
    } catch {
      return null
    }
  },

  // Plan / Invite
  getPlan: () => req<{ plan: string; expiresAt: string | null }>('GET', '/api/v1/invite/plan'),
  getUsage: () => req<{ plan: string; limit: number; used: number; remaining: number }>('GET', '/api/v1/invite/usage'),
  validateInvite: (code: string, userId?: number) =>
    req<{ valid: boolean; plan?: string; expiresAt?: string }>('POST', '/api/v1/invite/validate', { code, userId }),
}

export interface ScenarioSkillTag { id: string; name: string; icon: string }
export interface ScenarioListItem {
  id: number
  category: string
  sub_type: string
  title: string
  role_brief: string
  tension_brief: string
  user_goal_brief: string
  difficulty: number
  applicable_roles: string[]
  primary_skill_id: string | null
  skills: ScenarioSkillTag[]
}
export interface ScenarioListResp {
  role: string
  total: number
  items: ScenarioListItem[]
}

// Types
export interface SkillItem {
  id: string; name: string; category: string; stage: string; description: string;
  level: number; next_review_at: string | null;
}
export interface SkillDetail extends SkillItem {
  patterns: string; examples: string; correct_streak: number;
}
export interface StartPracticeResp {
  practice_id: number; title: string; scenario_setup: string;
  initial_message: string; ai_emotion: string;
}
export interface TurnResp {
  turn_number: number; ai_message: string | null; ai_emotion: string | null; should_end: boolean;
  total_score: number | null; scores: Record<string, number> | null; narrative: string | null;
  strengths: string | null; improvements: string | null; rewrite_suggestion: string | null;
  rewrite_suggestions: RewriteSuggestion[];
  techniques_used: string[]; techniques_available: string[]; style_matched: string | null;
  socratic_question: string | null; socratic_encouragement: string | null;
  coach_followup: string | null;
  ai_fallback?: boolean;
  well_used: string[]; missing: string[];
}
export interface RewriteSuggestion {
  style: string; style_name: string; text: string;
  techniques: string[]; technique_breakdown: string;
}
export interface StyleInfo {
  id: string; name: string; school: string; philosophy: string;
  famous_scene: string; learn: string[]; for_who: string; icon: string;
}
export interface ReflectResp {
  coach_reply: string; is_complete: boolean; technique_hint: string | null;
}
export interface DiaryInput {
  mode?: 'react' | 'initiate';
  context: string; other_party: string; their_words: string; my_response: string; outcome: string;
}
export interface DiaryResp {
  diary_id: number; analysis_id: number; identified_skills: string[];
  diagnosis_brief: string; socratic_questions: string[]; referenced_style: string;
}
export interface DiaryListItem {
  id: number; context: string; created_at: string;
}

// Home summary
export interface HomeStreakDay {
  date: string; day: number; weekday: string; done: boolean; today: boolean;
}
export interface HomeStreak {
  current: number; day_count: number; week: HomeStreakDay[]; week_done: number;
}
export interface HomeStyleItem { key: string; name: string; pct: number }
export interface HomeStyleStats {
  total_count: number;
  distribution: HomeStyleItem[];
  top_recent: string | null;
  target_styles?: string[];
}
export interface HomeHighlight {
  their_words: string;
  my_response: string;
  scores: { decency?: number; defusion?: number; humor?: number; style_match?: number };
  top_style: string;
  top_style_name: string;
  scenario_title: string | null;
}
export interface HomeBlindScene {
  skill_id: string; skill_name: string; icon: string; stage: string; level: number; scene_brief: string;
  scenario_title: string | null;
  scenario_setup: string | null;
  tension_brief: string | null;
  difficulty: number;
  category: string | null;
}
export interface HomeBlindBox {
  scenes: HomeBlindScene[]; skills_label: string; total: number; minutes_estimate: number;
}
export interface HomeSkillItem {
  id: string; name: string; icon: string; stage: string; level: number;
}
export interface HomeSkills {
  total: number; lit: number; items: HomeSkillItem[];
}
export interface HomeSummary {
  username: string;
  today: string;
  streak: HomeStreak;
  style_stats: HomeStyleStats;
  highlight: HomeHighlight | null;
  today_blind_box: HomeBlindBox;
  skills: HomeSkills;
  target_styles?: string[];
}
