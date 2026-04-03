import unittest
import os
from agenkit.core.db import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        # 使用临时数据库文件
        self.db_path = 'test_agenkit.db'
        self.db = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库文件
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_create_tables(self):
        """测试创建数据库表"""
        # 表应该在初始化时自动创建
        # 这里我们通过执行一个插入操作来验证表是否存在
        execution_record = {
            'execution_id': 'test-123',
            'agent': 'TestAgent',
            'task': 'Test task',
            'context': None,
            'start_time': '2024-01-01T00:00:00',
            'end_time': '2024-01-01T00:00:01',
            'status': 'completed',
            'reason': 'success',
            'result': 'Test result',
            'duration': 1.0
        }
        
        result = self.db.insert_execution(execution_record)
        self.assertTrue(result)
    
    def test_insert_execution(self):
        """测试插入执行记录"""
        execution_record = {
            'execution_id': 'test-456',
            'agent': 'TestAgent',
            'task': 'Test task 2',
            'context': {'key': 'value'},
            'start_time': '2024-01-01T00:00:00',
            'end_time': '2024-01-01T00:00:02',
            'status': 'completed',
            'reason': 'success',
            'result': 'Test result 2',
            'duration': 2.0
        }
        
        result = self.db.insert_execution(execution_record)
        self.assertTrue(result)
        
        # 验证记录是否插入成功
        executions = self.db.get_executions(limit=10)
        self.assertGreater(len(executions), 0)
        self.assertEqual(executions[0]['execution_id'], 'test-456')
    
    def test_insert_violation(self):
        """测试插入安全违规记录"""
        violation_record = {
            'violation_id': 'violation-123',
            'execution_id': 'test-789',
            'violation_type': 'test_violation',
            'details': 'Test violation details',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        result = self.db.insert_violation(violation_record)
        self.assertTrue(result)
        
        # 验证记录是否插入成功
        violations = self.db.get_violations(limit=10)
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0]['type'], 'test_violation')
        self.assertEqual(violations[0]['reason'], 'Test violation details')
    
    def test_get_executions(self):
        """测试获取执行记录"""
        # 插入多条记录
        for i in range(3):
            execution_record = {
                'execution_id': f'test-{i}',
                'agent': 'TestAgent',
                'task': f'Test task {i}',
                'context': None,
                'start_time': '2024-01-01T00:00:00',
                'end_time': '2024-01-01T00:00:01',
                'status': 'completed',
                'reason': 'success',
                'result': f'Test result {i}',
                'duration': 1.0
            }
            self.db.insert_execution(execution_record)
        
        # 获取记录
        executions = self.db.get_executions(limit=2)
        self.assertEqual(len(executions), 2)
    
    def test_get_violations(self):
        """测试获取安全违规记录"""
        # 插入多条记录
        for i in range(3):
            violation_record = {
                'violation_id': f'violation-{i}',
                'execution_id': f'test-{i}',
                'violation_type': 'test_violation',
                'details': f'Test violation details {i}',
                'timestamp': '2024-01-01T00:00:00'
            }
            self.db.insert_violation(violation_record)
        
        # 获取记录
        violations = self.db.get_violations(limit=2)
        self.assertEqual(len(violations), 2)
    
    def test_get_users(self):
        """测试获取用户记录"""
        # 插入用户记录
        user_data = {
            'username': 'testuser',
            'password': 'testhash',
            'role': 'user',
            'created_at': '2024-01-01T00:00:00'
        }
        self.db.insert_user(user_data)
        
        # 获取用户
        users = self.db.get_users()
        self.assertGreater(len(users), 0)
        self.assertEqual(users[0]['username'], 'testuser')

if __name__ == '__main__':
    unittest.main()