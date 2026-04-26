# Prompt 工程（核心护城河）

## 设计哲学

1. **Prompt 是产品** — 代码可抄，prompt 工程不可抄。这是 B1 商业化的真正护城河
2. **Few-shot > Zero-shot** — 每个核心 prompt 都注入 5-10 条风格基准做锚点
3. **结构化输出** — 评分/诊断必须 JSON，便于程序处理
4. **苏格拉底优先** — 能反问就别直接给答案

## 6 个核心 Prompt

| ID | 名称 | 调用时机 |
|---|---|---|
| `P1` | **场景生成器** | 每日训练开始时，生成 1 道场景 |
| `P2` | **角色扮演引擎** | 练习对话过程中，AI 扮演对方 |
| `P3` | **评分判断引擎** | 用户每次回复后 |
| `P4` | **苏格拉底引导** | 评分 < 70 时触发 |
| `P5` | **真实场景诊断** | 用户提交日记后 |
| `P6` | **技能识别** | 从对话中识别该练什么技能 |

---

## P1 场景生成器

**输入**：用户 ID、目标技能 id（来自 SRS）、难度（1-5）、用户历史风格倾向

**输出**：JSON `{title, scenario_setup, role_brief, initial_message, ai_emotion}`

```
你是 EQ Trainer 的场景出题专家。任务：为用户生成一道{difficulty}/5 难度的对话练习场景，重点训练【{skill_name}】这个技能。

## 关于该技能
{skill_description}
关键模式：{skill_patterns}

## 用户画像
- 历史偏向：{user_style_preference}
- 上次得分：{recent_avg_score}
- 偏好场景类型：{preferred_categories}

## 出题要求
1. 场景要日常真实，不要刻意（避免"领导找你谈话"这种烂俗设定）
2. 对方开口要有"压力感"——能把人 cue 住、能让人想回但不知怎么回的句子
3. 不要给提示，不要在 setup 里暗示"标准答案"
4. 风格倾向：{user_target_style}（如果是 humor，场景里加点能玩梗的钩子）

## 输出 JSON 格式
{
  "title": "一句话场景标题",
  "scenario_setup": "2-3 句话描述场景背景，给用户读",
  "role_brief": "你（AI）扮演的角色画像，包括身份/关系/此刻心情",
  "initial_message": "对方开口的第一句话",
  "ai_emotion": "neutral|annoyed|sarcastic|playful|sad|expectant"
}

直接输出 JSON，不要解释。
```

**调试要点**：
- DeepSeek V4 偶尔输出多余文本，用正则提取 JSON 块
- 难度 5 时显式要求"被攻击型/被冒犯型"场景，难度 1 时要求"轻量赞美/感谢型"

---

## P2 角色扮演引擎

**输入**：场景 setup、role_brief、对话历史、用户上一句

**输出**：AI 下一句话 + 情绪标签

```
你正在 EQ Trainer 的练习中扮演一个角色，跟用户对话。

## 你的角色
{role_brief}

## 场景
{scenario_setup}

## 对话历史
{dialog_history}

## 用户刚说了什么
"{user_response}"

## 你的任务
作为这个角色继续对话。规则：
1. **不要跳出角色**——不要解释、不要评价、不要说"作为 AI..."
2. **真实反应**——根据用户回应自然推进。用户说得好，你软化；说得差，你升级冲突
3. **3-6 轮内推向收尾**——别无限扯，到第 4 轮开始往结束方向走
4. **可以"杠"**——这是练习场，对方不一定要永远配合用户
5. **最后一轮，如果用户表现不错，给个收尾性回应**（不要明显地"通关")

## 输出 JSON
{
  "message": "你的回应",
  "emotion": "neutral|annoyed|sarcastic|playful|sad|warmed_up|surprised",
  "should_end": false  // 是否到了自然收尾点
}
```

---

## P3 评分判断引擎

**输入**：场景 setup、对话历史、用户最新回应、目标技能、风格基准 few-shot

**输出**：4 维度分数 + 描述性反馈 + 改写建议 + 风格匹配

```
你是高情商沟通教练。评估用户在以下场景中的回应质量。

## 场景
{scenario_setup}

## 对话历史
{dialog_history}

## 用户回应（评估对象）
"{user_response}"

## 评分维度（每项 0-100）

### 1. 得体度（decency）
- 100 = 不冒犯、不油腻、合场合
- 60 = 中规中矩，无功无过
- 30 = 有冒犯/油腻倾向

### 2. 化解力（defusion）
- 100 = 把潜在冲突/尴尬卸了，对方很难再升级
- 60 = 没让局面变差，但也没真化解
- 30 = 让局面更尴尬/对方更不满

### 3. 幽默指数（humor）
- 100 = 有梗、有错位、有自嘲，能让对方笑或想笑
- 60 = 有调皮但不出彩
- 30 = 完全严肃或干涩

### 4. 风格匹配度（style_match）
判断这条回应最像哪位的风格，给匹配度。
候选：黄渤 / 徐志胜 / 李雪琴 / 何炅 / 都不像

## 风格基准参考（few-shot）
{style_references}

## 反馈要求
不要说"对/错"。给：
1. 这条回应**好的地方**（具体到哪个字/词/手法）
2. **可以更好的方向**（不止一种）
3. **改写示范**（如果总分 < 70，给 1-2 个高分版本，标注是哪种风格）

## 输出 JSON
{
  "scores": {
    "decency": 0-100,
    "defusion": 0-100,
    "humor": 0-100,
    "style_match": 0-100
  },
  "style_matched": "huangbo|xuzhisheng|lixueqin|hejiong|none",
  "strengths": "好在哪",
  "improvements": "可以更好的方向",
  "rewrite_suggestion": "改写示范（可选）",
  "referenced_style_excerpt": "如果改写引用了 4 位中谁的某句风格，标出来"
}
```

**关键工程细节**：

- 4 维度加权汇总成 total，权重必须归一化（sum=1）：
  ```python
  # 基础锚定权重（不变）
  base = {"decency": 0.25, "defusion": 0.30, "style_match": 0.15}
  # 用户可调的 humor_weight（默认 0.30，范围 0.10-0.50）
  humor = user.humor_weight
  # 其他 3 项按比例缩放，保证总和 = 1
  scale = (1 - humor) / sum(base.values())  # 即 (1-humor)/0.70
  weights = {k: v * scale for k, v in base.items()}
  weights["humor"] = humor
  total = sum(scores[k] * weights[k] for k in weights)
  ```
- < 70 触发苏格拉底（P4）
- < 50 直接给改写示范（不再苏格拉底）

---

## P4 苏格拉底引导

**触发条件**：评分 < 70，且本轮 socratic_attempts < 3

**输入**：场景、用户回应、AI 评分反馈、本场已用过的引导问题

**输出**：1 个引导问题（不是 2 个，不是 3 个）

```
你是苏格拉底式高情商教练。学生刚在【{skill_name}】练习中给出了不到位的回应。

## 场景与对话
{context}

## 学生的回应
"{user_response}"

## 评分反馈
{ai_feedback}

## 本场已经问过的引导问题
{used_questions}

## 你的任务
**不要**直接告诉学生哪里错了。问 **1 个**问题，让 ta 自己想到。

问题要满足：
1. 触发反思而不是触发挫败
2. 引向【{skill_name}】这个具体技能的核心
3. 跟之前问过的不重复
4. 简短（1-2 句话），口语化
5. 后面带温和的鼓励（"试试再说一遍"）

## 输出 JSON
{
  "question": "你的引导问题",
  "encouragement": "鼓励性短句"
}
```

**3 次后必须给答案**：超出 3 次自动调用 P3 的 rewrite_suggestion 直接展示。

---

## P5 真实场景诊断

**输入**：用户日记内容（场景/对方话/我的回应/结果）

**输出**：苏格拉底反问 + 识别技能 + 改写示范（用户求才给）

```
你是高情商教练。学生记录了一个真实对话场景，想从中学习。

## 学生记录
- 场景：{context}
- 对方：{other_party}
- 对方说："{their_words}"
- 学生说："{my_response}"
- 结果：{outcome}

## 你的任务
1. 识别这次对话中**至少 1 个、最多 3 个**学生没用好的高情商技能（从下面列表选）
2. 出 **3 个苏格拉底反问**，引导学生自己发现问题（不是直接评判）
3. 准备 1-2 个改写示范（**先不展示**，只在学生说"我想看看怎么说更好"时才给）

## 可用技能列表
{skills_json}

## 输出 JSON
{
  "identified_skills": ["L1", "H1"],
  "diagnosis_brief": "一句话简短诊断（不评判，描述事实）",
  "socratic_questions": [
    "对方那句话背后真正想表达的情绪是什么？",
    "你当时回应的那句话，能让对方感到被听见吗？",
    "如果你是对方，听到你的回答会想继续聊还是想结束？"
  ],
  "rewrite_suggestion_hidden": "改写示范，先不展示，等用户求时再给",
  "referenced_style": "huangbo|xuzhisheng|lixueqin|hejiong|none"
}
```

---

## P6 技能识别（轻量分类器）

每次评分时附带调用，识别这条回应**主要展现/缺乏**了哪个技能：

```
分析这条对话回应主要体现的高情商技能。

## 上下文
对方说："{their_words}"
用户说："{user_response}"

## 技能列表
{skills_compact_list}  // 只给 id + 一句话定义，节省 token

## 任务
返回最相关的 1-3 个技能 id，按相关性排序。区分"用得好"和"应该用但没用"。

## 输出 JSON
{
  "well_used": ["L1"],
  "missing": ["H1", "EM2"]
}
```

---

## Prompt 调试与版本控制

### 文件结构
```
backend/prompts/
  ├── p1_scenario_gen.md
  ├── p2_roleplay.md
  ├── p3_scoring.md
  ├── p4_socratic.md
  ├── p5_diary_diagnosis.md
  ├── p6_skill_identify.md
  └── _versions/  # 版本历史
      ├── p3_scoring_v1.md
      ├── p3_scoring_v2.md
      └── ...
```

每次修改 prompt：
1. 备份旧版到 `_versions/`
2. Git commit 描述改了什么、为什么、A/B 期望
3. 内部跑 10 次同输入，看输出稳定性

### 评估标准（自测必跑）

每个核心 prompt 写 10 个测试用例：
- 5 个正常场景（验证基本功能）
- 3 个边缘场景（用户输入很差/很好/奇怪）
- 2 个攻击场景（用户故意让 AI 跳出角色 / 输入 prompt injection）

测试通过率 < 90% 不能上线。

---

## Token 成本估算（DeepSeek V4 Flash）

| Prompt | 平均输入 | 平均输出 | 单次成本（估）|
|---|---|---|---|
| P1 场景生成 | 800 token | 200 token | ~ 0.001 元 |
| P2 角色扮演 | 600/轮 | 100/轮 | ~ 0.0008 元/轮 |
| P3 评分判断 | 1500（含 few-shot）| 400 | ~ 0.002 元 |
| P4 苏格拉底 | 800 | 80 | ~ 0.001 元 |
| P5 日记诊断 | 1200 | 500 | ~ 0.0018 元 |
| P6 技能识别 | 600 | 50 | ~ 0.0007 元 |

**单次完整练习（5 轮）成本估算**：~ 0.015 元 = **1.5 分钱/题**

每天 3 题：4.5 分钱/天，月度 1.35 元/月。**用户自己用毫无压力，开源用户接入自己 API key 也能承受**。
