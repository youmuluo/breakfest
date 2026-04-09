import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "breakfast_system")

def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 数据库 '{DB_NAME}' 已创建或已存在")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        print("\n请检查：")
        print("1. MySQL服务是否已启动")
        print("2. 数据库用户名和密码是否正确")
        print("3. 数据库端口是否正确")
        return False

if __name__ == "__main__":
    create_database()
