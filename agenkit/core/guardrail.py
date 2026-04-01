import re

class SafetyGuard:
    def __init__(self, config=None):
        self.config = config or {}
        self.violations = []
        self.max_violations = self.config.get('max_violations', 500)
        
        # 安全规则配置
        self.rules = {
            'forbidden_commands': self.config.get('forbidden_commands', [
                'rm -rf', 'format', 'delete', 'destroy',
                'shutdown', 'reboot', 'sudo', 'su'
            ]),
            'forbidden_patterns': self.config.get('forbidden_patterns', [
                r'[0-9]{16}',  # 信用卡号
                r'[0-9]{9,12}',  # 社会安全号
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
                r'\bhttps?://\S+\b',  # URL
            ]),
            'risky_operations': self.config.get('risky_operations', [
                'file_write', 'file_delete', 'network_request',
                'system_command', 'database_operation'
            ]),
            'max_output_length': self.config.get('max_output_length', 10000),
            'max_execution_time': self.config.get('max_execution_time', 300)  # 5分钟
        }
    
    def check_task(self, task):
        """检查任务是否安全"""
        task_str = str(task)
        
        # 检查禁止的命令
        for cmd in self.rules['forbidden_commands']:
            if cmd in task_str.lower():
                violation = self._create_violation('forbidden_command', f'Forbidden command detected: {cmd}', task)
                return {'allowed': False, 'reason': violation['reason']}
        
        # 检查禁止的模式
        for pattern in self.rules['forbidden_patterns']:
            if re.search(pattern, task_str):
                violation = self._create_violation('forbidden_pattern', 'Forbidden pattern detected', task)
                return {'allowed': False, 'reason': violation['reason']}
        
        # 检查危险操作
        for op in self.rules['risky_operations']:
            if op in task_str.lower():
                # 危险操作需要人类干预，不是直接禁止
                pass
        
        return {'allowed': True, 'reason': 'Task passed security checks'}
    
    def check_result(self, result):
        """检查执行结果是否安全"""
        result_str = str(result)
        
        # 检查输出长度
        if len(result_str) > self.rules['max_output_length']:
            violation = self._create_violation('output_too_long', f'Output exceeds maximum length ({self.rules["max_output_length"]} chars)', result)
            return {'allowed': False, 'reason': violation['reason']}
        
        # 检查禁止的模式
        for pattern in self.rules['forbidden_patterns']:
            if re.search(pattern, result_str):
                violation = self._create_violation('forbidden_pattern', 'Forbidden pattern detected in result', result)
                return {'allowed': False, 'reason': violation['reason']}
        
        return {'allowed': True, 'reason': 'Result passed security checks'}
    
    def get_violations(self, limit=50):
        """获取安全违规记录"""
        return self.violations[-limit:]
    
    def _create_violation(self, violation_type, reason, context):
        """创建违规记录"""
        from datetime import datetime
        
        violation = {
            'timestamp': datetime.now().isoformat(),
            'type': violation_type,
            'reason': reason,
            'context': context
        }
        
        self.violations.append(violation)
        self._trim_violations()
        
        # 记录日志
        print(f"[SECURITY VIOLATION] {violation_type}: {reason}")
        
        return violation
    
    def _trim_violations(self):
        """修剪违规记录"""
        if len(self.violations) > self.max_violations:
            self.violations = self.violations[-self.max_violations:]
    
    def update_rules(self, rules):
        """更新安全规则"""
        self.rules.update(rules)
        return True
    
    def clear_violations(self):
        """清空违规记录"""
        self.violations = []
        return True