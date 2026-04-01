from agenkit import HITLSDK
from autogen import AssistantAgent, UserProxyAgent

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

# 初始化AutoGen代理
assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "model": "gpt-4",
        "temperature": 0
    }
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="You are a user proxy.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False
)

# 创建一个包装类，使AutoGen代理符合HITL SDK的接口
class AutoGenAgentWrapper:
    def __init__(self, assistant_agent, user_proxy_agent):
        self.assistant = assistant_agent
        self.user_proxy = user_proxy_agent
    
    def execute(self, task, context=None):
        """执行任务"""
        try:
            # 启动对话
            result = self.user_proxy.initiate_chat(
                self.assistant,
                message=task,
                silent=True
            )
            # 获取对话历史的最后一条消息
            if result and hasattr(result, 'chat_history'):
                last_message = result.chat_history[-1]
                return last_message.get('content', str(result))
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

# 包装AutoGen代理
wrapped_agent = AutoGenAgentWrapper(assistant, user_proxy)

# 测试1: 正常任务
print("\n=== Test 1: Normal task ===")
task1 = "计算12345的平方根"
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