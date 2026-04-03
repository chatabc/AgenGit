import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='agenkit.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建执行历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE,
            agent TEXT,
            task TEXT,
            context TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            reason TEXT,
            result TEXT,
            duration REAL
        )
        ''')
        
        # 创建安全违规表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS safety_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            reason TEXT,
            context TEXT
        )
        ''')
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            created_at TEXT
        )
        ''')
        
        # 创建角色表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            permissions TEXT
        )
        ''')
        
        # 插入默认角色
        cursor.execute('SELECT COUNT(*) FROM roles')
        if cursor.fetchone()[0] == 0:
            roles = [
                ('admin', json.dumps(['*'])),
                ('user', json.dumps(['execute', 'view_history'])),
                ('viewer', json.dumps(['view_history']))
            ]
            cursor.executemany('INSERT INTO roles (name, permissions) VALUES (?, ?)', roles)
        
        conn.commit()
        conn.close()
    
    def insert_execution(self, execution):
        """插入执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO execution_history 
        (execution_id, agent, task, context, start_time, end_time, status, reason, result, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution['execution_id'],
            execution['agent'],
            execution['task'],
            json.dumps(execution.get('context', {})),
            execution['start_time'],
            execution.get('end_time', None),
            execution['status'],
            execution.get('reason', None),
            execution.get('result', None),
            execution.get('duration', None)
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_executions(self, limit=100):
        """获取执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT execution_id, agent, task, context, start_time, end_time, status, reason, result, duration
        FROM execution_history
        ORDER BY start_time DESC
        LIMIT ?
        ''', (limit,))
        
        executions = []
        for row in cursor.fetchall():
            executions.append({
                'execution_id': row[0],
                'agent': row[1],
                'task': row[2],
                'context': json.loads(row[3]) if row[3] else None,
                'start_time': row[4],
                'end_time': row[5],
                'status': row[6],
                'reason': row[7],
                'result': row[8],
                'duration': row[9]
            })
        
        conn.close()
        return executions
    
    def insert_violation(self, violation):
        """插入安全违规记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 处理不同的字段名称
        violation_type = violation.get('type', violation.get('violation_type', 'unknown'))
        reason = violation.get('reason', violation.get('details', ''))
        
        cursor.execute('''
        INSERT INTO safety_violations (timestamp, type, reason, context)
        VALUES (?, ?, ?, ?)
        ''', (
            violation['timestamp'],
            violation_type,
            reason,
            json.dumps(violation.get('context', {}))
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_violations(self, limit=50):
        """获取安全违规记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT timestamp, type, reason, context
        FROM safety_violations
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (limit,))
        
        violations = []
        for row in cursor.fetchall():
            violations.append({
                'timestamp': row[0],
                'type': row[1],
                'reason': row[2],
                'context': json.loads(row[3]) if row[3] else None
            })
        
        conn.close()
        return violations
    
    def insert_user(self, user):
        """插入用户记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO users (username, password, role, created_at)
        VALUES (?, ?, ?, ?)
        ''', (
            user['username'],
            user['password'],
            user['role'],
            user.get('created_at', datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
    
    def get_user(self, username):
        """获取用户记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT username, password, role, created_at
        FROM users
        WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'username': row[0],
                'password': row[1],
                'role': row[2],
                'created_at': row[3]
            }
        return None
    
    def get_users(self):
        """获取所有用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT username, password, role, created_at
        FROM users
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'username': row[0],
                'role': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return users
    
    def get_roles(self):
        """获取所有角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT name, permissions
        FROM roles
        ''')
        
        roles = {}
        for row in cursor.fetchall():
            roles[row[0]] = json.loads(row[1])
        
        conn.close()
        return roles
    
    def close(self):
        """关闭数据库连接"""
        pass  # SQLite连接会在每次操作后自动关闭