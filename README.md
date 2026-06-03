# AI Relationship Oracle（AI 情感关系顾问）

一个围绕情感关系分析的 AI 顾问系统。

用户输入自己和对象的基础信息后即可直接提问，系统会自动识别对象、建立关系记忆，并结合八字、心理学、塔罗、RAG 和长期关系上下文，输出结构化关系洞察与行动建议。

---

## 项目定位

这个项目不是通用聊天机器人，也不是单纯算命工具。

它的核心定位是：

> 一个以情感关系为核心，以基础档案为输入，以 AI 关系记忆为中枢，以多分析维度为辅助，以行动建议为输出的 AI 顾问系统。

当前已经明确的核心能力包括：

- 首次咨询自动建档
- 按 Partner 维度维护长期关系记忆
- 支持八字 / 心理学 / 塔罗多维分析
- 聊天与正式报告分离
- 通过 Harness + Ragas 进行离线评测

---

## 当前目录结构

```text
agent算命/
├── docs/                  # 项目文档（00-15）
├── prompts/               # Prompt 资产
│   ├── global/
│   ├── nodes/
│   └── scenes/
├── backend/               # 后端工程（待继续落地）
├── frontend/              # 前端工程（待继续落地）
├── evaluation/            # 评测体系（待继续落地）
├── scripts/               # 辅助脚本
├── assets/                # 静态资源
├── output/                # 导出与运行产物
├── README.md
└── .gitignore
```

---

## 已完成内容

### 1. 项目文档基线

`docs/` 目录下已完成 00–15 文档，覆盖：

- 产品边界
- 系统架构
- 数据模型
- Agent 工作流
- Prompt 设计规范
- API 设计
- 页面说明
- 测试案例
- 执行计划

### 2. 第一批 Prompt 已落地

当前已创建的核心 Prompt：

- `prompts/global/system_base_prompt.md`
- `prompts/nodes/intent_router_prompt.md`
- `prompts/nodes/entity_extractor_prompt.md`
- `prompts/scenes/relationship_analysis_prompt.md`

这些 Prompt 是当前系统的第一版 Prompt 资产基线。

---

## 当前架构摘要

### 线上主链路

```text
用户输入
  ↓
Intent Router
  ↓
Entity Extractor
  ↓
Profile Loader
  ↓
Memory Loader
  ↓
Tool Router
  ├─ Bazi Engine
  ├─ Psychology Engine
  └─ Tarot Engine
  ↓
Knowledge RAG
  ↓
Compatibility Engine
  ↓
Prompt Builder
  ↓
LLM Generator
  ↓
Persist Result
```

### 数据分层

```text
Profile（事实档案）
+
Memory（AI 关系记忆）
+
Output（正式输出）
```

---

## 下一步计划

当前推荐的推进顺序：

1. 补齐剩余核心 Prompt
2. 搭建后端工程骨架
3. 建立数据库模型与 API schema
4. 实现 LangGraph state 与工作流节点
5. 接入评测框架

近期最优先的 Prompt 包括：

- `event_detector_prompt`
- `memory_update_prompt`
- `general_guidance_prompt`
- `report_builder_prompt`

---

## 开发原则

- 文档先行，代码落地
- Prompt 视为核心资产
- 关系事实优先于玄学推断
- 报告与聊天分离
- 所有 Prompt / Router / Memory / RAG 改动尽量进入评测回归

---

## 备注

当前仓库正处于：

```text
架构已收敛，准备进入实现阶段
```

后续将从文档驱动逐步过渡到工程实现驱动。
