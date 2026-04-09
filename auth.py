import hashlib
import mysql.connector
from datetime import datetime, timedelta
import jwt

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'breakfast_system'
}

# JWT密钥
JWT_SECRET = 'breakfast_system_secret_key'

class UserManager:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        self._create_users_table()
    
    def _create_users_table(self):
        """创建用户表"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME NULL
                )
            """)
            self.conn.commit()
            
            # 创建默认管理员账户
            self._create_default_admin()
        except Exception as e:
            print(f"创建用户表失败: {e}")
    
    def _create_default_admin(self):
        """创建默认管理员账户"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = %s", ('admin',))
            if not self.cursor.fetchone():
                hashed_password = self._hash_password('admin123')
                self.cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    ('admin', hashed_password, 'admin')
                )
                self.conn.commit()
        except Exception as e:
            print(f"创建默认管理员失败: {e}")
    
    def _hash_password(self, password):
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed_password):
        """验证密码"""
        return self._hash_password(password) == hashed_password
    
    def create_user(self, username, password, role='user'):
        """创建用户"""
        try:
            hashed_password = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_password, role)
            )
            self.conn.commit()
            return {'success': True, 'message': '用户创建成功'}
        except Exception as e:
            return {'success': False, 'message': f'创建用户失败: {str(e)}'}
    
    def authenticate_user(self, username, password):
        """用户认证"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = self.cursor.fetchone()
            
            if not user:
                return {'success': False, 'message': '用户名不存在'}
            
            if not self.verify_password(password, user['password']):
                return {'success': False, 'message': '密码错误'}
            
            # 更新最后登录时间
            self.cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(), user['id'])
            )
            self.conn.commit()
            
            # 生成JWT令牌
            token = self._generate_token(user)
            
            return {
                'success': True,
                'message': '登录成功',
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'认证失败: {str(e)}'}
    
    def _generate_token(self, user):
        """生成JWT令牌"""
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    def verify_token(self, token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return {'success': True, 'user': payload}
        except Exception as e:
            return {'success': False, 'message': f'令牌无效: {str(e)}'}
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_all_users(self):
        """获取所有用户"""
        try:
            self.cursor.execute("SELECT id, username, role, created_at, last_login FROM users")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    def update_user_role(self, user_id, role):
        """更新用户角色"""
        try:
            self.cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id)
            )
            self.conn.commit()
            return {'success': True, 'message': '角色更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'更新角色失败: {str(e)}'}
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.conn.commit()
            return {'success': True, 'message': '用户删除成功'}
        except Exception as e:
            return {'success': False, 'message': f'删除用户失败: {str(e)}'}
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# 创建全局用户管理器实例
user_manager = UserManager()

def get_user_manager():
    """获取用户管理器实例"""
    return user_manager
