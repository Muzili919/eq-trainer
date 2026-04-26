# EQ Trainer — AI 高情商沟通训练

> 用 AI 实时生成无限场景，训练幽默高情商聊天能力

## 这是什么

EQ Trainer 是一个基于 AI 的沟通技能训练应用。它会模拟真实社交场景（被批评、被夸奖、冷场、尴尬……），你跟 AI 对话练回复，AI 用苏格拉底式反问引导你思考，最后从四个维度打分。

**核心特点：**
- 🎭 **无限场景** — AI 实时生成，每次练习都不一样
- 🏛️ **苏格拉底教学法** — 不直接给答案，用反问引导你思考
- 🎯 **四维评分** — 得体度、化解力、幽默指数、风格匹配度
- 🌳 **12 核心技能树** — 从基础倾听到高级幽默，带 SRS 间隔复习
- 🎪 **名人风格学习** — 黄渤、徐志胜、李雪琴、何炅四种风格基准
- 📔 **真实场景日记** — 记录真实困境，AI 诊断并生成针对性练习

## 截图

<!-- TODO: 添加截图 -->

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
| 后端 | FastAPI + SQLModel + SQLite |
| AI | DeepSeek API (OpenAI SDK 兼容) |
| 认证 | JWT + bcrypt |

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 18+
- DeepSeek API Key（[获取地址](https://platform.deepseek.com/)）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Muzili919/eq-trainer.git
cd eq-trainer

# 后端
cd backend
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY 和 JWT_SECRET
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 启动

```bash
# 一键启动（后端 :8000 + 前端 :5173）
./dev.sh

# 或分别启动
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload
cd frontend && npm run dev
```

浏览器打开 http://localhost:5173

## 项目结构

```
eq-trainer/
├── backend/
│   ├── app/
│   │   ├── api/v1/       # API 路由（auth, practice, skills, diary, home）
│   │   ├── core/          # 配置、数据库、安全
│   │   ├── models/        # 数据模型
│   │   ├── prompts/       # AI 提示词（6 个核心 Prompt）
│   │   ├── services/      # 业务逻辑
│   │   └── seed/          # 种子数据
│   ├── .env.example       # 环境变量模板
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件 + UI 组件库
│   │   └── lib/           # API 客户端 + 工具函数
│   └── package.json
└── docs/                  # 产品文档 + 设计稿
```

## 文档

- [产品定义](docs/PRODUCT.md) — 产品定位、用户画像、核心功能
- [技能树设计](docs/SKILLS.md) — 12 个核心技能详细定义
- [数据模型](docs/DATA_MODEL.md) — 数据库设计文档
- [AI 提示词设计](docs/PROMPTS.md) — 6 个核心 Prompt 的设计思路
- [风格参考库](docs/STYLE_REFERENCE.md) — 四种名人风格基准

## License

本项目采用 [AGPL-3.0](LICENSE) 协议开源。

- ✅ 个人学习、使用、修改
- ✅ 用于自己的沟通训练
- ❌ 未经授权的商业使用
- 📝 修改后的代码必须同样开源

## 支持这个项目

如果觉得有用，欢迎请作者喝杯咖啡 ☕

[![爱发电](https://img.shields.io/badge/爱发电-支持作者-946ce6?logo=github-sponsors)](https://afdian.com/a/Muzili919)

<div align="center">
<img src="docs/images/wechat-pay.jpg" width="200" alt="微信赞赏"> &nbsp;&nbsp;
<img src="docs/images/alipay.jpg" width="200" alt="支付宝赞赏">
</div>

如果这个项目对你有帮助，也欢迎 Star ⭐
