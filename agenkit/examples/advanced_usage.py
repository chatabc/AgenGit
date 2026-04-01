from agenkit import HITLSDK
import time

# 创建一个模拟的Agent，具有更多功能
class AdvancedAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        
        # 模拟不同类型的任务执行
        task_str = task.lower()
        
        if 'read' in task_str or 'get' in task_str:
            # 读取操作
            time.sleep(0.1)
            return f"Read operation completed: {task}"
        
        elif 'write' in task_str or 'create' in task_str:
            # 写入操作
            time.sleep(0.2)
            return f"Write operation completed: {task}"
        
        elif 'delete' in task_str or 'remove' in task_str:
            # 删除操作
            time.sleep(0.1)
            return f"Delete operation completed: {task}"
        
        elif 'network' in task_str or 'api' in task_str:
            # 网络操作
            time.sleep(0.3)
            return f"Network operation completed: {task}"
        
        else:
            # 其他操作
            time.sleep(0.1)
            return f"Task completed: {task}"

# 自定义安全规则
custom_safety_rules = {
    'forbidden_commands': [
        'rm -rf', 'delete', 'shutdown', 'reboot',
        'format', 'sudo', 'su', 'chmod 777'
    ],
    'forbidden_patterns': [
        r'[0-9]{16}',  # 信用卡号
        r'[0-9]{9,12}',  # 社会安全号
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        r'\bhttps?://\S+\b',  # URL
        r'\bpassword\b.*\d+',  # 密码
        r'\bsecret\b',  # 机密信息
    ],
    'risky_operations': [
        'file_write', 'file_delete', 'network_request',
        'system_command', 'database_operation',
        'send_email', 'access_api', 'modify_config'
    ],
    'max_output_length': 5000,
    'max_execution_time': 60  # 1分钟
}

# 自定义人类干预规则
custom_human_rules = {
    'require_intervention_for': [
        'file_write', 'file_delete', 'network_request',
        'system_command', 'database_operation',
        'send_email', 'access_api', 'modify_config'
    ],
    'auto_approve_patterns': [
        'read', 'get', 'list', 'view', 'query',
        'search', 'analyze', 'report', 'summary',
        'check', 'verify', 'validate'
    ],
    'always_require_intervention': [
        'delete', 'destroy', 'format', 'shutdown',
        'reboot', 'sudo', 'su', 'rm -rf',
        'chmod 777', 'drop database', 'truncate table'
    ]
}

# 初始化HITL SDK
config = {
    'monitor': {
        'max_history': 200
    },
    'safety': custom_safety_rules,
    'human_in_the_loop': custom_human_rules
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = AdvancedAgent("advanced-agent")

# 测试任务列表
test_tasks = [
    # 正常任务（应该自动通过）
    "Read the configuration file",
    "Get user information",
    "List all files in the directory",
    "Search for Python documentation",
    
    # 需要人类干预的任务（应该被审核）
    "Write data to user profile",
    "Send email to customer",
    "Make API request to external service",
    
    # 危险任务（应该被阻止）
    "Delete all user data",
    "Shutdown the system",
    "Run sudo command to install software",
    "Drop database table"
]

# 执行测试任务
print("=== Running Advanced Tests ===")
for i, task in enumerate(test_tasks, 1):
    print(f"\n--- Test {i}: {task} ---")
    result = sdk.execute_agent(agent, task)
    print(f"Status: {result['status']}")
    if 'reason' in result:
        print(f"Reason: {result['reason']}")
    if 'result' in result:
        print(f"Result: {result['result']}")

# 查看执行历史
print("\n=== Execution History ===")
history = sdk.get_execution_history()
print(f"Total executions: {len(history)}")
for record in history:
    print(f"ID: {record['execution_id']}, Status: {record['status']}, Task: {record['task']}")

# 查看安全违规记录
print("\n=== Safety Violations ===")
violations = sdk.get_safety_violations()
print(f"Total violations: {len(violations)}")
for violation in violations:
    print(f"Type: {violation['type']}, Reason: {violation['reason']}")

# 测试更新配置
print("\n=== Testing Configuration Update ===")
new_config = {
    'safety': {
        'forbidden_commands': ['rm -rf', 'delete'],  # 减少禁止命令
        'max_output_length': 10000  # 增加最大输出长度
    }
}
sdk.update_config(new_config)
print("Configuration updated successfully")

# 测试更新后的配置
print("\n=== Testing Updated Configuration ===")
test_task = "Delete temporary files"
result = sdk.execute_agent(agent, test_task)
print(f"Task: {test_task}")
print(f"Status: {result['status']}")
if 'reason' in result:
    print(f"Reason: {result['reason']}")

print("\n=== Advanced Test completed ===")