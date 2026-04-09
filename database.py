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

@cached(ttl=600)
def get_morning_peak_analysis() -> Dict[str, Any]:
    """早高峰时段分析（6:00-10:00）"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                HOUR(order_time) as hour,
                COUNT(DISTINCT order_no) as order_count,
                SUM(total_amount) as total_sales,
                COUNT(*) as item_count
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE HOUR(order_time) BETWEEN 6 AND 9
            GROUP BY HOUR(order_time)
            ORDER BY hour
        """))
        
        rows = result.fetchall()
        hourly_data = [
            {
                'hour': f"{row.hour}:00-{row.hour+1}:00",
                'order_count': int(row.order_count),
                'total_sales': float(row.total_sales),
                'item_count': int(row.item_count)
            }
            for row in rows
        ]
        
        total_result = connection.execute(text("""
            SELECT SUM(total_amount) as total
            FROM orders
            WHERE HOUR(order_time) BETWEEN 6 AND 9
        """))
        total_row = total_result.fetchone()
        morning_peak_total = float(total_row.total) if total_row.total else 0.0
        
        all_result = connection.execute(text("SELECT SUM(total_amount) as total FROM orders"))
        all_row = all_result.fetchone()
        all_total = float(all_row.total) if all_row.total else 0.0
        
        peak_ratio = (morning_peak_total / all_total * 100) if all_total > 0 else 0
        
        return {
            'hourly_data': hourly_data,
            'morning_peak_total': morning_peak_total,
            'peak_ratio': round(peak_ratio, 2)
        }

@cached(ttl=600)
def get_dish_ranking(top_n: int = 20) -> List[Dict[str, Any]]:
    """菜品销量排行"""
    with engine.connect() as connection:
        result = connection.execute(text(f"""
            SELECT 
                p.name as dish_name,
                p.category,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.amount) as total_amount,
                COUNT(DISTINCT o.order_no) as order_count,
                ROUND(AVG(oi.amount / oi.quantity), 2) as avg_price
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            GROUP BY p.id, p.name, p.category
            ORDER BY total_quantity DESC
            LIMIT {top_n}
        """))
        
        rows = result.fetchall()
        return [
            {
                'dish_name': row.dish_name,
                'category': row.category,
                'total_quantity': int(row.total_quantity),
                'total_amount': float(row.total_amount),
                'order_count': int(row.order_count),
                'avg_price': float(row.avg_price)
            }
            for row in rows
        ]

@cached(ttl=600)
def get_channel_comparison() -> Dict[str, Any]:
    """堂食/外卖渠道对比分析"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                channel,
                SUM(total_amount) as total_sales,
                COUNT(DISTINCT order_no) as order_count,
                COUNT(*) as item_count
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE channel IS NOT NULL
            GROUP BY channel
        """))
        
        rows = result.fetchall()
        channel_data = [
            {
                'channel': row.channel,
                'total_sales': float(row.total_sales),
                'order_count': int(row.order_count),
                'item_count': int(row.item_count)
            }
            for row in rows
        ]
        
        total_result = connection.execute(text("""
            SELECT SUM(total_amount) as total
            FROM orders
            WHERE channel IS NOT NULL
        """))
        total_row = total_result.fetchone()
        total_sales = float(total_row.total) if total_row.total else 0.0
        
        for channel in channel_data:
            channel['sales_ratio'] = round((channel['total_sales'] / total_sales * 100), 2) if total_sales > 0 else 0
        
        return {
            'channel_data': channel_data,
            'total_sales': total_sales
        }

@cached(ttl=600)
def get_order_value_analysis() -> Dict[str, Any]:
    """客单价分析"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                total_amount
            FROM orders
            WHERE total_amount > 0
        """))
        
        rows = result.fetchall()
        amounts = [float(row.total_amount) for row in rows]
        
        if not amounts:
            return {
                'avg_order_value': 0.0,
                'median_order_value': 0.0,
                'distribution': []
            }
        
        avg_value = sum(amounts) / len(amounts)
        sorted_amounts = sorted(amounts)
        median_value = sorted_amounts[len(sorted_amounts) // 2]
        
        bins = [
            (0, 10, '0-10元'),
            (10, 20, '10-20元'),
            (20, 30, '20-30元'),
            (30, 50, '30-50元'),
            (50, 100, '50-100元'),
            (100, float('inf'), '100元以上')
        ]
        
        distribution = []
        for min_val, max_val, label in bins:
            count = sum(1 for amount in amounts if min_val <= amount < max_val)
            ratio = round((count / len(amounts) * 100), 2)
            distribution.append({
                'range': label,
                'count': count,
                'ratio': ratio
            })
        
        return {
            'avg_order_value': round(avg_value, 2),
            'median_order_value': round(median_value, 2),
            'distribution': distribution
        }

@cached(ttl=600)
def get_repeat_customer_analysis() -> Dict[str, Any]:
    """复购用户分析"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                customer_id,
                COUNT(DISTINCT order_no) as order_count,
                SUM(total_amount) as total_amount
            FROM orders
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        """))
        
        rows = result.fetchall()
        
        if not rows:
            return {
                'total_customers': 0,
                'repeat_customers': 0,
                'repeat_ratio': 0.0,
                'frequency_distribution': []
            }
        
        customer_data = [
            {
                'customer_id': row.customer_id,
                'order_count': int(row.order_count),
                'total_amount': float(row.total_amount)
            }
            for row in rows
        ]
        
        total_customers = len(customer_data)
        repeat_customers = sum(1 for c in customer_data if c['order_count'] >= 2)
        repeat_ratio = round((repeat_customers / total_customers * 100), 2) if total_customers > 0 else 0
        
        frequency_bins = [
            (1, 1, '1次'),
            (2, 2, '2次'),
            (3, 3, '3次'),
            (4, 5, '4-5次'),
            (6, float('inf'), '6次以上')
        ]
        
        frequency_distribution = []
        for min_val, max_val, label in frequency_bins:
            count = sum(1 for c in customer_data if min_val <= c['order_count'] <= max_val)
            ratio = round((count / total_customers * 100), 2) if total_customers > 0 else 0
            frequency_distribution.append({
                'frequency': label,
                'count': count,
                'ratio': ratio
            })
        
        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'repeat_ratio': repeat_ratio,
            'frequency_distribution': frequency_distribution
        }

