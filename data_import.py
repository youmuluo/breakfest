import pandas as pd
import mysql.connector
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'breakfast_system'
}

def import_csv_file(file_path):
    """导入CSV文件数据到数据库"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 数据预处理
        df = preprocess_data(df)
        
        # 导入数据到数据库
        import_to_database(df)
        
        return {'success': True, 'message': f'成功导入 {len(df)} 条数据'}
    except Exception as e:
        return {'success': False, 'message': f'导入失败: {str(e)}'}

def import_excel_file(file_path):
    """导入Excel文件数据到数据库"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 数据预处理
        df = preprocess_data(df)
        
        # 导入数据到数据库
        import_to_database(df)
        
        return {'success': True, 'message': f'成功导入 {len(df)} 条数据'}
    except Exception as e:
        return {'success': False, 'message': f'导入失败: {str(e)}'}

def preprocess_data(df):
    """预处理数据"""
    # 处理缺失值
    df = df.dropna()
    
    # 处理时间格式
    if 'order_time' in df.columns:
        df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
        df = df.dropna(subset=['order_time'])
    
    # 处理数值类型
    numeric_columns = ['quantity', 'price', 'total_amount']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=[col])
    
    # 处理字符串类型
    string_columns = ['order_id', 'product_id', 'product_name', 'category']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    return df

def import_to_database(df):
    """将数据导入到数据库"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 导入订单数据
        for _, row in df.iterrows():
            # 检查订单是否已存在
            cursor.execute("SELECT id FROM orders WHERE order_id = %s", (row['order_id'],))
            if cursor.fetchone():
                continue
            
            # 插入订单数据
            order_sql = """
            INSERT INTO orders (order_id, order_time, total_amount)
            VALUES (%s, %s, %s)
            """
            cursor.execute(order_sql, (
                row['order_id'],
                row['order_time'],
                row['total_amount']
            ))
            
            # 获取订单ID
            order_id = cursor.lastrowid
            
            # 插入订单详情数据
            detail_sql = """
            INSERT INTO order_details (order_id, product_id, product_name, category, quantity, price, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(detail_sql, (
                order_id,
                row['product_id'],
                row['product_name'],
                row['category'],
                row['quantity'],
                row['price'],
                row['quantity'] * row['price']
            ))
        
        # 提交事务
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def validate_data(file_path, file_type):
    """验证数据文件"""
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 检查必要列
        required_columns = ['order_id', 'order_time', 'product_id', 'product_name', 'category', 'quantity', 'price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {'valid': False, 'message': f'缺少必要列: {missing_columns}'}
        
        # 检查数据质量
        if len(df) == 0:
            return {'valid': False, 'message': '文件为空'}
        
        # 检查数据类型
        if 'order_time' in df.columns:
            df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
            invalid_dates = df['order_time'].isna().sum()
            if invalid_dates > 0:
                return {'valid': False, 'message': f'存在 {invalid_dates} 个无效的时间格式'}
        
        # 检查数值类型
        numeric_columns = ['quantity', 'price']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid_numeric = df[col].isna().sum()
                if invalid_numeric > 0:
                    return {'valid': False, 'message': f'存在 {invalid_numeric} 个无效的 {col} 值'}
        
        return {'valid': True, 'message': f'数据验证通过，共 {len(df)} 条记录'}
    except Exception as e:
        return {'valid': False, 'message': f'验证失败: {str(e)}'}
