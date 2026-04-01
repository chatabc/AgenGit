class HumanIntervention:
    def __init__(self, config=None):
        self.config = config or {}
        self.intervention_history = []
        self.max_history = self.config.get('max_history', 500)
        
        # 干预规则配置
        self.rules = {
            'require_intervention_for': self.config.get('require_intervention_for', [
                'file_write', 'file_delete', 'network_request',
                'system_command', 'database_operation',
                'send_email', 'access_api', 'modify_config'
            ]),
            'auto_approve_patterns': self.config.get('auto_approve_patterns', [
                'read', 'get', 'list', 'view', 'query',
                'search', 'analyze', 'report', 'summary'
            ]),
            'always_require_intervention': self.config.get('always_require_intervention', [
                'delete', 'destroy', 'format', 'shutdown',
                'reboot', 'sudo', 'su', 'rm -rf'
            ])
        }
    
    def requires_intervention(self, task, context=None):
        """判断是否需要人类干预"""
        task_str = str(task).lower()
        
        # 检查是否总是需要干预的操作
        for op in self.rules['always_require_intervention']:
            if op in task_str:
                return True
        
        # 检查是否需要干预的操作
        for op in self.rules['require_intervention_for']:
            if op in task_str:
                # 检查是否可以自动批准
                for pattern in self.rules['auto_approve_patterns']:
                    if pattern in task_str:
                        return False
                return True
        
        return False
    
    def request_intervention(self, agent, task, context=None):
        """请求人类干预"""
        # 这里实现干预逻辑
        # 在实际应用中，这可能会打开一个UI界面或者发送通知给人类审核者
        
        # 记录干预请求
        intervention_record = {
            'agent': str(agent),
            'task': task,
            'context': context,
            'timestamp': self._get_timestamp(),
            'status': 'pending'
        }
        
        # 模拟人类干预（在实际应用中，这里会等待人类输入）
        # 对于演示目的，我们默认批准
        approved = self._simulate_human_response(task)
        
        intervention_record['status'] = 'approved' if approved else 'rejected'
        intervention_record['decision_time'] = self._get_timestamp()
        
        self.intervention_history.append(intervention_record)
        self._trim_history()
        
        # 记录日志
        print(f"[HUMAN INTERVENTION] {'Approved' if approved else 'Rejected'}: {task}")
        
        return {
            'approved': approved,
            'intervention_id': len(self.intervention_history),
            'task': task
        }
    
    def get_intervention_history(self, limit=50):
        """获取干预历史"""
        return self.intervention_history[-limit:]
    
    def _simulate_human_response(self, task):
        """模拟人类响应（仅用于演示）"""
        # 在实际应用中，这里会等待人类输入
        # 对于演示目的，我们默认批准大多数操作
        # 但拒绝明显危险的操作
        
        task_str = str(task).lower()
        dangerous_patterns = [
            'delete', 'destroy', 'format', 'shutdown',
            'reboot', 'sudo', 'su', 'rm -rf'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in task_str:
                return False
        
        return True
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _trim_history(self):
        """修剪历史记录"""
        if len(self.intervention_history) > self.max_history:
            self.intervention_history = self.intervention_history[-self.max_history:]
    
    def update_rules(self, rules):
        """更新干预规则"""
        self.rules.update(rules)
        return True
    
    def clear_history(self):
        """清空干预历史"""
        self.intervention_history = []
        return True