import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from database import (
    get_total_sales, get_today_sales, get_avg_order_value,
    get_weekly_hot_products, get_specific_time_period_sales,
    get_morning_peak_analysis, get_dish_ranking,
    get_channel_comparison, get_order_value_analysis,
    get_repeat_customer_analysis, export_weekly_report_to_excel
)
from chart_generator import (
    create_sales_trend_chart, create_top_products_chart,
    create_time_period_chart, create_category_sales_chart
)
import base64
import io
from datetime import datetime

app = dash.Dash(__name__, suppress_callback_exceptions=True)

COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'dark': '#1f2937',
    'light': '#f3f4f6'
}

GRADIENT = {
    'blue': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'green': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    'orange': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'purple': 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)'
}

def create_kpi_card(title, value, icon, color, subtitle=''):
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icon, style={
                    'fontSize': '32px',
                    'opacity': '0.9'
                })
            ], style={
                'background': 'rgba(255,255,255,0.2)',
                'width': '60px',
                'height': '60px',
                'borderRadius': '16px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }),
            html.Div([
                html.P(title, style={
                    'margin': '0',
                    'color': 'rgba(255,255,255,0.8)',
                    'fontSize': '14px',
                    'fontWeight': '500'
                }),
                html.H2(value, style={
                    'margin': '8px 0 0 0',
                    'color': 'white',
                    'fontSize': '32px',
                    'fontWeight': '700',
                    'lineHeight': '1.2'
                }),
                html.P(subtitle, style={
                    'margin': '4px 0 0 0',
                    'color': 'rgba(255,255,255,0.7)',
                    'fontSize': '13px'
                }) if subtitle else None
            ], style={
                'marginLeft': '20px'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        })
    ], style={
        'background': color,
        'borderRadius': '20px',
        'padding': '24px',
        'boxShadow': '0 10px 40px rgba(0,0,0,0.1)',
        'transition': 'all 0.3s cubic-bezier(0.4,0,0.2,1)',
        'cursor': 'pointer'
    }, className='kpi-card')

def create_chart_card(title, content, height='400px'):
    return html.Div([
        html.Div([
            html.H3(title, style={
                'margin': '0',
                'color': '#1f2937',
                'fontSize': '18px',
                'fontWeight': '600'
            }),
            html.Div([
                html.Span('📊', style={'marginRight': '8px'}),
                html.Span('实时更新', style={
                    'color': '#6b7280',
                    'fontSize': '13px'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'marginBottom': '20px',
            'paddingBottom': '16px',
            'borderBottom': '2px solid #f3f4f6'
        }),
        html.Div(content, style={
            'height': height
        })
    ], style={
        'background': 'white',
        'borderRadius': '20px',
        'padding': '24px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.06)',
        'transition': 'all 0.3s ease'
    }, className='chart-card')

app.layout = html.Div([
    dcc.Store(id='data-store'),
    dcc.Interval(
        id='interval-component',
        interval=300000,
        n_intervals=0
    ),
    
    html.Div([
        html.Div([
            html.H1('🍜 早餐店数据分析系统', style={
                'margin': '0',
                'color': 'white',
                'fontSize': '28px',
                'fontWeight': '700',
                'letterSpacing': '-0.5px'
            }),
            html.P('数据驱动的餐饮运营决策平台', style={
                'margin': '8px 0 0 0',
                'color': 'rgba(255,255,255,0.8)',
                'fontSize': '14px'
            })
        ], style={
            'flex': '1'
        }),
        html.Div([
            html.Div([
                html.Span('🟢', style={'marginRight': '8px'}),
                html.Span('系统运行正常', style={
                    'color': 'white',
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'background': 'rgba(255,255,255,0.15)',
                'padding': '10px 20px',
                'borderRadius': '12px'
            }),
            html.Div(id='current-time', style={
                'marginLeft': '20px',
                'color': 'rgba(255,255,255,0.9)',
                'fontSize': '14px'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        })
    ], style={
        'background': GRADIENT['blue'],
        'padding': '30px 40px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'space-between',
        'boxShadow': '0 4px 20px rgba(102,126,234,0.3)'
    }),
    
    html.Div([
        html.Div([
            html.Div([
                dcc.Tabs(id='main-tabs', value='overview', children=[
                    dcc.Tab(label='📈 数据概览', value='overview', className='custom-tab', selected_className='custom-tab--selected'),
                    dcc.Tab(label='⏰ 时段分析', value='time', className='custom-tab', selected_className='custom-tab--selected'),
                    dcc.Tab(label='🥟 菜品分析', value='products', className='custom-tab', selected_className='custom-tab--selected'),
                    dcc.Tab(label='👥 客户分析', value='customers', className='custom-tab', selected_className='custom-tab--selected'),
                    dcc.Tab(label='📋 报表导出', value='export', className='custom-tab', selected_className='custom-tab--selected')
                ], style={
                    'display': 'flex',
                    'gap': '8px',
                    'borderBottom': 'none'
                })
            ], style={
                'background': 'white',
                'padding': '12px',
                'borderRadius': '16px',
                'boxShadow': '0 2px 12px rgba(0,0,0,0.06)'
            })
        ], style={
            'marginBottom': '24px'
        }),
        
        html.Div(id='tab-content')
        
    ], style={
        'padding': '30px 40px',
        'background': '#f8fafc',
        'minHeight': 'calc(100vh - 120px)'
    })
], style={
    'minHeight': '100vh',
    'background': '#f8fafc'
})

@app.callback(Output('current-time', 'children'),
              Input('interval-component', 'n_intervals'))
def update_time(n):
    return datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

@app.callback(Output('tab-content', 'children'),
              Input('main-tabs', 'value'))
def render_tab_content(tab):
    if tab == 'overview':
        return html.Div([
            html.Div([
                create_kpi_card(
                    '总销售额',
                    html.Span([
                        html.Span('¥', style={'fontSize': '24px', 'fontWeight': '400'}),
                        html.Span(id='total-sales-display', children='加载中...')
                    ], style={'display': 'flex', 'alignItems': 'baseline'}),
                    '💰',
                    GRADIENT['blue'],
                    '累计至今'
                ),
                create_kpi_card(
                    '今日销售额',
                    html.Span([
                        html.Span('¥', style={'fontSize': '24px', 'fontWeight': '400'}),
                        html.Span(id='today-sales-display', children='加载中...')
                    ], style={'display': 'flex', 'alignItems': 'baseline'}),
                    '📅',
                    GRADIENT['green'],
                    '实时更新'
                ),
                create_kpi_card(
                    '客单价',
                    html.Span([
                        html.Span('¥', style={'fontSize': '24px', 'fontWeight': '400'}),
                        html.Span(id='avg-order-value-display', children='加载中...')
                    ], style={'display': 'flex', 'alignItems': 'baseline'}),
                    '🛒',
                    GRADIENT['orange'],
                    '平均每单'
                ),
                create_kpi_card(
                    '复购率',
                    html.Span([
                        html.Span(id='repeat-rate-display', children='加载中...'),
                        html.Span('%', style={'fontSize': '24px', 'fontWeight': '400'})
                    ], style={'display': 'flex', 'alignItems': 'baseline'}),
                    '🔄',
                    GRADIENT['purple'],
                    '客户回头率'
                )
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '24px',
                'marginBottom': '24px'
            }),
            
            html.Div([
                create_chart_card(
                    '📈 销售趋势',
                    dcc.Graph(id='sales-trend-chart', config={'displayModeBar': False}),
                    '380px'
                ),
                create_chart_card(
                    '🏆 热销商品TOP10',
                    dcc.Graph(id='top-products-chart', config={'displayModeBar': False}),
                    '380px'
                )
            ], style={
                'display': 'grid',
                'gridTemplateColumns': '2fr 1fr',
                'gap': '24px',
                'marginBottom': '24px'
            }),
            
            html.Div([
                create_chart_card(
                    '🕐 时段销售分布',
                    dcc.Graph(id='time-period-chart', config={'displayModeBar': False}),
                    '350px'
                ),
                create_chart_card(
                    '📊 堂食/外卖对比',
                    dcc.Graph(id='channel-chart', config={'displayModeBar': False}),
                    '350px'
                )
            ], style={
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '24px'
            })
        ])
    
    elif tab == 'time':
        return html.Div([
            html.Div([
                html.Div([
                    html.H2('⏰ 早高峰时段分析', style={
                        'margin': '0 0 8px 0',
                        'color': '#1f2937',
                        'fontSize': '24px',
                        'fontWeight': '700'
                    }),
                    html.P('深度分析6:00-10:00早餐高峰时段的销售数据', style={
                        'margin': '0',
                        'color': '#6b7280',
                        'fontSize': '14px'
                    })
                ], style={
                    'marginBottom': '24px'
                }),
                
                html.Div([
                    html.Div(id='morning-peak-cards', style={
                        'display': 'grid',
                        'gridTemplateColumns': 'repeat(4, 1fr)',
                        'gap': '20px',
                        'marginBottom': '24px'
                    }),
                    create_chart_card(
                        '📊 早高峰时段销售明细',
                        dcc.Graph(id='morning-peak-chart', config={'displayModeBar': False}),
                        '400px'
                    )
                ])
            ], style={
                'background': 'white',
                'padding': '32px',
                'borderRadius': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.06)'
            })
        ])
    
    elif tab == 'products':
        return html.Div([
            html.Div([
                html.H2('🥟 菜品销量分析', style={
                    'margin': '0 0 24px 0',
                    'color': '#1f2937',
                    'fontSize': '24px',
                    'fontWeight': '700'
                }),
                create_chart_card(
                    '🏆 菜品销量排行榜',
                    html.Div(id='dish-ranking-table'),
                    '500px'
                )
            ], style={
                'background': 'white',
                'padding': '32px',
                'borderRadius': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.06)'
            })
        ])
    
    elif tab == 'customers':
        return html.Div([
            html.Div([
                html.H2('👥 客户分析', style={
                    'margin': '0 0 24px 0',
                    'color': '#1f2937',
                    'fontSize': '24px',
                    'fontWeight': '700'
                }),
                html.Div([
                    create_chart_card(
                        '💰 客单价分布',
                        dcc.Graph(id='order-value-chart', config={'displayModeBar': False}),
                        '400px'
                    ),
                    create_chart_card(
                        '🔄 复购用户分析',
                        dcc.Graph(id='repeat-customer-chart', config={'displayModeBar': False}),
                        '400px'
                    )
                ], style={
                    'display': 'grid',
                    'gridTemplateColumns': '1fr 1fr',
                    'gap': '24px'
                })
            ], style={
                'background': 'white',
                'padding': '32px',
                'borderRadius': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.06)'
            })
        ])
    
    elif tab == 'export':
        return html.Div([
            html.Div([
                html.H2('📋 报表导出', style={
                    'margin': '0 0 24px 0',
                    'color': '#1f2937',
                    'fontSize': '24px',
                    'fontWeight': '700'
                }),
                html.Div([
                    html.Button('📥 导出周报', id='export-btn', n_clicks=0, style={
                        'background': GRADIENT['blue'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '16px 32px',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'borderRadius': '12px',
                        'cursor': 'pointer',
                        'boxShadow': '0 4px 12px rgba(102,126,234,0.3)',
                        'transition': 'all 0.3s ease'
                    }),
                    html.Div(id='export-status', style={
                        'marginTop': '16px',
                        'padding': '12px 20px',
                        'borderRadius': '8px',
                        'display': 'none'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '60px 0'
                })
            ], style={
                'background': 'white',
                'padding': '32px',
                'borderRadius': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.06)'
            })
        ])

@app.callback(
    [Output('total-sales-display', 'children'),
     Output('today-sales-display', 'children'),
     Output('avg-order-value-display', 'children'),
     Output('repeat-rate-display', 'children')],
    Input('interval-component', 'n_intervals'))
def update_kpis(n):
    try:
        total_sales = get_total_sales()
        today_sales = get_today_sales()
        avg_order = get_order_value_analysis()
        repeat_customer = get_repeat_customer_analysis()
        
        return (
            f"{total_sales.get('total_sales', 0):,.2f}",
            f"{today_sales.get('today_sales', 0):,.2f}",
            f"{avg_order.get('avg_order_value', 0):,.2f}",
            f"{repeat_customer.get('repeat_rate', 0):.1f}"
        )
    except:
        return ('0.00', '0.00', '0.00', '0.0')

@app.callback(Output('sales-trend-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_sales_trend(n):
    try:
        fig = create_sales_trend_chart()
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('top-products-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_top_products(n):
    try:
        fig = create_top_products_chart()
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('time-period-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_time_period(n):
    try:
        fig = create_time_period_chart()
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('channel-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_channel(n):
    try:
        data = get_channel_comparison()
        channel_data = data.get('channel_data', [])
        
        fig = go.Figure(data=[
            go.Pie(
                labels=[d['渠道'] for d in channel_data],
                values=[d['销售额'] for d in channel_data],
                hole=0.4,
                marker=dict(colors=['#667eea', '#764ba2']),
                textinfo='label+percent',
                textposition='outside'
            )
        ])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('morning-peak-cards', 'children'),
              Input('interval-component', 'n_intervals'))
def update_morning_peak_cards(n):
    try:
        data = get_morning_peak_analysis()
        return [
            html.Div([
                html.P('早高峰销售额', style={'color': '#667eea', 'fontSize': '13px', 'margin': '0'}),
                html.H3(f'¥{data.get("total_peak_sales", 0):,.2f}', style={'color': '#1f2937', 'fontSize': '28px', 'margin': '8px 0 0 0'})
            ], style={'background': '#f0f4ff', 'padding': '20px', 'borderRadius': '16px', 'textAlign': 'center'}),
            html.Div([
                html.P('早高峰订单数', style={'color': '#10b981', 'fontSize': '13px', 'margin': '0'}),
                html.H3(f'{data.get("total_peak_orders", 0)}', style={'color': '#1f2937', 'fontSize': '28px', 'margin': '8px 0 0 0'})
            ], style={'background': '#ecfdf5', 'padding': '20px', 'borderRadius': '16px', 'textAlign': 'center'}),
            html.Div([
                html.P('早高峰占比', style={'color': '#f59e0b', 'fontSize': '13px', 'margin': '0'}),
                html.H3(f'{data.get("peak_ratio", 0)}%', style={'color': '#1f2937', 'fontSize': '28px', 'margin': '8px 0 0 0'})
            ], style={'background': '#fef9e7', 'padding': '20px', 'borderRadius': '16px', 'textAlign': 'center'}),
            html.Div([
                html.P('分析时段', style={'color': '#ef4444', 'fontSize': '13px', 'margin': '0'}),
                html.H3('6:00-10:00', style={'color': '#1f2937', 'fontSize': '22px', 'margin': '8px 0 0 0'})
            ], style={'background': '#fef2f2', 'padding': '20px', 'borderRadius': '16px', 'textAlign': 'center'})
        ]
    except:
        return []

@app.callback(Output('morning-peak-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_morning_peak_chart(n):
    try:
        data = get_morning_peak_analysis()
        hourly = data.get('hourly_breakdown', [])
        
        fig = go.Figure(data=[
            go.Bar(
                name='销售额',
                x=[d['小时'] for d in hourly],
                y=[d['销售额'] for d in hourly],
                marker_color='#667eea',
                text=[f'¥{d["销售额"]:,.0f}' for d in hourly],
                textposition='auto'
            ),
            go.Scatter(
                name='订单数',
                x=[d['小时'] for d in hourly],
                y=[d['订单数'] for d in hourly],
                yaxis='y2',
                line=dict(color='#764ba2', width=3),
                mode='lines+markers'
            )
        ])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis2=dict(overlaying='y', side='right'),
            showlegend=False
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('dish-ranking-table', 'children'),
              Input('interval-component', 'n_intervals'))
def update_dish_ranking(n):
    try:
        data = get_dish_ranking(top_n=20)
        df = pd.DataFrame(data)
        
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'name': '排名', 'id': '排名'},
                {'name': '商品名称', 'id': '商品名称'},
                {'name': '销售数量', 'id': '销售数量'},
                {'name': '销售金额', 'id': '销售金额'},
                {'name': '平均单价', 'id': '平均单价'}
            ],
            style_header={
                'backgroundColor': '#667eea',
                'color': 'white',
                'fontWeight': '600',
                'padding': '12px',
                'textAlign': 'center'
            },
            style_cell={
                'padding': '12px',
                'textAlign': 'center',
                'fontSize': '14px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8fafc'
                }
            ],
            page_size=10
        )
    except:
        return html.P('数据加载中...')

@app.callback(Output('order-value-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_order_value(n):
    try:
        data = get_order_value_analysis()
        distribution = data.get('price_distribution', [])
        
        fig = go.Figure(data=[
            go.Bar(
                x=[d['价格区间'] for d in distribution],
                y=[d['订单数'] for d in distribution],
                marker_color='#667eea',
                text=[f'{d["占比"]}%' for d in distribution],
                textposition='auto'
            )
        ])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('repeat-customer-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_repeat_customer(n):
    try:
        data = get_repeat_customer_analysis()
        freq = data.get('purchase_frequency', [])
        
        fig = go.Figure(data=[
            go.Pie(
                labels=[f'{d["购买次数"]}次' for d in freq],
                values=[d['客户数'] for d in freq],
                hole=0.4,
                marker=dict(colors=['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444'])
            )
        ])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig
    except:
        return go.Figure()

@app.callback(Output('export-status', 'children'),
              Output('export-status', 'style'),
              Input('export-btn', 'n_clicks'),
              prevent_initial_call=True)
def export_report(n_clicks):
    if n_clicks:
        try:
            filename = export_weekly_report_to_excel()
            return (
                f'✅ 导出成功！文件：{filename}',
                {'display': 'block', 'background': '#ecfdf5', 'color': '#065f46'}
            )
        except Exception as e:
            return (
                f'❌ 导出失败：{str(e)}',
                {'display': 'block', 'background': '#fef2f2', 'color': '#991b1b'}
            )
    return '', {'display': 'none'}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>早餐店数据分析系统</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            .custom-tab {
                background-color: transparent !important;
                border: none !important;
                padding: 12px 24px !important;
                color: #6b7280 !important;
                font-weight: 500 !important;
                font-size: 14px !important;
                border-radius: 10px !important;
                transition: all 0.2s ease !important;
            }
            .custom-tab:hover {
                background-color: #f3f4f6 !important;
                color: #374151 !important;
            }
            .custom-tab--selected {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                box-shadow: 0 4px 12px rgba(102,126,234,0.3) !important;
            }
            .kpi-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
            }
            .chart-card:hover {
                box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    import pandas as pd
    app.run(debug=False, port=8051)
