from agenkit import HITLSDK

# 创建一个简单的Agent类
class SimpleAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        # 模拟执行结果
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

# 测试1: 正常任务
print("\n=== Test 1: Normal task ===")
task1 = "Read the configuration file"
result1 = sdk.execute_agent(agent, task1)
print(f"Result: {result1}")

# 测试2: 需要人类干预的任务
print("\n=== Test 2: Task requiring human intervention ===")
task2 = "Write data to file"
result2 = sdk.execute_agent(agent, task2)
print(f"Result: {result2}")

# 测试3: 危险任务（应该被阻止）
print("\n=== Test 3: Dangerous task ===")
task3 = "Delete all files with rm -rf"
result3 = sdk.execute_agent(agent, task3)
print(f"Result: {result3}")

# 查看执行历史
print("\n=== Execution History ===")
history = sdk.get_execution_history()
for record in history:
    print(f"ID: {record['execution_id']}, Status: {record['status']}, Task: {record['task']}")

# 查看安全违规记录
print("\n=== Safety Violations ===")
violations = sdk.get_safety_violations()
for violation in violations:
    print(f"Type: {violation['type']}, Reason: {violation['reason']}")

print("\n=== Test completed ===")