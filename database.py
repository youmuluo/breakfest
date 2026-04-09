from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date, timedelta
from cache import cached
from typing import List, Dict, Any

DATABASE_URL = "mysql+pymysql://root:you136018@localhost/breakfast_system"

engine = create_engine(DATABASE_URL)

def test_connection() -> Any:
    """测试数据库连接"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.fetchone()

def get_all_products() -> List[Dict[str, Any]]:
    """获取所有商品信息"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM products"))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

@cached(ttl=300)  # 5分钟缓存
def get_total_sales() -> Dict[str, float]:
    """获取总销售额"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT SUM(total_amount) AS total_sales FROM orders"))
        row = result.fetchone()
        return {"total_sales": float(row.total_sales) if row.total_sales else 0.0}

@cached(ttl=600)  # 10分钟缓存
def get_top_products() -> List[Dict[str, Any]]:
    """获取热销商品排行"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                p.name,
                SUM(oi.quantity) AS total_quantity,
                SUM(oi.amount) AS total_amount
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.name
            ORDER BY total_quantity DESC
        """))
        
        rows = result.fetchall()
        return [
            {
                "name": row.name,
                "total_quantity": int(row.total_quantity),
                "total_amount": float(row.total_amount)
            }
            for row in rows
        ]

@cached(ttl=600)  # 10分钟缓存
def get_sales_trend() -> List[Dict[str, Any]]:
    """获取销售趋势"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                DATE(order_time) AS sale_date,
                SUM(total_amount) AS daily_total
            FROM orders
            GROUP BY DATE(order_time)
            ORDER BY sale_date
        """))

        rows = result.fetchall()
        return [
            {
                "date": str(row.sale_date),
                "total": float(row.daily_total)
            }
            for row in rows
        ]

@cached(ttl=600)  # 10分钟缓存
def get_time_period_sales() -> List[Dict[str, Any]]:
    """获取时段销售分布"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                CASE 
                    WHEN HOUR(order_time) BETWEEN 6 AND 7 THEN '06-08'
                    WHEN HOUR(order_time) BETWEEN 8 AND 9 THEN '08-10'
                    WHEN HOUR(order_time) BETWEEN 10 AND 11 THEN '10-12'
                    ELSE '其他'
                END AS time_period,
                SUM(total_amount) AS total
            FROM orders
            GROUP BY time_period
        """))

        rows = result.fetchall()
        return [
            {
                "time_period": row.time_period,
                "total": float(row.total)
            }
            for row in rows
        ]

@cached(ttl=300)  # 5分钟缓存
def get_today_sales() -> Dict[str, float]:
    """获取今日销售额"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT SUM(total_amount) AS today_total
            FROM orders
            WHERE DATE(order_time) = CURDATE()
        """))
        row = result.fetchone()
        return {"today_sales": float(row.today_total) if row.today_total else 0.0}

@cached(ttl=600)  # 10分钟缓存
def get_avg_order_value() -> Dict[str, float]:
    """获取客单价"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                ROUND(SUM(total_amount) / COUNT(*), 2) AS avg_order_value
            FROM orders
        """))
        row = result.fetchone()
        return {
            "avg_order_value": float(row.avg_order_value) if row.avg_order_value else 0.0
        }

@cached(ttl=600)  # 10分钟缓存
def get_category_sales() -> List[Dict[str, Any]]:
    """获取分类销售数据"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                p.category,
                SUM(oi.amount) AS total_sales
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.category
            ORDER BY total_sales DESC
        """))

        rows = result.fetchall()

        return [
            {
                "category": row.category,
                "total_sales": float(row.total_sales)
            }
            for row in rows
        ]

@cached(ttl=300)  # 5分钟缓存
def get_sales_trend_7d() -> List[Dict[str, Any]]:
    """获取近7天销售趋势"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                DATE(order_time) AS sale_date,
                SUM(total_amount) AS daily_total
            FROM orders
            WHERE order_time >= (CURDATE() - INTERVAL 6 DAY)
            GROUP BY DATE(order_time)
            ORDER BY sale_date
        """))

        rows = result.fetchall()

    data_map = {str(r.sale_date): float(r.daily_total) for r in rows}
    result_list = []

    today = date.today()

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ds = d.isoformat()
        result_list.append({
            "date": ds,
            "total": data_map.get(ds, 0.0)
        })

    return result_list

def get_orders_dataframe() -> pd.DataFrame:
    """获取订单数据为Pandas DataFrame用于数据处理"""
    query = """
    SELECT 
        o.id, o.order_no, o.order_time, o.total_amount,
        p.id as product_id, p.name, p.category, p.price,
        oi.quantity, oi.amount as item_amount
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    """
    df = pd.read_sql(query, engine)
    
    df['order_time'] = pd.to_datetime(df['order_time'])
    df['date'] = df['order_time'].dt.date
    df['hour'] = df['order_time'].dt.hour
    
    return df

def clean_and_process_data() -> pd.DataFrame:
    """数据清洗和处理函数"""
    df = get_orders_dataframe()
    
    # 处理缺失值
    df = df.dropna(subset=['total_amount', 'quantity'])
    
    # 数据类型转换
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    
    # 异常值处理 - 移除负值
    df = df[(df['total_amount'] > 0) & (df['quantity'] > 0)]
    
    # 时间段分类
    df['time_period'] = pd.cut(df['hour'], 
                               bins=[0, 6, 8, 10, 12, 24], 
                               labels=['凌晨', '6-8点', '8-10点', '10-12点', '其他'])
    
    return df

@cached(ttl=3600)  # 1小时缓存
def get_weekly_hot_products() -> List[Dict[str, Any]]:
    """获取上周爆款菜品"""
    df = clean_and_process_data()
    last_week_start = date.today() - timedelta(days=14)
    last_week_end = date.today() - timedelta(days=7)
    
    last_week_data = df[(df['date'] >= last_week_start) & (df['date'] < last_week_end)]
    hot_products = last_week_data.groupby('name').agg(
        total_quantity=('quantity', 'sum'),
        total_amount=('item_amount', 'sum')
    ).reset_index().sort_values('total_quantity', ascending=False).head(5)
    
    return hot_products.to_dict('records')

def get_specific_time_period_sales(start_hour: int = 7, end_hour: int = 8) -> Dict[str, Any]:
    """获取特定时间段销售数据"""
    df = clean_and_process_data()
    specific_period_data = df[(df['hour'] >= start_hour) & (df['hour'] < end_hour)]
    return {
        'period': f'{start_hour}:00-{end_hour}:00',
        'total_sales': float(specific_period_data['total_amount'].sum()),
        'order_count': len(specific_period_data['order_no'].unique())
    }

def export_data_to_csv(filename: str = 'breakfast_data.csv') -> str:
    """导出数据到CSV文件"""
    df = clean_and_process_data()
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return filename

def export_data_to_excel(filename: str = 'breakfast_data.xlsx') -> str:
    """导出数据到Excel文件"""
    df = clean_and_process_data()
    df.to_excel(filename, index=False, engine='openpyxl')
    return filename

def export_sales_report_to_excel(filename: str = 'sales_report.xlsx') -> str:
    """导出销售报告到Excel文件"""
    df = clean_and_process_data()
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='原始数据', index=False)
        
        daily_sales = df.groupby('date').agg({
            'total_amount': 'sum',
            'order_no': 'nunique'
        }).reset_index()
        daily_sales.columns = ['日期', '总销售额', '订单数量']
        daily_sales.to_excel(writer, sheet_name='日销售汇总', index=False)
        
        product_sales = df.groupby('name').agg({
            'quantity': 'sum',
            'item_amount': 'sum'
        }).reset_index()
        product_sales.columns = ['商品名称', '销售数量', '销售金额']
        product_sales = product_sales.sort_values('销售数量', ascending=False)
        product_sales.to_excel(writer, sheet_name='商品销售排行', index=False)
        
        category_sales = df.groupby('category').agg({
            'item_amount': 'sum'
        }).reset_index()
        category_sales.columns = ['分类', '销售金额']
        category_sales = category_sales.sort_values('销售金额', ascending=False)
        category_sales.to_excel(writer, sheet_name='分类销售汇总', index=False)
    
    return filename

def export_weekly_report_to_excel(filename: str = 'weekly_report.xlsx') -> str:
    """导出周报告到Excel文件"""
    df = clean_and_process_data()
    
    last_week_start = date.today() - timedelta(days=14)
    last_week_end = date.today() - timedelta(days=7)
    
    last_week_data = df[(df['date'] >= last_week_start) & (df['date'] < last_week_end)]
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        last_week_data.to_excel(writer, sheet_name='上周数据', index=False)
        
        hot_products = last_week_data.groupby('name').agg({
            'quantity': 'sum',
            'item_amount': 'sum'
        }).reset_index()
        hot_products.columns = ['商品名称', '销售数量', '销售金额']
        hot_products = hot_products.sort_values('销售数量', ascending=False).head(10)
        hot_products.to_excel(writer, sheet_name='爆款商品', index=False)
        
        daily_sales = last_week_data.groupby('date').agg({
            'total_amount': 'sum',
            'order_no': 'nunique'
        }).reset_index()
        daily_sales.columns = ['日期', '总销售额', '订单数量']
        daily_sales.to_excel(writer, sheet_name='日销售汇总', index=False)
    
    return filename

