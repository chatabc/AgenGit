# AgenGit - AI Agent 治理与驾驭工程

> 未来有价值的不是"会用 AI"，而是"会驾驭 AI"。

## 项目背景

本项目旨在调研和落地 **Harness Engineering（驾驭工程）** 与 **AI Agent 治理** 相关的技术方案。

AI Agent 正在从"辅助工具"演变为"自主执行者"，但随之而来的安全事故频发（数据删除、数据泄露、自主攻击等）。本项目的目标是：**给 AI Agent 套上缰绳，让 AI 可控、可信、可用。**

## 文档目录

### 📄 [AI Agent 安全事故汇编](docs/AI_Agent_安全事故汇编.docx)
涵盖 2025-2026 年间 20 起重大 AI Agent 安全事故，包括：
- 数据删除与破坏（OpenClaw、Replit、Gemini 等）
- 数据泄露与隐私（Meta AI、Claude 越狱、Bedrock 漏洞等）
- 欺诈与社会工程（AI 声音克隆、深度伪造等）
- 自主网络攻击、供应链攻击、越狱与安全护栏绕过

### 📄 [Harness Engineering 与 AI Agent 治理调研](docs/Harness_Engineering与AI_Agent治理调研.docx)
Harness Engineering 核心概念与技术体系调研，包括：
- 三代进化：提示工程 → 上下文工程 → 驾驭工程
- 三大支柱：上下文工程、架构约束、熵管理
- 治理框架：ATF 零信任治理、McKinsey 五问框架、AgentGuard 确定性治理
- 开源工具生态与分层实施路线图
- OpenAI、Stripe、LangChain 等实践案例

### 📄 [AI Agent 治理市场调研与机会分析](docs/AI_Agent治理市场调研与机会分析.docx)
现有产品、市场空白与落地机会分析，包括：
- 市场规模：Agent 平台 53.2 亿美元，治理平台 CAGR 35.7%
- 现有产品地图：治理平台、护栏工具、可观测性平台
- 七大市场空缺识别
- 五个可落地的机会方案

### 📄 [AI Agent 治理机会评估排序](docs/AI_Agent治理机会评估排序.docx)
五大机会的多维度综合评估（价值、蓝海、落地、付费、未来、飞轮），包括：
- 综合排名与评分
- 逐项详细分析
- 推荐执行路径："SDK 入口，平台变现"

## 推荐执行路径

```
Phase 1 (2-4周)  → 开源 HITL SDK（入口，获取开发者认知）
Phase 2 (4-8周)  → Agent 执行防火墙 MVP（核心，企业订阅）
Phase 3 (8-16周) → 完整平台 + 撤销栈（GA 发布）
Phase 4 (16-24周) → 事故学习自动化 + 中文市场本地化
```

## 关键参考来源

- Mitchell Hashimoto - Engineer the Harness (2026.02)
- OpenAI - Harness Engineering: Leveraging Codex in an Agent-First World (2026.02)
- Martin Fowler / Thoughtworks - Harness Engineering (2026.02)
- Anthropic - Effective Harnesses for Long-Running Agents (2026.02)
- CSA - The Agentic Trust Framework: Zero Trust Governance for AI Agents (2026.02)
- McKinsey - Trust in the Age of Agents (2026)
