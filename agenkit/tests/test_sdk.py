import unittest
import os
from agenkit import HITLSDK
from agenkit.core.db import DatabaseManager

class TestHITLSDK(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        # 使用临时数据库文件
        self.db_path = 'test_agenkit.db'
        self.sdk = HITLSDK({
            'auth': {
                'secret_key': 'test_secret_key',
                'roles': {
                    'admin': ['*'],
                    'user': ['execute', 'view_history'],
                    'viewer': ['view_history']
                }
            },
            'db_path': self.db_path
        })
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库文件
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_execute_agent(self):
        """测试执行Agent任务"""
        # 创建测试Agent
        class TestAgent:
            def execute(self, task, context=None):
                return f"Test result for: {task}"
        
        agent = TestAgent()
        task = "Test task"
        
        # 测试无token执行
        result = self.sdk.execute_agent(agent, task)
        self.assertEqual(result['status'], 'completed')
        self.assertIn('Test result for: Test task', result['result'])
        self.assertIn('execution_id', result)
    
    def test_get_execution_history(self):
        """测试获取执行历史"""
        # 先执行一个任务
        class TestAgent:
            def execute(self, task, context=None):
                return f"Test result"
        
        agent = TestAgent()
        self.sdk.execute_agent(agent, "Test task for history")
        
        # 获取历史
        history = self.sdk.get_execution_history(limit=10)
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
    
    def test_register_user(self):
        """测试注册用户"""
        result = self.sdk.register_user('testuser_unique', 'testpassword', 'user')
        self.assertTrue(result['success'])
        self.assertEqual(result['username'], 'testuser_unique')
        self.assertEqual(result['role'], 'user')
    
    def test_login(self):
        """测试用户登录"""
        # 先注册用户
        self.sdk.register_user('testuser2_unique', 'testpassword', 'user')
        
        # 测试登录
        result = self.sdk.login('testuser2_unique', 'testpassword')
        self.assertTrue(result['success'])
        self.assertIn('token', result)
        self.assertEqual(result['username'], 'testuser2_unique')
    
    def test_verify_token(self):
        """测试验证token"""
        # 注册并登录获取token
        self.sdk.register_user('testuser3_unique', 'testpassword', 'user')
        login_result = self.sdk.login('testuser3_unique', 'testpassword')
        token = login_result['token']
        
        # 验证token
        verify_result = self.sdk.verify_token(token)
        self.assertTrue(verify_result['valid'])
        self.assertEqual(verify_result['username'], 'testuser3_unique')
    
    def test_get_active_executions(self):
        """测试获取活跃执行"""
        active = self.sdk.get_active_executions()
        self.assertIsInstance(active, list)
    
    def test_update_firewall_rules(self):
        """测试更新防火墙规则"""
        new_rules = {
            'max_execution_time': 600,
            'max_output_length': 20000
        }
        result = self.sdk.update_firewall_rules(new_rules)
        self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main()