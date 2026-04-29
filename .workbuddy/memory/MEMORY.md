# EQ Trainer 长期记忆

## 项目概况
EQ Trainer - 高情商对话训练 Web 应用，6 个 prompt 引擎（P1场景生成/P2角色扮演/P3评分/P4苏格拉底/P5日记诊断/P6技能识别）

## 部署
- **阿里云 ECS**：47.108.174.249:8090
- **SSH**：`admin@47.108.174.249`（admin 可连，root 不行）
- **一键部署**：`ssh admin@47.108.174.249 "cd /var/www/eq-trainer && bash deploy.sh"`
- **部署流程**：git pull → pip install → vite build → cp dist → systemctl restart eq-trainer
- **数据库**：SQLite，`/var/www/eq-trainer/backend/eq_trainer.db`
- **注意**：`admin` 用户需要 `sudo` 操作 `/var/www/` 目录

## 技术栈
- 后端：FastAPI + SQLModel + SQLite + DeepSeek API
- 前端：React + Vite + TypeScript + Tailwind
- AI：DeepSeek chat 模型，OpenAI SDK 调用

## 关键踩坑
- SQLModel `create_all()` 不 ALTER 已有表约束，需手动迁移（db.py 有 `_migrate_nullable_columns`）
- SQLite 不支持 ALTER COLUMN，需重建表
- `or None` 对空字符串有陷阱：`"" or None` → `None`，可能违反 NOT NULL
- P2 角色扮演需要立场红线约束 + 每轮立场自检，否则 AI 会帮用户说话
- 日记 initiate 模式下 `their_words` 为空，必须允许数据库 NULL
