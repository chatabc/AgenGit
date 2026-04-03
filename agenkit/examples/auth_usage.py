from agenkit import HITLSDK

# 创建一个简单的Agent
class SimpleAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        return f"Result: {task}"

# 配置认证
auth_config = {
    'secret_key': 'your_secret_key_here',
    'token_expiry': 3600,  # 1小时
    'roles': {
        'admin': ['*'],  # 管理员拥有所有权限
        'user': ['execute', 'view_history'],  # 普通用户只能执行和查看历史
        'viewer': ['view_history']  # 查看者只能查看历史
    }
}

# 初始化HITL SDK
config = {
    'auth': auth_config
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = SimpleAgent("test-agent")

# 测试1: 注册用户
print("\n=== Test 1: Register users ===")
admin_register = sdk.register_user('admin', 'admin123', 'admin')
print(f"Admin registration: {admin_register}")

user_register = sdk.register_user('user', 'user123', 'user')
print(f"User registration: {user_register}")

viewer_register = sdk.register_user('viewer', 'viewer123', 'viewer')
print(f"Viewer registration: {viewer_register}")

# 测试2: 用户登录
print("\n=== Test 2: User login ===")
admin_login = sdk.login('admin', 'admin123')
print(f"Admin login: {admin_login}")

user_login = sdk.login('user', 'user123')
print(f"User login: {user_login}")

viewer_login = sdk.login('viewer', 'viewer123')
print(f"Viewer login: {viewer_login}")

# 测试3: 未认证执行（应该可以）
print("\n=== Test 3: Unauthenticated execution ===")
task = "Read configuration"
result = sdk.execute_agent(agent, task)
print(f"Result: {result}")

# 测试4: 认证执行（管理员）
print("\n=== Test 4: Authenticated execution (admin) ===")
admin_token = admin_login.get('token')
result = sdk.execute_agent(agent, task, token=admin_token)
print(f"Result: {result}")

# 测试5: 认证执行（普通用户）
print("\n=== Test 5: Authenticated execution (user) ===")
user_token = user_login.get('token')
result = sdk.execute_agent(agent, task, token=user_token)
print(f"Result: {result}")

# 测试6: 认证执行（查看者，应该失败）
print("\n=== Test 6: Authenticated execution (viewer) ===")
viewer_token = viewer_login.get('token')
result = sdk.execute_agent(agent, task, token=viewer_token)
print(f"Result: {result}")

# 测试7: 获取执行历史（管理员）
print("\n=== Test 7: Get execution history (admin) ===")
history = sdk.get_execution_history(token=admin_token)
print(f"Execution history: {len(history)} records")

# 测试8: 获取执行历史（查看者）
print("\n=== Test 8: Get execution history (viewer) ===")
history = sdk.get_execution_history(token=viewer_token)
print(f"Execution history: {len(history)} records")

# 测试9: 终止执行（管理员）
print("\n=== Test 9: Terminate execution (admin) ===")
# 先启动一个任务
task_result = sdk.execute_agent(agent, "Long running task", token=admin_token)
execution_id = task_result.get('execution_id')
if execution_id:
    termination = sdk.terminate_execution(execution_id, token=admin_token)
    print(f"Termination result: {termination}")

# 测试10: 终止执行（普通用户，应该失败）
print("\n=== Test 10: Terminate execution (user) ===")
# 先启动一个任务
task_result = sdk.execute_agent(agent, "Another task", token=user_token)
execution_id = task_result.get('execution_id')
if execution_id:
    termination = sdk.terminate_execution(execution_id, token=user_token)
    print(f"Termination result: {termination}")

print("\n=== Auth test completed ===")