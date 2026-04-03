import threading
import time
from datetime import datetime

class AgentFirewall:
    def __init__(self, config=None):
        self.config = config or {}
        self.executions = {}
        self.rules = {
            'max_execution_time': self.config.get('max_execution_time', 300),  # 5分钟
            'max_output_length': self.config.get('max_output_length', 10000),
            'allowed_operations': self.config.get('allowed_operations', []),
            'blocked_operations': self.config.get('blocked_operations', []),
            'rate_limit': self.config.get('rate_limit', 10),  # 每分钟最大执行次数
        }
        self.execution_counts = {}
        self.lock = threading.Lock()
    
    def start_execution(self, execution_id, agent, task, context=None):
        """开始执行，添加到防火墙监控"""
        # 检查速率限制
        if not self._check_rate_limit():
            return {'allowed': False, 'reason': 'Rate limit exceeded'}
        
        # 检查操作是否被阻止
        if not self._check_operation(task):
            return {'allowed': False, 'reason': 'Operation blocked'}
        
        with self.lock:
            self.executions[execution_id] = {
                'agent': str(agent),
                'task': task,
                'context': context,
                'start_time': datetime.now(),
                'status': 'running',
                'output': '',
                'thread': threading.current_thread().ident
            }
        
        # 启动监控线程
        monitor_thread = threading.Thread(
            target=self._monitor_execution,
            args=(execution_id,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return {'allowed': True, 'execution_id': execution_id}
    
    def update_execution(self, execution_id, output_chunk=None, status=None):
        """更新执行状态"""
        with self.lock:
            if execution_id in self.executions:
                if output_chunk:
                    self.executions[execution_id]['output'] += output_chunk
                    # 检查输出长度
                    if len(self.executions[execution_id]['output']) > self.rules['max_output_length']:
                        self.executions[execution_id]['status'] = 'blocked'
                        self.executions[execution_id]['reason'] = 'Output length exceeded'
                        return {'allowed': False, 'reason': 'Output length exceeded'}
                if status:
                    self.executions[execution_id]['status'] = status
        return {'allowed': True}
    
    def end_execution(self, execution_id, status, result=None):
        """结束执行"""
        with self.lock:
            if execution_id in self.executions:
                self.executions[execution_id]['status'] = status
                self.executions[execution_id]['end_time'] = datetime.now()
                self.executions[execution_id]['result'] = result
                # 清理执行记录（可选，根据配置）
                if self.config.get('cleanup_executions', True):
                    del self.executions[execution_id]
        return {'success': True}
    
    def _monitor_execution(self, execution_id):
        """监控执行过程"""
        start_time = datetime.now()
        while True:
            time.sleep(1)
            
            with self.lock:
                if execution_id not in self.executions:
                    break
                
                execution = self.executions[execution_id]
                if execution['status'] != 'running':
                    break
                
                # 检查执行时间
                elapsed = (datetime.now() - execution['start_time']).total_seconds()
                if elapsed > self.rules['max_execution_time']:
                    execution['status'] = 'blocked'
                    execution['reason'] = 'Execution time exceeded'
                    break
    
    def _check_rate_limit(self):
        """检查速率限制"""
        current_minute = datetime.now().strftime('%Y-%m-%d %H:%M')
        with self.lock:
            if current_minute not in self.execution_counts:
                self.execution_counts[current_minute] = 0
            
            self.execution_counts[current_minute] += 1
            
            # 清理旧的计数
            for minute in list(self.execution_counts.keys()):
                if minute != current_minute:
                    del self.execution_counts[minute]
            
            return self.execution_counts[current_minute] <= self.rules['rate_limit']
    
    def _check_operation(self, task):
        """检查操作是否被允许"""
        task_str = str(task).lower()
        
        # 检查是否在阻止列表中
        for op in self.rules['blocked_operations']:
            if op in task_str:
                return False
        
        # 检查是否在允许列表中（如果有）
        if self.rules['allowed_operations']:
            for op in self.rules['allowed_operations']:
                if op in task_str:
                    return True
            return False
        
        return True
    
    def get_execution_status(self, execution_id):
        """获取执行状态"""
        with self.lock:
            if execution_id in self.executions:
                return self.executions[execution_id]
        return None
    
    def get_active_executions(self):
        """获取活跃的执行"""
        active = []
        with self.lock:
            for execution_id, execution in self.executions.items():
                if execution['status'] == 'running':
                    active.append({
                        'execution_id': execution_id,
                        'agent': execution['agent'],
                        'task': execution['task'],
                        'start_time': execution['start_time'].isoformat(),
                        'elapsed': (datetime.now() - execution['start_time']).total_seconds()
                    })
        return active
    
    def terminate_execution(self, execution_id):
        """终止执行"""
        with self.lock:
            if execution_id in self.executions:
                self.executions[execution_id]['status'] = 'terminated'
                self.executions[execution_id]['end_time'] = datetime.now()
                self.executions[execution_id]['reason'] = 'Manually terminated'
                return {'success': True}
        return {'success': False, 'reason': 'Execution not found'}
    
    def update_rules(self, rules):
        """更新规则"""
        with self.lock:
            self.rules.update(rules)
        return {'success': True}
    
    def get_rules(self):
        """获取当前规则"""
        with self.lock:
            return self.rules.copy()