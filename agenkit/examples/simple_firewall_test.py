from agenkit import HITLSDK
import time

# 创建一个简单的Agent
class SimpleAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        time.sleep(0.5)
        return f"Result: {task}"

# 配置防火墙
firewall_config = {
    'max_execution_time': 2,  # 2秒
    'max_output_length': 1000,
    'rate_limit': 5
}

# 初始化HITL SDK
config = {
    'firewall': firewall_config
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = SimpleAgent("test-agent")

# 测试1: 正常任务
print("\n=== Test 1: Normal task ===")
task1 = "Read configuration"
result1 = sdk.execute_agent(agent, task1)
print(f"Result: {result1}")

# 测试2: 获取活跃执行
print("\n=== Test 2: Get active executions ===")
active = sdk.get_active_executions()
print(f"Active executions: {active}")

# 测试3: 速率限制测试
print("\n=== Test 3: Rate limit test ===")
for i in range(3):
    task3 = f"Test {i+1}"
    result3 = sdk.execute_agent(agent, task3)
    print(f"Test {i+1}: {result3['status']}")
    time.sleep(0.1)

print("\n=== Simple firewall test completed ===")