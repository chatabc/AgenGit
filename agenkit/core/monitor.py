import uuid
import time
from datetime import datetime

class AgentMonitor:
    def __init__(self, config=None):
        self.config = config or {}
        self.execution_history = []
        self.max_history = self.config.get('max_history', 1000)
    
    def start_execution(self, agent, task, context=None):
        """开始执行监控"""
        execution_id = str(uuid.uuid4())
        execution_record = {
            'execution_id': execution_id,
            'agent': str(agent),
            'task': task,
            'context': context,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'details': {}
        }
        
        self.execution_history.append(execution_record)
        self._trim_history()
        
        self._log('info', f'Starting execution {execution_id}', {
            'agent': str(agent),
            'task': task
        })
        
        return execution_id
    
    def end_execution(self, execution_id, status, reason):
        """结束执行监控"""
        for record in self.execution_history:
            if record['execution_id'] == execution_id:
                record['status'] = status
                record['end_time'] = datetime.now().isoformat()
                record['reason'] = reason
                record['duration'] = self._calculate_duration(record['start_time'])
                
                self._log('info', f'Execution {execution_id} completed with status {status}', {
                    'status': status,
                    'reason': reason,
                    'duration': record['duration']
                })
                break
    
    def get_history(self, limit=100):
        """获取执行历史"""
        return self.execution_history[-limit:]
    
    def get_execution(self, execution_id):
        """获取特定执行记录"""
        for record in self.execution_history:
            if record['execution_id'] == execution_id:
                return record
        return None
    
    def _calculate_duration(self, start_time):
        """计算执行时长"""
        start = datetime.fromisoformat(start_time)
        end = datetime.now()
        return (end - start).total_seconds()
    
    def _trim_history(self):
        """修剪历史记录，保持在最大限制内"""
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]
    
    def _log(self, level, message, extra=None):
        """日志记录"""
        timestamp = datetime.now().isoformat()
        log_message = f"[{timestamp}] [{level.upper()}] {message}"
        if extra:
            log_message += f" | {extra}"
        
        # 这里可以集成到更完善的日志系统
        print(log_message)
    
    def clear_history(self):
        """清空历史记录"""
        self.execution_history = []
        return True