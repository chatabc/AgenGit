from agenkit import HITLSDK

# 创建一个简单的Agent
class SimpleAgent:
    def __init__(self, name):
        self.name = name
    
    def execute(self, task, context=None):
        """执行任务"""
        print(f"Agent {self.name} executing task: {task}")
        return f"Result: {task}"

# 初始化HITL SDK，使用数据库
config = {
    'db_path': 'test_agenkit.db'
}

sdk = HITLSDK(config)

# 创建Agent实例
agent = SimpleAgent("test-agent")

# 测试1: 执行任务并保存到数据库
print("\n=== Test 1: Execute task and save to database ===")
task1 = "Read configuration file"
result1 = sdk.execute_agent(agent, task1)
print(f"Result: {result1}")

# 测试2: 从数据库获取执行历史
print("\n=== Test 2: Get execution history from database ===")
history = sdk.get_execution_history()
print(f"Execution history count: {len(history)}")
for record in history:
    print(f"ID: {record['execution_id']}, Status: {record['status']}, Task: {record['task']}")

# 测试3: 注册用户并保存到数据库
print("\n=== Test 3: Register user and save to database ===")
register_result = sdk.register_user('testuser', 'password123', 'user')
print(f"Register result: {register_result}")

# 测试4: 用户登录
print("\n=== Test 4: User login ===")
login_result = sdk.login('testuser', 'password123')
print(f"Login result: {login_result}")

# 测试5: 获取所有用户
print("\n=== Test 5: Get all users ===")
users = sdk.auth.get_users()
print(f"Users count: {len(users)}")
for user in users:
    print(f"Username: {user['username']}, Role: {user['role']}")

# 测试6: 获取所有角色
print("\n=== Test 6: Get all roles ===")
roles = sdk.auth.get_roles()
print(f"Roles: {roles}")

print("\n=== Database test completed ===")