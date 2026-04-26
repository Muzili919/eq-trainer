# 数据模型 v1

## 设计原则

1. **不存"标准答案"** — 评分由 AI 实时判断，不对照固定答案
2. **场景生成 > 场景固定** — 只存模板/类型，具体台词由 AI 生成
3. **细粒度记录** — 每轮对话单独存，便于后续分析和回溯
4. **可扩展** — MVP 用 SQLite，后续切 PostgreSQL 不动结构

## 技术栈

- **ORM**：SQLAlchemy 2.0 + SQLModel（Pydantic 一体，FastAPI 友好）
- **DB**：SQLite（MVP）→ PostgreSQL（开源/SaaS 后切）
- **迁移**：Alembic

## ER 总览

```
User ──┬── SkillProgress ─── Skill
       ├── Practice ─── PracticeTurn
       ├── Diary ─── DiaryAnalysis
       └── DailyStreak

ScenarioTemplate ─── Practice (生成时引用)
StyleReference ─── (静态种子，prompt few-shot 用)
```

---

## 表定义

### User

```python
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True, index=True, max_length=32)
    password_hash: str
    nickname: str | None = None  # 显示名
    
    # 风格偏好（影响推送和评分权重）
    target_style: str = "balanced"  # balanced | huangbo | xuzhisheng | lixueqin | hejiong
    humor_weight: float = 0.4  # 0-1，幽默指数在评分中的权重
    
    # 训练设置
    daily_goal: int = 3  # 每日目标题数（默认 3）
    voice_input_enabled: bool = True  # 是否启用语音输入
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime | None = None
```

---

### Skill（静态种子数据，从 SKILLS.md 导入）

```python
class Skill(SQLModel, table=True):
    id: str = Field(primary_key=True)  # 'L1', 'H2' 等
    category: str  # listening | expression | empathy | boundary | resolution | maintenance | humor
    name: str  # "情绪命名"
    name_en: str  # "emotion_naming"，给 AI prompt 用
    stage: str  # basic | mid | advanced
    
    description: str  # 一句话定义
    patterns: str  # JSON 数组，关键模式
    examples_good: str  # JSON 数组
    examples_bad: str  # JSON 数组
    socratic_prompts: str  # JSON 数组，引导问题集
    prerequisites: str  # JSON 数组，前置技能 id（如 ["L1"]）
    
    icon: str | None = None  # emoji 或图标 key
    color: str | None = None  # 主色（前端展示用）
```

---

### SkillProgress（用户对每个技能的熟练度）

```python
class SkillProgress(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    skill_id: str = Field(foreign_key="skill.id", index=True)
    
    level: int = 0  # 0-5（参考 SKILLS.md SRS 表）
    correct_streak: int = 0  # 连续达标次数（用于升级判定）
    total_attempts: int = 0
    avg_score: float = 0.0  # 历史平均分
    
    last_practiced_at: datetime | None = None
    next_review_at: datetime | None = None  # SRS 下次复习日
    
    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)
```

---

### ScenarioTemplate（场景模板，种子数据）

不写死具体台词，AI 据此实时生成：

```python
class ScenarioTemplate(SQLModel, table=True):
    id: int = Field(primary_key=True)
    
    category: str  # workplace | social | family | romance | self
    sub_type: str  # 'colleague_jealousy' | 'parent_nagging' | 'date_awkward' ...
    title: str  # "前同事酸你升职"
    
    # 场景参数（AI 用来生成具体台词）
    role_brief: str  # AI 扮演的角色画像
    tension_brief: str  # 冲突/张力来源
    user_goal_brief: str  # 用户在这场对话里的合理目标
    
    # 关联
    primary_skills: str  # JSON 数组：本场景主要练哪些技能 id
    difficulty: int  # 1-5
    
    # AI 生成 prompt 模板（含变量占位）
    generation_prompt: str
```

---

### Practice（一次完整练习会话）

```python
class Practice(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # 触发来源
    source: str  # daily | diary | freestyle | skill_drill
    scenario_template_id: int | None = Field(foreign_key="scenariotemplate.id", default=None)
    diary_id: int | None = Field(foreign_key="diary.id", default=None)
    target_skill_id: str | None = Field(foreign_key="skill.id", default=None)  # 主要练的技能
    
    # AI 生成的具体场景（不固定）
    scenario_setup: str  # 场景描述（AI 生成）
    initial_message: str  # 对方开口的第一句话（AI 生成）
    
    # 状态
    status: str = "in_progress"  # in_progress | completed | abandoned
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    
    # 最终结果（completed 时填）
    final_scores: str | None = None  # JSON: {decency, defusion, humor, style_match}
    style_matched: str | None = None  # huangbo | xuzhisheng | lixueqin | hejiong | none
    summary_feedback: str | None = None  # AI 总评
    socratic_round_count: int = 0  # 用了几轮苏格拉底引导
```

---

### PracticeTurn（每轮对话，含 AI 评分和反馈）

```python
class PracticeTurn(SQLModel, table=True):
    id: int = Field(primary_key=True)
    practice_id: int = Field(foreign_key="practice.id", index=True)
    turn_index: int  # 第几轮（0 开始）
    
    # AI 扮演方的话
    ai_message: str
    ai_emotion: str | None = None  # 该轮 AI 角色的情绪（可视化用）
    
    # 用户回应
    user_input_mode: str  # text | voice
    user_response: str  # 文本（语音转文本后）
    user_audio_url: str | None = None  # 语音原始音频（可选保留）
    response_time_ms: int | None = None  # 用户响应耗时（评估"即兴"）
    
    # AI 评分（4 维度）
    score_decency: int | None = None  # 得体度 0-100
    score_defusion: int | None = None  # 化解力 0-100
    score_humor: int | None = None  # 幽默指数 0-100
    score_style_match: int | None = None  # 风格匹配度 0-100
    style_matched: str | None = None  # 最像谁
    
    # AI 反馈
    feedback_text: str | None = None  # 描述性反馈
    suggested_rewrite: str | None = None  # 改写建议
    referenced_style_id: int | None = None  # 引用的风格基准条目
    
    # 苏格拉底
    socratic_triggered: bool = False  # 是否触发引导
    socratic_questions: str | None = None  # JSON 数组：本轮提的引导问题
    socratic_attempts: int = 0  # 用户重写次数
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Diary（真实场景日记）

```python
class Diary(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # 用户输入
    occurred_at: datetime  # 实际发生时间（用户填）
    context: str  # 场景描述（"昨天和老板开会"）
    other_party: str | None = None  # 对方是谁（"领导"/"同事 A"/"妈妈"）
    
    their_words: str  # 对方说了啥
    my_response: str  # 我说了啥
    outcome: str | None = None  # 结果（"对方沉默"/"吵起来"/"还行"）
    
    input_mode: str = "text"  # text | voice
    
    # 关联（AI 分析后填）
    practice_id: int | None = None  # 触发的微练习（如果用户进了重演）
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### DiaryAnalysis（AI 苏格拉底诊断结果）

```python
class DiaryAnalysis(SQLModel, table=True):
    id: int = Field(primary_key=True)
    diary_id: int = Field(foreign_key="diary.id", index=True, unique=True)
    
    # AI 分析
    socratic_questions: str  # JSON 数组：3 个反问
    identified_skills: str  # JSON 数组：识别出的薄弱技能 id（["L1", "H1"]）
    diagnosis_summary: str  # 简短诊断（不直接评判）
    suggested_rewrite: str | None = None  # 改写示范（如果用户卡住才给）
    referenced_style_id: int | None = None
    
    # 用户和 AI 的反思对话（多轮）
    reflection_dialog: str | None = None  # JSON 数组：[{role, content, timestamp}]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### StyleReference（风格基准条目，静态种子）

4 人的经典回应语料库，prompt few-shot 用：

```python
class StyleReference(SQLModel, table=True):
    id: int = Field(primary_key=True)
    
    persona: str  # huangbo | xuzhisheng | lixueqin | hejiong
    scenario_type: str  # praised | attacked | awkward | rejected | comforting | tease | other
    
    trigger: str  # 对方说了啥
    response: str  # ta 怎么回的
    technique: str  # JSON 数组：用到的技能 id（["H1", "EM1"]）
    
    notes: str | None = None  # 解释为什么有效
    source: str | None = None  # 出处（综艺/采访/...）
```

---

### DailyStreak（每日打卡）

```python
class DailyStreak(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    
    current_streak: int = 0  # 当前连续天数
    longest_streak: int = 0  # 历史最长
    last_active_date: date | None = None  # 最后活跃日（用于判断断签）
    total_days: int = 0  # 累计活跃天数
```

---

### DailyLog（每日完成情况，单独存便于日历视图）

```python
class DailyLog(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    log_date: date = Field(index=True)
    
    practices_completed: int = 0
    avg_score: float | None = None
    diary_count: int = 0
    
    __table_args__ = (UniqueConstraint("user_id", "log_date"),)
```

---

## 索引策略

```
User.username (unique)
SkillProgress.(user_id, skill_id) (unique)
SkillProgress.next_review_at (推送查询用)
Practice.user_id + Practice.started_at (用户练习历史)
PracticeTurn.practice_id
Diary.user_id + Diary.occurred_at
DailyLog.(user_id, log_date) (unique)
```

## 种子数据需求

启动 MVP 时要预填：
1. **Skill 表**：12 条技能（从 SKILLS.md 导入）
2. **ScenarioTemplate 表**：每个技能至少 3 个场景模板，共 ~40 个
3. **StyleReference 表**：4 人 x 每人 20 条 = 80 条经典回应（详见 STYLE_REFERENCE.md）

## 后置（V2 之后）

- `WeeklyReview` 周复盘表
- `Achievement` 成就/徽章表
- `OAuthAccount`（Google/GitHub 登录）
- `Subscription`（B1 商业化）
- `ApiUsage`（按 token 计费用）
