import hashlib
import jwt
import time
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.secret_key = self.config.get('secret_key', 'default_secret_key')
        self.token_expiry = self.config.get('token_expiry', 3600)  # 1小时
        
        # 初始化数据库
        try:
            from .db import DatabaseManager
            self.db = DatabaseManager()
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to initialize database: {e}")
            self.db = None
            #  fallback to in-memory storage
            self.users = self.config.get('users', {})
            self.roles = self.config.get('roles', {
                'admin': ['*'],
                'user': ['execute', 'view_history'],
                'viewer': ['view_history']
            })
    
    def register_user(self, username, password, role='user'):
        """注册新用户"""
        # 检查用户是否已存在
        if self.db:
            existing_user = self.db.get_user(username)
            if existing_user:
                return {'success': False, 'reason': 'User already exists'}
        else:
            if username in self.users:
                return {'success': False, 'reason': 'User already exists'}
        
        # 哈希密码
        hashed_password = self._hash_password(password)
        
        # 保存用户信息
        user_data = {
            'username': username,
            'password': hashed_password,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        if self.db:
            self.db.insert_user(user_data)
        else:
            self.users[username] = user_data
        
        return {'success': True, 'username': username, 'role': role}
    
    def login(self, username, password):
        """用户登录"""
        # 获取用户信息
        user = None
        if self.db:
            user = self.db.get_user(username)
        else:
            if username in self.users:
                user = self.users[username]
        
        if not user:
            return {'success': False, 'reason': 'Invalid username or password'}
        
        # 验证密码
        if not self._verify_password(password, user['password']):
            return {'success': False, 'reason': 'Invalid username or password'}
        
        # 生成JWT token
        token = self._generate_token(username, user['role'])
        
        return {
            'success': True,
            'token': token,
            'username': username,
            'role': user['role']
        }
    
    def verify_token(self, token):
        """验证token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload['exp'] < time.time():
                return {'valid': False, 'reason': 'Token expired'}
            
            return {
                'valid': True,
                'username': payload['sub'],
                'role': payload['role']
            }
        except jwt.InvalidTokenError:
            return {'valid': False, 'reason': 'Invalid token'}
    
    def check_permission(self, username, action):
        """检查用户权限"""
        # 获取用户信息
        user = None
        if self.db:
            user = self.db.get_user(username)
        else:
            if username in self.users:
                user = self.users[username]
        
        if not user:
            return False
        
        # 获取角色权限
        user_role = user['role']
        roles = {}
        if self.db:
            roles = self.db.get_roles()
        else:
            roles = self.roles
        
        if user_role not in roles:
            return False
        
        # 检查是否有通配符权限
        if '*' in roles[user_role]:
            return True
        
        # 检查是否有具体权限
        return action in roles[user_role]
    
    def update_user_role(self, username, role):
        """更新用户角色"""
        # 检查用户是否存在
        user = None
        if self.db:
            user = self.db.get_user(username)
        else:
            if username in self.users:
                user = self.users[username]
        
        if not user:
            return {'success': False, 'reason': 'User not found'}
        
        # 检查角色是否有效
        roles = {}
        if self.db:
            roles = self.db.get_roles()
        else:
            roles = self.roles
        
        if role not in roles:
            return {'success': False, 'reason': 'Invalid role'}
        
        # 更新用户角色
        if self.db:
            user['role'] = role
            self.db.insert_user(user)
        else:
            self.users[username]['role'] = role
        
        return {'success': True, 'username': username, 'role': role}
    
    def change_password(self, username, old_password, new_password):
        """修改密码"""
        # 检查用户是否存在
        user = None
        if self.db:
            user = self.db.get_user(username)
        else:
            if username in self.users:
                user = self.users[username]
        
        if not user:
            return {'success': False, 'reason': 'User not found'}
        
        # 验证旧密码
        if not self._verify_password(old_password, user['password']):
            return {'success': False, 'reason': 'Invalid old password'}
        
        # 更新密码
        hashed_password = self._hash_password(new_password)
        
        if self.db:
            user['password'] = hashed_password
            self.db.insert_user(user)
        else:
            self.users[username]['password'] = hashed_password
        
        return {'success': True, 'username': username}
    
    def get_users(self):
        """获取所有用户"""
        if self.db:
            return self.db.get_users()
        else:
            users = []
            for username, user_data in self.users.items():
                users.append({
                    'username': username,
                    'role': user_data['role'],
                    'created_at': user_data['created_at']
                })
            return users
    
    def get_roles(self):
        """获取所有角色"""
        if self.db:
            return self.db.get_roles()
        else:
            return self.roles
    
    def _hash_password(self, password):
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, hashed_password):
        """验证密码"""
        return self._hash_password(password) == hashed_password
    
    def _generate_token(self, username, role):
        """生成JWT token"""
        payload = {
            'sub': username,
            'role': role,
            'iat': time.time(),
            'exp': time.time() + self.token_expiry
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def update_config(self, config):
        """更新配置"""
        self.config.update(config)
        if 'users' in config:
            self.users = config['users']
        if 'roles' in config:
            self.roles = config['roles']
        if 'secret_key' in config:
            self.secret_key = config['secret_key']
        if 'token_expiry' in config:
            self.token_expiry = config['token_expiry']
        return {'success': True}