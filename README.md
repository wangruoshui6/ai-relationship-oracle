# AI Relationship Oracle（AI 情感关系顾问）

一个围绕情感关系分析的 AI 顾问系统。

用户可以维护命主与对象资料，并基于八字、心理学、塔罗等分析方式发起咨询，系统会结合关系上下文给出建议与洞察。

---

## 项目简介

这个项目不是通用聊天机器人，也不是单纯算命工具。

它的定位是：

> 一个以情感关系为核心，以人物档案为输入，以多分析维度为辅助，以 AI 咨询为输出的关系顾问系统。

当前仓库包含：

- `backend/`：后端服务（FastAPI + SQLAlchemy + Alembic）
- `frontend/`：前端应用（Vue 3 + Vite + Pinia）
- `prompts/`：Prompt 资产
- `docs/`：项目文档

---

## 目录结构

```text
agent算命/
├── backend/               # 后端工程
├── frontend/              # 前端工程
├── prompts/               # Prompt 资产
├── docs/                  # 项目文档
├── README.md
└── .gitignore
```

---

## 开发环境

建议环境：

- Python 3.11+
- Node.js 18+
- npm 9+

后端默认使用：

- FastAPI
- SQLAlchemy
- Alembic
- SQLite（默认 `backend/dev.db`）

前端默认使用：

- Vue 3
- Vite
- Pinia
- Axios

---

## 后端运行方式

进入后端目录：

```powershell
cd "d:\code.agent\agent算命\backend"
```

如果你使用项目虚拟环境，推荐这样启动：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

默认后端地址：

```text
http://127.0.0.1:8000
```

### 数据库迁移

如果后端模型或表结构有更新，请先执行迁移：

```powershell
cd "d:\code.agent\agent算命\backend"
.\.venv\Scripts\python.exe -m alembic.config upgrade head
```

如果你已经激活虚拟环境，也可以直接执行：

```powershell
alembic upgrade head
```

---

## 前端运行方式

进入前端目录：

```powershell
cd "d:\code.agent\agent算命\frontend"
```

安装依赖：

```powershell
npm install
```

启动开发环境：

```powershell
npm run dev
```

Vite 默认端口配置为：

```text
5173
```

如果 `5173` 已被占用，Vite 可能自动切换到 `5174` 或其他可用端口。

---

## 当前功能概览

当前版本已包含基础可运行能力：

- 用户登录 / 注册
- 命主资料维护
- 对象资料维护
- 单页咨询工作台
- 八字 / 心理学 / 塔罗分析方式选择
- 流式咨询返回

---

## 开发说明

### 前后端启动顺序

推荐顺序：

1. 启动后端
2. 执行数据库迁移（如有结构变更）
3. 启动前端

### 常见问题

#### 1. 前端端口不是 5173

这通常表示已经有另一个 Vite 实例占用了 `5173`，新实例自动切换到了其他端口。

#### 2. 新增字段不生效

如果前后端代码都更新了，但数据库里没有对应字段，请先执行 Alembic migration。

---

## 备注

当前仓库已经进入可运行开发阶段，README 主要用于帮助开发者快速理解项目与完成本地启动。
