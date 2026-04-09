import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from database import get_all_orders
import mysql.connector
from datetime import datetime, timedelta

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'breakfast_system'
}

def sales_prediction(days=7):
    """预测未来销售额"""
    try:
        # 获取历史销售数据
        orders = get_all_orders()
        df = pd.DataFrame(orders)
        
        # 按日期分组统计销售额
        df['order_time'] = pd.to_datetime(df['order_time'])
        df['date'] = df['order_time'].dt.date
        daily_sales = df.groupby('date')['total_amount'].sum().reset_index()
        daily_sales.columns = ['date', 'sales']
        
        # 准备训练数据
        daily_sales['date_num'] = (daily_sales['date'] - daily_sales['date'].min()).dt.days
        X = daily_sales[['date_num']].values
        y = daily_sales['sales'].values
        
        # 训练模型
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测未来销售额
        last_date = daily_sales['date'].max()
        predictions = []
        
        for i in range(1, days + 1):
            future_date = last_date + timedelta(days=i)
            future_date_num = (future_date - daily_sales['date'].min()).days
            predicted_sales = model.predict([[future_date_num]])[0]
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_sales': round(predicted_sales, 2)
            })
        
        return {'success': True, 'data': predictions}
    except Exception as e:
        return {'success': False, 'message': f'预测失败: {str(e)}'}

def product_association_analysis(min_support=0.01):
    """商品关联分析"""
    try:
        # 获取订单数据
        orders = get_all_orders()
        df = pd.DataFrame(orders)
        
        # 按订单分组，获取每个订单的商品列表
        order_products = df.groupby('order_id')['product_name'].apply(list).reset_index()
        
        # 计算商品之间的关联度
        from mlxtend.frequent_patterns import apriori, association_rules
        
        # 创建商品交易矩阵
        products = df['product_name'].unique()
        transaction_matrix = []
        
        for _, row in order_products.iterrows():
            transaction = {}
            for product in products:
                transaction[product] = 1 if product in row['product_name'] else 0
            transaction_matrix.append(transaction)
        
        transaction_df = pd.DataFrame(transaction_matrix)
        
        # 找出频繁项集
        frequent_itemsets = apriori(transaction_df, min_support=min_support, use_colnames=True)
        
        # 生成关联规则
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
        
        # 整理结果
        associations = []
        for _, row in rules.iterrows():
            associations.append({
                'antecedents': list(row['antecedents']),
                'consequents': list(row['consequents']),
                'support': round(row['support'], 4),
                'confidence': round(row['confidence'], 4),
                'lift': round(row['lift'], 4)
            })
        
        return {'success': True, 'data': associations}
    except Exception as e:
        return {'success': False, 'message': f'关联分析失败: {str(e)}'}

def customer_segmentation():
    """客户消费行为分析"""
    try:
        # 获取订单数据
        orders = get_all_orders()
        df = pd.DataFrame(orders)
        
        # 按客户分组（这里用order_id模拟客户ID）
        customer_df = df.groupby('order_id').agg({
            'total_amount': 'sum',
            'order_time': 'count'
        }).reset_index()
        customer_df.columns = ['customer_id', 'total_spent', 'order_count']
        
        # 计算客单价
        customer_df['avg_order_value'] = customer_df['total_spent'] / customer_df['order_count']
        
        # 简单的客户分类
        segments = []
        for _, row in customer_df.iterrows():
            if row['total_spent'] > 100:
                segment = '高价值客户'
            elif row['total_spent'] > 50:
                segment = '中等价值客户'
            else:
                segment = '低价值客户'
            
            segments.append({
                'customer_id': row['customer_id'],
                'total_spent': round(row['total_spent'], 2),
                'order_count': row['order_count'],
                'avg_order_value': round(row['avg_order_value'], 2),
                'segment': segment
            })
        
        # 统计各段客户数量
        segment_counts = pd.DataFrame(segments).groupby('segment').size().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        return {
            'success': True,
            'segments': segments,
            'segment_counts': segment_counts.to_dict('records')
        }
    except Exception as e:
        return {'success': False, 'message': f'客户分析失败: {str(e)}'}

def sales_forecast_by_category():
    """按商品类别预测销售额"""
    try:
        # 获取历史销售数据
        orders = get_all_orders()
        df = pd.DataFrame(orders)
        
        # 按日期和类别分组统计销售额
        df['order_time'] = pd.to_datetime(df['order_time'])
        df['date'] = df['order_time'].dt.date
        category_sales = df.groupby(['date', 'category'])['amount'].sum().reset_index()
        
        # 预测每个类别的销售额
        predictions = []
        categories = category_sales['category'].unique()
        
        for category in categories:
            cat_data = category_sales[category_sales['category'] == category]
            if len(cat_data) < 3:  # 数据不足，跳过
                continue
            
            # 准备训练数据
            cat_data['date_num'] = (cat_data['date'] - cat_data['date'].min()).dt.days
            X = cat_data[['date_num']].values
            y = cat_data['amount'].values
            
            # 训练模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测未来7天
            last_date = cat_data['date'].max()
            for i in range(1, 8):
                future_date = last_date + timedelta(days=i)
                future_date_num = (future_date - cat_data['date'].min()).days
                predicted_sales = model.predict([[future_date_num]])[0]
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'predicted_sales': round(predicted_sales, 2)
                })
        
        return {'success': True, 'data': predictions}
    except Exception as e:
        return {'success': False, 'message': f'类别预测失败: {str(e)}'}
