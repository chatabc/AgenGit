from datetime import datetime

class HITLSDK:
    def __init__(self, config=None):
        self.config = config or {}
        self.monitor = None
        self.safety_guard = None
        self.human_intervention = None
        self.firewall = None
        self.auth = None
        self.db = None
        self._initialize_components()
    
    def _initialize_components(self):
        from .monitor import AgentMonitor
        from .guardrail import SafetyGuard
        from .human_in_the_loop import HumanIntervention
        from .firewall import AgentFirewall
        from .auth import AuthManager
        from .db import DatabaseManager
        
        self.monitor = AgentMonitor(self.config.get('monitor', {}))
        self.safety_guard = SafetyGuard(self.config.get('safety', {}))
        self.human_intervention = HumanIntervention(self.config.get('human_in_the_loop', {}))
        self.firewall = AgentFirewall(self.config.get('firewall', {}))
        self.auth = AuthManager(self.config.get('auth', {}))
        self.db = DatabaseManager(self.config.get('db_path', 'agenkit.db'))
    
    def execute_agent(self, agent, task, context=None, token=None):
        """执行Agent任务，包含监控和安全检查"""
        # 1. 认证检查
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {
                    'status': 'unauthorized',
                    'reason': auth_result['reason'],
                    'task': task
                }
            
            # 权限检查
            if not self.auth.check_permission(auth_result['username'], 'execute'):
                return {
                    'status': 'forbidden',
                    'reason': 'Insufficient permissions',
                    'task': task
                }
        
        # 2. 前置安全检查
        safety_check = self.safety_guard.check_task(task)
        if not safety_check['allowed']:
            return {
                'status': 'blocked',
                'reason': safety_check['reason'],
                'task': task
            }
        
        # 3. 开始监控
        execution_id = self.monitor.start_execution(agent, task, context)
        
        try:
            # 4. 防火墙检查
            firewall_check = self.firewall.start_execution(execution_id, agent, task, context)
            if not firewall_check['allowed']:
                self.monitor.end_execution(execution_id, 'blocked', firewall_check['reason'])
                # 保存到数据库
                execution_record = {
                    'execution_id': execution_id,
                    'agent': str(agent),
                    'task': task,
                    'context': context,
                    'start_time': datetime.now().isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'status': 'blocked',
                    'reason': firewall_check['reason'],
                    'result': None,
                    'duration': 0
                }
                self.db.insert_execution(execution_record)
                return {
                    'status': 'blocked',
                    'reason': firewall_check['reason'],
                    'task': task
                }
            
            # 5. 执行前检查是否需要人类干预
            if self.human_intervention.requires_intervention(task, context):
                intervention_result = self.human_intervention.request_intervention(
                    agent, task, context
                )
                if not intervention_result['approved']:
                    self.firewall.end_execution(execution_id, 'blocked', 'human_rejected')
                    self.monitor.end_execution(execution_id, 'blocked', 'human_rejected')
                    # 保存到数据库
                    execution_record = {
                        'execution_id': execution_id,
                        'agent': str(agent),
                        'task': task,
                        'context': context,
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'status': 'blocked',
                        'reason': 'Human intervention rejected',
                        'result': None,
                        'duration': 0
                    }
                    self.db.insert_execution(execution_record)
                    return {
                        'status': 'blocked',
                        'reason': 'Human intervention rejected',
                        'task': task
                    }
            
            # 6. 执行Agent
            start_time = datetime.now()
            result = agent.execute(task, context)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 7. 防火墙更新执行状态
            self.firewall.update_execution(execution_id, str(result))
            
            # 8. 执行后安全检查
            post_check = self.safety_guard.check_result(result)
            if not post_check['allowed']:
                self.firewall.end_execution(execution_id, 'blocked', 'post_check_failed')
                self.monitor.end_execution(execution_id, 'blocked', 'post_check_failed')
                # 保存到数据库
                execution_record = {
                    'execution_id': execution_id,
                    'agent': str(agent),
                    'task': task,
                    'context': context,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'status': 'blocked',
                    'reason': post_check['reason'],
                    'result': str(result),
                    'duration': duration
                }
                self.db.insert_execution(execution_record)
                return {
                    'status': 'blocked',
                    'reason': post_check['reason'],
                    'result': result
                }
            
            # 9. 完成监控
            self.firewall.end_execution(execution_id, 'completed', result)
            self.monitor.end_execution(execution_id, 'completed', 'success')
            
            # 保存到数据库
            execution_record = {
                'execution_id': execution_id,
                'agent': str(agent),
                'task': task,
                'context': context,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'status': 'completed',
                'reason': 'success',
                'result': str(result),
                'duration': duration
            }
            self.db.insert_execution(execution_record)
            
            return {
                'status': 'completed',
                'result': result,
                'execution_id': execution_id
            }
            
        except Exception as e:
            self.firewall.end_execution(execution_id, 'error', str(e))
            self.monitor.end_execution(execution_id, 'error', str(e))
            # 保存到数据库
            execution_record = {
                'execution_id': execution_id,
                'agent': str(agent),
                'task': task,
                'context': context,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'status': 'error',
                'reason': str(e),
                'result': None,
                'duration': 0
            }
            self.db.insert_execution(execution_record)
            return {
                'status': 'error',
                'reason': str(e),
                'task': task
            }
    
    def get_execution_history(self, limit=100, token=None):
        """获取执行历史"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'error': 'Unauthorized', 'reason': auth_result['reason']}
            
            if not self.auth.check_permission(auth_result['username'], 'view_history'):
                return {'error': 'Forbidden', 'reason': 'Insufficient permissions'}
        # 从数据库获取执行历史
        return self.db.get_executions(limit)
    
    def get_safety_violations(self, limit=50, token=None):
        """获取安全违规记录"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'error': 'Unauthorized', 'reason': auth_result['reason']}
            
            if not self.auth.check_permission(auth_result['username'], 'view_history'):
                return {'error': 'Forbidden', 'reason': 'Insufficient permissions'}
        # 从数据库获取安全违规记录
        return self.db.get_violations(limit)
    
    def get_active_executions(self, token=None):
        """获取活跃的执行"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'error': 'Unauthorized', 'reason': auth_result['reason']}
            
            if not self.auth.check_permission(auth_result['username'], 'view_history'):
                return {'error': 'Forbidden', 'reason': 'Insufficient permissions'}
        return self.firewall.get_active_executions()
    
    def terminate_execution(self, execution_id, token=None):
        """终止执行"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'success': False, 'reason': 'Unauthorized'}
            
            if not self.auth.check_permission(auth_result['username'], 'terminate'):
                return {'success': False, 'reason': 'Insufficient permissions'}
        return self.firewall.terminate_execution(execution_id)
    
    def get_execution_status(self, execution_id, token=None):
        """获取执行状态"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'error': 'Unauthorized', 'reason': auth_result['reason']}
            
            if not self.auth.check_permission(auth_result['username'], 'view_history'):
                return {'error': 'Forbidden', 'reason': 'Insufficient permissions'}
        return self.firewall.get_execution_status(execution_id)
    
    def update_firewall_rules(self, rules, token=None):
        """更新防火墙规则"""
        if token:
            auth_result = self.auth.verify_token(token)
            if not auth_result['valid']:
                return {'success': False, 'reason': 'Unauthorized'}
            
            if not self.auth.check_permission(auth_result['username'], 'update_rules'):
                return {'success': False, 'reason': 'Insufficient permissions'}
        return self.firewall.update_rules(rules)
    
    def register_user(self, username, password, role='user'):
        """注册用户"""
        return self.auth.register_user(username, password, role)
    
    def login(self, username, password):
        """用户登录"""
        return self.auth.login(username, password)
    
    def verify_token(self, token):
        """验证token"""
        return self.auth.verify_token(token)
    
    def update_config(self, config):
        """更新配置"""
        self.config.update(config)
        self._initialize_components()
        return True