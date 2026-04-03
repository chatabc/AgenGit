# AgenGit - AI Agent 治理与驾驭工程

> 未来有价值的不是"会用 AI"，而是"会驾驭 AI"。

## 项目背景

本项目旨在调研和落地 **Harness Engineering（驾驭工程）** 与 **AI Agent 治理** 相关的技术方案。

AI Agent 正在从"辅助工具"演变为"自主执行者"，但随之而来的安全事故频发（数据删除、数据泄露、自主攻击等）。本项目的目标是：**给 AI Agent 套上缰绳，让 AI 可控、可信、可用。**

## 核心功能

### Phase 1 基础功能
- **执行监控**：实时监控 Agent 执行过程，记录执行历史和日志
- **安全护栏**：检测和阻止危险操作，防止安全事故发生
- **人类干预**：对高风险操作进行人类审核，确保安全执行
- **执行历史**：完整记录执行过程，支持审计和分析
- **安全违规**：记录和分析安全违规行为，持续改进安全策略

### Phase 2 企业级功能
- **Agent 执行防火墙**：智能监控和控制 Agent 执行，包括速率限制、执行时间监控、输出长度检查
- **用户认证与权限管理**：基于 JWT 的身份验证，支持角色权限控制
- **Web 管理界面**：直观的 Web 界面，支持监控、安全管理和用户管理
- **数据库存储**：使用 SQLite 持久化存储执行历史、安全违规记录和用户数据
- **RESTful API**：完整的 API 接口，支持外部系统集成
- **测试套件**：全面的测试用例，确保系统稳定性和可靠性

## 技术架构

### 模块结构
- **agenkit/core/**：核心模块
  - **sdk.py**：HITL SDK 主类
  - **monitor.py**：执行监控模块
  - **guardrail.py**：安全护栏模块
  - **human_in_the_loop.py**：人类干预模块
  - **firewall.py**：Agent 执行防火墙
  - **auth.py**：用户认证与权限管理
  - **db.py**：数据库管理
- **agenkit/examples/**：使用示例
- **agenkit/tests/**：测试套件
- **agenkit/web/**：Web 管理界面
  - **app.py**：Flask Web 应用
  - **templates/**：HTML 模板

### 技术栈
- **语言**：Python 3.7+
- **核心依赖**：
  - Flask：Web 界面和 API 服务
  - PyJWT：JWT 令牌生成和验证
  - SQLite：数据库存储
- **扩展性**：模块化设计，易于集成和扩展

## 安装方法

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/chatabc/AgenGit.git
cd AgenGit

# 安装核心依赖
pip install Flask PyJWT

# 安装包
pip install -e .

# 安装开发依赖（可选）
pip install -e "[dev]"
```

## 快速开始

### 基本使用

```python
from agenkit import HITLSDK

# 创建一个简单的Agent类
class SimpleAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        return f"Result for task: {task}"

# 初始化HITL SDK
config = {
    'monitor': {
        'max_history': 100
    },
    'safety': {
        'forbidden_commands': ['rm -rf', 'delete', 'shutdown'],
        'max_output_length': 1000
    },
    'human_in_the_loop': {
        'require_intervention_for': ['file_write', 'system_command'],
        'always_require_intervention': ['delete', 'rm -rf']
    }
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = SimpleAgent("test-agent")

# 执行任务
result = sdk.execute_agent(agent, "Read configuration file")
print(result)

# 查看执行历史
history = sdk.get_execution_history()
print(history)

# 查看安全违规记录
violations = sdk.get_safety_violations()
print(violations)
```

### 安全规则配置

```python
# 自定义安全规则
config = {
    'safety': {
        'forbidden_commands': ['rm -rf', 'delete', 'shutdown'],
        'forbidden_patterns': [
            r'[0-9]{16}',  # 信用卡号
            r'[0-9]{9,12}',  # 社会安全号
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        ],
        'max_output_length': 10000,
        'max_execution_time': 300  # 5分钟
    }
}
```

### 人类干预配置

```python
# 自定义人类干预规则
config = {
    'human_in_the_loop': {
        'require_intervention_for': ['file_write', 'file_delete', 'network_request'],
        'auto_approve_patterns': ['read', 'get', 'list', 'view'],
        'always_require_intervention': ['delete', 'destroy', 'format']
    }
}
```

### Phase 2 企业级功能使用

#### 用户认证与权限管理

```python
from agenkit import HITLSDK

# 初始化SDK（包含认证配置）
config = {
    'auth': {
        'secret_key': 'your_secret_key_here',
        'roles': {
            'admin': ['*'],
            'user': ['execute', 'view_history'],
            'viewer': ['view_history']
        }
    }
}

sdk = HITLSDK(config)

# 注册用户
sdk.register_user('admin', 'admin123', 'admin')
sdk.register_user('user1', 'user123', 'user')

# 用户登录
login_result = sdk.login('user1', 'user123')
token = login_result['token']

# 使用token执行任务
result = sdk.execute_agent(agent, "Read configuration file", token=token)
print(result)

# 使用token获取执行历史
history = sdk.get_execution_history(token=token)
print(history)
```

#### Web 管理界面

```bash
# 启动Web服务器
python agenkit/web/app.py

# 访问Web界面
# http://localhost:5000
```

#### 数据库功能

```python
from agenkit import HITLSDK

# 初始化SDK（指定数据库路径）
config = {
    'db_path': 'agenkit.db'
}

sdk = HITLSDK(config)

# 执行任务（会自动保存到数据库）
result = sdk.execute_agent(agent, "Read configuration file")
print(result)

# 从数据库获取执行历史
history = sdk.get_execution_history()
print(f"Execution history count: {len(history)}")
```

#### API 接口

```bash
# 启动Web服务器
python agenkit/web/app.py

# 登录获取token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 使用token执行任务
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"task": "Read configuration file"}'

# 获取执行历史
curl http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

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

## 执行路线图

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

## 贡献指南

我们欢迎社区贡献，包括：
- 代码贡献：修复 bug、添加新功能
- 文档完善：更新文档、添加示例
- 安全规则：提供新的安全规则和检测方法
- 集成测试：与其他 Agent 框架的集成

## 许可证

MIT License

## 联系方式

- 项目地址：https://github.com/chatabc/AgenGit
- 团队邮箱：team@agengit.com