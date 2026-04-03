from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from agenkit import HITLSDK
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# 初始化HITL SDK
sdk = HITLSDK({
    'auth': {
        'secret_key': 'your_secret_key_here',
        'roles': {
            'admin': ['*'],
            'user': ['execute', 'view_history'],
            'viewer': ['view_history']
        }
    }
})

# 检查用户是否登录
def is_logged_in():
    return 'token' in session and 'username' in session

# 主页
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        result = sdk.login(username, password)
        if result['success']:
            session['token'] = result['token']
            session['username'] = result['username']
            session['role'] = result['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error=result['reason'])
    return render_template('login.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        
        result = sdk.register_user(username, password, role)
        if result['success']:
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=result['reason'])
    return render_template('register.html')

# 登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 执行Agent任务
@app.route('/execute', methods=['POST'])
def execute():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    task = request.json.get('task')
    if not task:
        return jsonify({'error': 'Task is required'})
    
    # 创建一个简单的Agent
    class SimpleAgent:
        def execute(self, task, context=None):
            return f"Result: {task}"
    
    agent = SimpleAgent()
    result = sdk.execute_agent(agent, task, token=session['token'])
    return jsonify(result)

# 获取执行历史
@app.route('/history')
def history():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    limit = int(request.args.get('limit', 100))
    history = sdk.get_execution_history(limit, token=session['token'])
    return jsonify(history)

# 获取安全违规记录
@app.route('/violations')
def violations():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    limit = int(request.args.get('limit', 50))
    violations = sdk.get_safety_violations(limit, token=session['token'])
    return jsonify(violations)

# 获取活跃执行
@app.route('/active')
def active():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    active = sdk.get_active_executions(token=session['token'])
    return jsonify(active)

# 终止执行
@app.route('/terminate/<execution_id>')
def terminate(execution_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    result = sdk.terminate_execution(execution_id, token=session['token'])
    return jsonify(result)

# 监控页面
@app.route('/monitor')
def monitor():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('monitor.html', username=session['username'])

# 安全页面
@app.route('/security')
def security():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('security.html', username=session['username'])

# 用户管理页面
@app.route('/users')
def users():
    if not is_logged_in() or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # 获取所有用户
    users = sdk.auth.get_users()
    roles = sdk.auth.get_roles()
    return render_template('users.html', username=session['username'], users=users, roles=roles)

# API接口路由组
@app.route('/api/execute', methods=['POST'])
def api_execute():
    """API: 执行Agent任务"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    data = request.json
    if not data or 'task' not in data:
        return jsonify({'error': 'Bad Request', 'reason': 'Task is required'}), 400
    
    task = data['task']
    context = data.get('context')
    
    # 创建一个简单的Agent
    class SimpleAgent:
        def execute(self, task, context=None):
            return f"Result: {task}"
    
    agent = SimpleAgent()
    result = sdk.execute_agent(agent, task, context, token=token)
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def api_history():
    """API: 获取执行历史"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    limit = int(request.args.get('limit', 100))
    history = sdk.get_execution_history(limit, token=token)
    if 'error' in history:
        return jsonify(history), 403
    return jsonify(history)

@app.route('/api/violations', methods=['GET'])
def api_violations():
    """API: 获取安全违规记录"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    limit = int(request.args.get('limit', 50))
    violations = sdk.get_safety_violations(limit, token=token)
    if 'error' in violations:
        return jsonify(violations), 403
    return jsonify(violations)

@app.route('/api/active', methods=['GET'])
def api_active():
    """API: 获取活跃执行"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    active = sdk.get_active_executions(token=token)
    if 'error' in active:
        return jsonify(active), 403
    return jsonify(active)

@app.route('/api/terminate/<execution_id>', methods=['POST'])
def api_terminate(execution_id):
    """API: 终止执行"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    result = sdk.terminate_execution(execution_id, token=token)
    if not result.get('success'):
        return jsonify(result), 403
    return jsonify(result)

@app.route('/api/execution/<execution_id>', methods=['GET'])
def api_execution(execution_id):
    """API: 获取执行状态"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    result = sdk.get_execution_status(execution_id, token=token)
    if 'error' in result:
        return jsonify(result), 403
    return jsonify(result)

@app.route('/api/firewall/rules', methods=['GET', 'PUT'])
def api_firewall_rules():
    """API: 获取或更新防火墙规则"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized', 'reason': 'Missing token'}), 401
    
    if request.method == 'GET':
        # 获取当前规则
        rules = sdk.firewall.get_rules()
        return jsonify({'rules': rules})
    elif request.method == 'PUT':
        # 更新规则
        data = request.json
        if not data or 'rules' not in data:
            return jsonify({'error': 'Bad Request', 'reason': 'Rules are required'}), 400
        
        result = sdk.update_firewall_rules(data['rules'], token=token)
        if not result.get('success'):
            return jsonify(result), 403
        return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API: 用户登录"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Bad Request', 'reason': 'Username and password are required'}), 400
    
    result = sdk.login(data['username'], data['password'])
    if not result.get('success'):
        return jsonify(result), 401
    return jsonify(result)

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API: 用户注册"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Bad Request', 'reason': 'Username and password are required'}), 400
    
    role = data.get('role', 'user')
    result = sdk.register_user(data['username'], data['password'], role)
    if not result.get('success'):
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/auth/verify', methods=['POST'])
def api_verify():
    """API: 验证token"""
    data = request.json
    if not data or 'token' not in data:
        return jsonify({'error': 'Bad Request', 'reason': 'Token is required'}), 400
    
    result = sdk.verify_token(data['token'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)