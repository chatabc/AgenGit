class HITLSDK:
    def __init__(self, config=None):
        self.config = config or {}
        self.monitor = None
        self.safety_guard = None
        self.human_intervention = None
        self._initialize_components()
    
    def _initialize_components(self):
        from .monitor import AgentMonitor
        from .guardrail import SafetyGuard
        from .human_in_the_loop import HumanIntervention
        
        self.monitor = AgentMonitor(self.config.get('monitor', {}))
        self.safety_guard = SafetyGuard(self.config.get('safety', {}))
        self.human_intervention = HumanIntervention(self.config.get('human_in_the_loop', {}))
    
    def execute_agent(self, agent, task, context=None):
        """执行Agent任务，包含监控和安全检查"""
        # 1. 前置安全检查
        safety_check = self.safety_guard.check_task(task)
        if not safety_check['allowed']:
            return {
                'status': 'blocked',
                'reason': safety_check['reason'],
                'task': task
            }
        
        # 2. 开始监控
        execution_id = self.monitor.start_execution(agent, task, context)
        
        try:
            # 3. 执行前检查是否需要人类干预
            if self.human_intervention.requires_intervention(task, context):
                intervention_result = self.human_intervention.request_intervention(
                    agent, task, context
                )
                if not intervention_result['approved']:
                    self.monitor.end_execution(execution_id, 'blocked', 'human_rejected')
                    return {
                        'status': 'blocked',
                        'reason': 'Human intervention rejected',
                        'task': task
                    }
            
            # 4. 执行Agent
            result = agent.execute(task, context)
            
            # 5. 执行后安全检查
            post_check = self.safety_guard.check_result(result)
            if not post_check['allowed']:
                self.monitor.end_execution(execution_id, 'blocked', 'post_check_failed')
                return {
                    'status': 'blocked',
                    'reason': post_check['reason'],
                    'result': result
                }
            
            # 6. 完成监控
            self.monitor.end_execution(execution_id, 'completed', 'success')
            
            return {
                'status': 'completed',
                'result': result,
                'execution_id': execution_id
            }
            
        except Exception as e:
            self.monitor.end_execution(execution_id, 'error', str(e))
            return {
                'status': 'error',
                'reason': str(e),
                'task': task
            }
    
    def get_execution_history(self, limit=100):
        """获取执行历史"""
        return self.monitor.get_history(limit)
    
    def get_safety_violations(self, limit=50):
        """获取安全违规记录"""
        return self.safety_guard.get_violations(limit)
    
    def update_config(self, config):
        """更新配置"""
        self.config.update(config)
        self._initialize_components()
        return True