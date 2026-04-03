from agenkit import HITLSDK
import time

# 创建一个模拟的Agent
class TestAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        
        # 模拟不同执行时间的任务
        task_str = task.lower()
        
        if 'long' in task_str:
            # 长时间运行的任务
            time.sleep(2)  # 2秒
            return f"Long running task completed: {task}"
        elif 'output' in task_str:
            # 大量输出的任务
            return "X" * 15000  # 15000个字符
        else:
            # 正常任务
            time.sleep(0.1)
            return f"Task completed: {task}"

# 配置防火墙
firewall_config = {
    'max_execution_time': 1,  # 1秒
    'max_output_length': 10000,  # 10000字符
    'blocked_operations': ['delete', 'shutdown'],
    'rate_limit': 3  # 每分钟最多3次执行
}

# 初始化HITL SDK
config = {
    'monitor': {
        'max_history': 100
    },
    'safety': {
        'forbidden_commands': ['rm -rf', 'delete', 'shutdown']
    },
    'firewall': firewall_config
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = TestAgent("test-agent")

# 测试1: 正常任务
print("\n=== Test 1: Normal task ===")
task1 = "Read configuration file"
result1 = sdk.execute_agent(agent, task1)
print(f"Result: {result1}")

# 测试2: 长时间运行的任务（应该被防火墙终止）
print("\n=== Test 2: Long running task ===")
task2 = "Run long running task"
result2 = sdk.execute_agent(agent, task2)
print(f"Result: {result2}")

# 测试3: 大量输出的任务（应该被防火墙阻止）
print("\n=== Test 3: Task with large output ===")
task3 = "Generate large output"
result3 = sdk.execute_agent(agent, task3)
print(f"Result: {result3}")

# 测试4: 速率限制测试
print("\n=== Test 4: Rate limit test ===")
for i in range(5):
    task4 = f"Test rate limit {i+1}"
    result4 = sdk.execute_agent(agent, task4)
    print(f"Test {i+1}: {result4['status']}")
    if not result4['status'] == 'completed':
        break
    time.sleep(0.1)

# 测试5: 获取活跃执行
print("\n=== Test 5: Get active executions ===")
active = sdk.get_active_executions()
print(f"Active executions: {active}")

# 测试6: 终止执行（先启动一个长时间任务）
print("\n=== Test 6: Terminate execution ===")
task6 = "Run another long task"
result6 = sdk.execute_agent(agent, task6)
print(f"Task started: {result6}")

# 等待一下，确保任务在运行
import time
import threading

def terminate_after_delay():
    time.sleep(0.5)
    if 'execution_id' in result6:
        termination = sdk.terminate_execution(result6['execution_id'])
        print(f"Termination result: {termination}")

# 启动线程来终止任务
terminate_thread = threading.Thread(target=terminate_after_delay)
terminate_thread.daemon = True
terminate_thread.start()

# 等待任务完成
while True:
    status = sdk.get_execution_status(result6.get('execution_id'))
    if status and status['status'] != 'running':
        print(f"Final status: {status['status']}")
        break
    time.sleep(0.1)

# 测试7: 更新防火墙规则
print("\n=== Test 7: Update firewall rules ===")
new_rules = {
    'max_execution_time': 5,  # 增加到5秒
    'rate_limit': 10  # 增加到10次/分钟
}
update_result = sdk.update_firewall_rules(new_rules)
print(f"Rule update result: {update_result}")

# 测试更新后的规则
print("\n=== Test 8: Test updated rules ===")
task8 = "Run task with updated rules"
result8 = sdk.execute_agent(agent, task8)
print(f"Result: {result8}")

print("\n=== Firewall test completed ===")