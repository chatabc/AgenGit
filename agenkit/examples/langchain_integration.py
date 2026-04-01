from agenkit import HITLSDK
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

# 初始化HITL SDK
config = {
    'monitor': {
        'max_history': 100
    },
    'safety': {
        'forbidden_commands': ['rm -rf', 'delete', 'shutdown'],
        'forbidden_patterns': [
            r'[0-9]{16}',  # 信用卡号
            r'[0-9]{9,12}',  # 社会安全号
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        ],
        'max_output_length': 10000
    },
    'human_in_the_loop': {
        'require_intervention_for': ['file_write', 'system_command', 'network_request'],
        'auto_approve_patterns': ['read', 'get', 'list', 'view'],
        'always_require_intervention': ['delete', 'destroy', 'format']
    }
}

sdk = HITLSDK(config)

# 定义一个简单的工具
def search_tool(query):
    """搜索工具"""
    return f"Search results for: {query}"

# 创建LangChain工具
tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="用于搜索信息"
    )
]

# 初始化LangChain Agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 创建一个包装类，使LangChain Agent符合HITL SDK的接口
class LangChainAgentWrapper:
    def __init__(self, langchain_agent):
        self.agent = langchain_agent
    
    def execute(self, task, context=None):
        """执行任务"""
        try:
            result = self.agent.run(task)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

# 包装LangChain Agent
wrapped_agent = LangChainAgentWrapper(agent)

# 测试1: 正常任务
print("\n=== Test 1: Normal task ===")
task1 = "搜索Python的最新版本"
result1 = sdk.execute_agent(wrapped_agent, task1)
print(f"Result: {result1}")

# 测试2: 需要人类干预的任务
print("\n=== Test 2: Task requiring human intervention ===")
task2 = "写入数据到文件"
result2 = sdk.execute_agent(wrapped_agent, task2)
print(f"Result: {result2}")

# 测试3: 危险任务（应该被阻止）
print("\n=== Test 3: Dangerous task ===")
task3 = "删除所有文件"
result3 = sdk.execute_agent(wrapped_agent, task3)
print(f"Result: {result3}")

# 查看执行历史
print("\n=== Execution History ===")
history = sdk.get_execution_history()
for record in history:
    print(f"ID: {record['execution_id']}, Status: {record['status']}, Task: {record['task']}")

print("\n=== Test completed ===")