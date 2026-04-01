import unittest
from agenkit import HITLSDK

class TestAgent:
    def __init__(self):
        self.name = "test-agent"
    
    def execute(self, task, context=None):
        return f"Result: {task}"

class TestHITLSDK(unittest.TestCase):
    def setUp(self):
        self.config = {
            'monitor': {'max_history': 100},
            'safety': {
                'forbidden_commands': ['rm -rf', 'delete'],
                'max_output_length': 1000
            },
            'human_in_the_loop': {
                'require_intervention_for': ['file_write'],
                'always_require_intervention': ['delete']
            }
        }
        self.sdk = HITLSDK(self.config)
        self.agent = TestAgent()
    
    def test_normal_task(self):
        """测试正常任务执行"""
        task = "Read configuration"
        result = self.sdk.execute_agent(self.agent, task)
        self.assertEqual(result['status'], 'completed')
        self.assertIn('Result: Read configuration', result['result'])
    
    def test_dangerous_task(self):
        """测试危险任务被阻止"""
        task = "Delete files with rm -rf"
        result = self.sdk.execute_agent(self.agent, task)
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('Forbidden command detected', result['reason'])
    
    def test_human_intervention(self):
        """测试需要人类干预的任务"""
        task = "Write data to file"
        result = self.sdk.execute_agent(self.agent, task)
        # 模拟环境下应该被批准
        self.assertEqual(result['status'], 'completed')
    
    def test_execution_history(self):
        """测试执行历史记录"""
        task = "Test task"
        self.sdk.execute_agent(self.agent, task)
        history = self.sdk.get_execution_history()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1]['task'], task)
    
    def test_safety_violations(self):
        """测试安全违规记录"""
        # 执行一个危险任务
        task = "Delete files"
        self.sdk.execute_agent(self.agent, task)
        violations = self.sdk.get_safety_violations()
        self.assertGreater(len(violations), 0)

if __name__ == '__main__':
    unittest.main()