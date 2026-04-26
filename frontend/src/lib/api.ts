const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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
  me: () => req<{ id: number; username: string; target_style: string; humor_weight: number; target_role: string }>('GET', '/api/v1/auth/me'),

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
  submitTurn: (practice_id: number, user_input: string, input_mode?: string) =>
    req<TurnResp>('POST', `/api/v1/practice/${practice_id}/turn`, { user_input, input_mode: input_mode ?? 'text' }),
  completePractice: (practice_id: number) =>
    req<{ ok: boolean; avg_score: number; skill_level: number }>('POST', `/api/v1/practice/${practice_id}/complete`),

  // Diary
  createDiary: (data: DiaryInput) => req<DiaryResp>('POST', '/api/v1/diary', data),
  listDiaries: () => req<DiaryListItem[]>('GET', '/api/v1/diary'),
  getRewrite: (diary_id: number) => req<{ rewrite_suggestion: string }>('GET', `/api/v1/diary/${diary_id}/rewrite`),

  // Home aggregate
  homeSummary: () => req<HomeSummary>('GET', '/api/v1/home/summary'),

  // Scenario library
  listScenarios: (role: 'auto' | 'all' | 'decoration_boss' | 'property_manager' | 'general' = 'auto') =>
    req<ScenarioListResp>('GET', `/api/v1/scenarios?role=${role}`),
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
  turn_number: number; ai_message: string; ai_emotion: string; should_end: boolean;
  total_score: number; scores: Record<string, number>;
  strengths: string; improvements: string; rewrite_suggestion: string | null;
  socratic_question: string | null; socratic_encouragement: string | null;
  well_used: string[]; missing: string[];
}
export interface DiaryInput {
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
}
