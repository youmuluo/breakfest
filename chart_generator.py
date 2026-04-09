import plotly.graph_objects as go
import plotly.express as px
from database import get_sales_trend_7d, get_top_products, get_time_period_sales, get_category_sales, clean_and_process_data

def create_sales_trend_chart():
    """创建销售趋势图"""
    data = get_sales_trend_7d()
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[d['date'] for d in data],
        y=[d['total'] for d in data],
        mode='lines+markers',
        name='销售额',
        line=dict(color='#1890ff', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='近7天销售趋势',
        xaxis_title='日期',
        yaxis_title='销售额(元)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_top_products_chart():
    """创建热销商品排行图"""
    data = get_top_products()
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[d['name'] for d in data],
        y=[d['total_quantity'] for d in data],
        marker_color='#52c41a',
        text=[d['total_quantity'] for d in data],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='热销商品排行',
        xaxis_title='商品名称',
        yaxis_title='销售数量',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_time_period_chart():
    """创建时段销售分布图"""
    data = get_time_period_sales()
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=[d['time_period'] for d in data],
        values=[d['total'] for d in data],
        hole=0.4,
        marker=dict(colors=['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'])
    ))
    
    fig.update_layout(
        title='时段销售分布',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_category_sales_chart():
    """创建分类销售占比图"""
    data = get_category_sales()
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=[d['category'] for d in data],
        values=[d['total_sales'] for d in data],
        hole=0.4
    ))
    
    fig.update_layout(
        title='销售结构占比',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_weekly_hot_products_chart():
    """创建上周爆款菜品图表"""
    df = clean_and_process_data()
    from datetime import date, timedelta
    
    last_week_start = date.today() - timedelta(days=14)
    last_week_end = date.today() - timedelta(days=7)
    
    last_week_data = df[(df['date'] >= last_week_start) & (df['date'] < last_week_end)]
    hot_products = last_week_data.groupby('name').agg(
        total_quantity=('quantity', 'sum')
    ).reset_index().sort_values('total_quantity', ascending=False).head(5)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hot_products['name'],
        y=hot_products['total_quantity'],
        marker_color='#ff7a45',
        text=hot_products['total_quantity'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='上周爆款菜品',
        xaxis_title='菜品名称',
        yaxis_title='销售数量',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_hourly_sales_chart():
    """创建每小时销售分布图"""
    df = clean_and_process_data()
    hourly_sales = df.groupby('hour')['total_amount'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_sales['hour'],
        y=hourly_sales['total_amount'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#1890ff', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='每小时销售分布',
        xaxis_title='小时',
        yaxis_title='销售额(元)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_product_performance_chart():
    """创建商品表现综合图表"""
    df = clean_and_process_data()
    product_stats = df.groupby('name').agg(
        total_quantity=('quantity', 'sum'),
        total_amount=('item_amount', 'sum'),
        avg_price=('price', 'mean')
    ).reset_index().sort_values('total_quantity', ascending=False).head(10)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=product_stats['name'],
        y=product_stats['total_quantity'],
        name='销售数量',
        marker_color='#1890ff'
    ))
    
    fig.add_trace(go.Scatter(
        x=product_stats['name'],
        y=product_stats['total_amount'],
        name='销售金额',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#52c41a', width=3)
    ))
    
    fig.update_layout(
        title='商品表现综合分析',
        xaxis_title='商品名称',
        yaxis=dict(title='销售数量', side='left'),
        yaxis2=dict(title='销售金额(元)', side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        barmode='group'
    )
    
    return fig
