import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import requests
from database import get_total_sales, get_today_sales, get_avg_order_value, get_weekly_hot_products, get_specific_time_period_sales
from chart_generator import create_sales_trend_chart, create_top_products_chart, create_time_period_chart, create_category_sales_chart, create_weekly_hot_products_chart, create_hourly_sales_chart, create_product_performance_chart

app = dash.Dash(__name__)

# 现代化样式
app.layout = html.Div([
    # 顶部导航栏
    html.Div([
        html.Div([
            html.H1('早餐店数据分析系统', style={
                'color': 'white',
                'margin': '0',
                'fontSize': '24px',
                'fontWeight': '600'
            })
        ], style={
            'flex': '1',
            'display': 'flex',
            'alignItems': 'center'
        }),
        html.Div([
            html.P('实时数据监控', style={
                'color': 'rgba(255,255,255,0.8)',
                'margin': '0',
                'fontSize': '14px'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'paddingRight': '20px'
        })
    ], className='header', style={
        'background': 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
        'padding': '20px 30px',
        'display': 'flex',
        'alignItems': 'center',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
    }),
    
    # 主要内容区域
    html.Div([
        # KPI指标卡片
        html.Div([
            html.Div([
                html.Div([
                    html.Span('总销售额', style={
                        'color': '#666',
                        'fontSize': '14px',
                        'display': 'block',
                        'marginBottom': '8px'
                    }),
                    html.Span(id='total-sales', children='加载中...', style={
                        'fontSize': '28px',
                        'fontWeight': '600',
                        'color': '#1890ff',
                        'display': 'block'
                    }),
                    html.Span('¥', style={
                        'fontSize': '16px',
                        'fontWeight': '400',
                        'color': '#1890ff',
                        'marginRight': '4px',
                        'verticalAlign': 'top'
                    })
                ], style={
                    'flex': '1',
                    'display': 'flex',
                    'flexDirection': 'column'
                }),
                html.Div([
                    html.I(className='fas fa-chart-line', style={
                        'fontSize': '24px',
                        'color': 'rgba(24,144,255,0.2)'
                    })
                ], style={
                    'width': '60px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'height': '100%'
            })
        ], className='card', style={
            'flex': '1',
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
            'padding': '24px',
            'transition': 'all 0.3s ease',
            'cursor': 'pointer'
        }, id='kpi-card-1'),
        
        html.Div([
            html.Div([
                html.Span('今日销售额', style={
                    'color': '#666',
                    'fontSize': '14px',
                    'display': 'block',
                    'marginBottom': '8px'
                }),
                html.Span(id='today-sales', children='加载中...', style={
                    'fontSize': '28px',
                    'fontWeight': '600',
                    'color': '#52c41a',
                    'display': 'block'
                }),
                html.Span('¥', style={
                    'fontSize': '16px',
                    'fontWeight': '400',
                    'color': '#52c41a',
                    'marginRight': '4px',
                    'verticalAlign': 'top'
                })
            ], style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column'
            }),
            html.Div([
                html.I(className='fas fa-calendar-day', style={
                    'fontSize': '24px',
                    'color': 'rgba(82,196,26,0.2)'
                })
            ], style={
                'width': '60px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            })
        ], className='card', style={
            'flex': '1',
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
            'padding': '24px',
            'transition': 'all 0.3s ease',
            'cursor': 'pointer'
        }, id='kpi-card-2'),
        
        html.Div([
            html.Div([
                html.Span('客单价', style={
                    'color': '#666',
                    'fontSize': '14px',
                    'display': 'block',
                    'marginBottom': '8px'
                }),
                html.Span(id='avg-order-value', children='加载中...', style={
                    'fontSize': '28px',
                    'fontWeight': '600',
                    'color': '#faad14',
                    'display': 'block'
                }),
                html.Span('¥', style={
                    'fontSize': '16px',
                    'fontWeight': '400',
                    'color': '#faad14',
                    'marginRight': '4px',
                    'verticalAlign': 'top'
                })
            ], style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'column'
            }),
            html.Div([
                html.I(className='fas fa-shopping-cart', style={
                    'fontSize': '24px',
                    'color': 'rgba(250,173,20,0.2)'
                })
            ], style={
                'width': '60px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            })
        ], className='card', style={
            'flex': '1',
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
            'padding': '24px',
            'transition': 'all 0.3s ease',
            'cursor': 'pointer'
        }, id='kpi-card-3')
    ], className='kpi-container', style={
        'display': 'flex',
        'gap': '20px',
        'margin': '30px 0',
        'padding': '0 30px'
    }),
    
    # 图表区域
    html.Div([
        # 销售趋势图
        html.Div([
            html.Div([
                html.H3('销售趋势', style={
                    'color': '#333',
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'margin': '0 0 20px 0'
                }),
                dcc.Graph(
                    id='sales-trend-chart',
                    config={
                        'displayModeBar': False
                    }
                )
            ], style={
                'height': '100%'
            })
        ], className='card chart-container', style={
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
            'padding': '24px',
            'marginBottom': '20px'
        }),
        
        # 两列图表
        html.Div([
            html.Div([
                html.H3('时段销售分布', style={
                    'color': '#333',
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'margin': '0 0 20px 0'
                }),
                dcc.Graph(
                    id='time-period-chart',
                    config={
                        'displayModeBar': False
                    }
                )
            ], className='card', style={
                'flex': '1',
                'padding': '24px',
                'background': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.08)'
            }),
            
            html.Div([
                html.H3('销售结构占比', style={
                    'color': '#333',
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'margin': '0 0 20px 0'
                }),
                dcc.Graph(
                    id='category-sales-chart',
                    config={
                        'displayModeBar': False
                    }
                )
            ], className='card', style={
                'flex': '1',
                'padding': '24px',
                'background': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.08)'
            })
        ], className='two-column', style={
            'display': 'flex',
            'gap': '20px',
            'marginBottom': '20px'
        }),
        
        # 热销商品排行
        html.Div([
            html.H3('热销商品排行', style={
                'color': '#333',
                'fontSize': '18px',
                'fontWeight': '600',
                'margin': '0 0 20px 0'
            }),
            dcc.Graph(
                id='top-products-chart',
                config={
                    'displayModeBar': False
                }
            )
        ], className='card chart-container', style={
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
            'padding': '24px',
            'marginBottom': '20px'
        }),
        
        # 高级分析功能
        html.Div([
            html.H3('高级分析功能', style={
                'color': '#333',
                'fontSize': '18px',
                'fontWeight': '600',
                'margin': '0 0 20px 0'
            }),
            
            # 上周爆款菜品查询
            html.Div([
                html.Div([
                    html.H4('查询上周爆款菜品', style={
                        'color': '#666',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'margin': '0 0 15px 0'
                    }),
                    html.Button('查询', id='btn-weekly-hot', n_clicks=0, style={
                        'background': 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '12px 24px',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'transition': 'all 0.3s ease'
                    }),
                    html.Div(id='weekly-hot-result', style={
                        'marginTop': '20px'
                    })
                ])
            ], style={
                'background': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                'padding': '24px',
                'marginBottom': '20px'
            }),
            
            # 特定时间段查询
            html.Div([
                html.H4('查询特定时间段订单量', style={
                    'color': '#666',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'margin': '0 0 15px 0'
                }),
                html.Div([
                    html.Div([
                        html.Label('开始时间：', style={
                            'color': '#666',
                            'fontSize': '14px',
                            'marginBottom': '8px',
                            'display': 'block'
                        }),
                        dcc.Dropdown(
                            id='start-hour',
                            options=[{'label': f'{i}:00', 'value': i} for i in range(6, 12)],
                            value=7,
                            style={
                                'borderRadius': '8px',
                                'border': '1px solid #e8e8e8'
                            }
                        )
                    ], style={'flex': '1', 'marginRight': '10px'}),
                    
                    html.Div([
                        html.Label('结束时间：', style={
                            'color': '#666',
                            'fontSize': '14px',
                            'marginBottom': '8px',
                            'display': 'block'
                        }),
                        dcc.Dropdown(
                            id='end-hour',
                            options=[{'label': f'{i}:00', 'value': i} for i in range(7, 13)],
                            value=8,
                            style={
                                'borderRadius': '8px',
                                'border': '1px solid #e8e8e8'
                            }
                        )
                    ], style={'flex': '1', 'marginRight': '10px'}),
                    
                    html.Div([
                        html.Label('操作：', style={
                            'color': '#666',
                            'fontSize': '14px',
                            'marginBottom': '8px',
                            'display': 'block',
                            'visibility': 'hidden'
                        }),
                        html.Button('查询', id='btn-time-period', n_clicks=0, style={
                            'background': 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)',
                            'color': 'white',
                            'border': 'none',
                            'padding': '12px 24px',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': '500',
                            'transition': 'all 0.3s ease',
                            'width': '100%'
                        })
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'alignItems': 'flex-end'}),
                html.Div(id='time-period-result', style={
                    'marginTop': '20px'
                })
            ], style={
                'background': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                'padding': '24px',
                'marginBottom': '20px'
            }),
            
            # 高级分析功能
            html.Div([
                html.H4('高级分析功能', style={
                    'color': '#666',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'margin': '0 0 15px 0'
                }),
                html.Div([
                    html.Button('销售预测', id='btn-sales-prediction', n_clicks=0, style={
                        'background': 'linear-gradient(135deg, #faad14 0%, #d48806 100%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '12px 20px',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'transition': 'all 0.3s ease',
                        'marginRight': '10px'
                    }),
                    html.Button('商品关联分析', id='btn-product-association', n_clicks=0, style={
                        'background': 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '12px 20px',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'transition': 'all 0.3s ease',
                        'marginRight': '10px'
                    }),
                    html.Button('客户分析', id='btn-customer-segmentation', n_clicks=0, style={
                        'background': 'linear-gradient(135deg, #eb2f96 0%, #c41d7f 100%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '12px 20px',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'transition': 'all 0.3s ease'
                    })
                ], className='button-group', style={'display': 'flex', 'marginBottom': '20px'}),
                html.Div(id='advanced-analysis-result', style={
                    'minHeight': '300px'
                })
            ], style={
                'background': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                'padding': '24px'
            })
        ], style={
            'marginBottom': '30px'
        })
    ], style={
        'padding': '0 30px 30px 30px'
    }),
    
    # 页脚
    html.Div([
        html.P('© 2026 早餐店数据分析系统 | 基于大数据技术构建', style={
            'color': '#999',
            'fontSize': '14px',
            'margin': '0'
        })
    ], style={
        'background': 'white',
        'padding': '20px 30px',
        'borderTop': '1px solid #f0f0f0',
        'textAlign': 'center'
    }),
    
    # 定时器
    dcc.Interval(
        id='interval-component',
        interval=60*1000,
        n_intervals=0
    ),
    
    # 引入Font Awesome图标
    html.Link(
        rel='stylesheet',
        href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ),
    
    # 自定义CSS
    html.Div([], style={'display': 'none'}, id='custom-css'),
    
    # 响应式CSS
    html.Div('''
        /* 基础样式 */
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .kpi-container {
                flex-direction: column !important;
                gap: 15px !important;
            }
            
            .chart-container {
                margin-bottom: 20px !important;
            }
            
            .two-column {
                flex-direction: column !important;
                gap: 20px !important;
            }
            
            .button-group {
                flex-direction: column !important;
                gap: 10px !important;
            }
            
            .button-group button {
                width: 100% !important;
                margin-right: 0 !important;
            }
            
            .header {
                padding: 15px 20px !important;
            }
            
            .header h1 {
                font-size: 20px !important;
            }
            
            .content {
                padding: 0 20px !important;
            }
            
            .card {
                padding: 20px !important;
            }
        }
        
        /* 卡片悬停效果 */
        #kpi-card-1:hover, #kpi-card-2:hover, #kpi-card-3:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            transition: all 0.3s ease;
        }
        
        /* 表格样式 */
        .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
            font-weight: 600 !important;
        }
        
        /* 下拉框样式 */
        .Select-control {
            border-radius: 8px !important;
            border: 1px solid #e8e8e8 !important;
        }
        
        .Select-menu-outer {
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        /* 按钮样式 */
        button {
            transition: all 0.3s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        /* 加载动画 */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
    ''', style={'display': 'none'})
])

@app.callback(
    [Output('total-sales', 'children'),
     Output('today-sales', 'children'),
     Output('avg-order-value', 'children'),
     Output('sales-trend-chart', 'figure'),
     Output('time-period-chart', 'figure'),
     Output('category-sales-chart', 'figure'),
     Output('top-products-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    total_sales = get_total_sales()
    today_sales = get_today_sales()
    avg_order_value = get_avg_order_value()
    
    # 创建图表
    sales_trend_fig = create_sales_trend_chart()
    time_period_fig = create_time_period_chart()
    category_sales_fig = create_category_sales_chart()
    top_products_fig = create_top_products_chart()
    
    # 美化图表
    sales_trend_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI'),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    time_period_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI'),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    category_sales_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI'),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    top_products_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI'),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return (
        f"{total_sales['total_sales']:.2f}",
        f"{today_sales['today_sales']:.2f}",
        f"{avg_order_value['avg_order_value']:.2f}",
        sales_trend_fig,
        time_period_fig,
        category_sales_fig,
        top_products_fig
    )

@app.callback(
    Output('weekly-hot-result', 'children'),
    [Input('btn-weekly-hot', 'n_clicks')]
)
def update_weekly_hot(n_clicks):
    if n_clicks > 0:
        hot_products = get_weekly_hot_products()
        
        if hot_products:
            fig = create_weekly_hot_products_chart()
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Segoe UI'),
                margin=dict(l=10, r=10, t=30, b=10)
            )
            
            return html.Div([
                html.H4('上周爆款菜品', style={
                    'color': '#333',
                    'fontSize': '16px',
                    'fontWeight': '600',
                    'margin': '0 0 15px 0'
                }),
                dash_table.DataTable(
                    data=hot_products,
                    columns=[
                        {'name': '菜品名称', 'id': 'name'},
                        {'name': '销售数量', 'id': 'total_quantity'},
                        {'name': '销售金额', 'id': 'total_amount'}
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'fontFamily': 'Segoe UI',
                        'padding': '10px',
                        'borderBottom': '1px solid #f0f0f0'
                    },
                    style_header={
                        'backgroundColor': 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
                        'color': 'white',
                        'fontWeight': '600',
                        'padding': '12px',
                        'borderBottom': '2px solid #1890ff'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ],
                    style_table={
                        'borderRadius': '8px',
                        'overflow': 'hidden',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                        'marginBottom': '20px'
                    }
                ),
                dcc.Graph(
                    figure=fig,
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        else:
            return html.Div([
                html.P('暂无数据', style={
                    'color': '#999',
                    'textAlign': 'center',
                    'padding': '40px 0'
                })
            ])
    return ""

@app.callback(
    Output('time-period-result', 'children'),
    [Input('btn-time-period', 'n_clicks')],
    [State('start-hour', 'value'),
     State('end-hour', 'value')]
)
def update_time_period_sales(n_clicks, start_hour, end_hour):
    if n_clicks > 0:
        result = get_specific_time_period_sales(start_hour, end_hour)
        
        return html.Div([
            html.H4(f"{result['period']} 销售数据", style={
                'color': '#333',
                'fontSize': '16px',
                'fontWeight': '600',
                'margin': '0 0 15px 0'
            }),
            html.Div([
                html.Div([
                    html.Span('总销售额', style={
                        'color': '#666',
                        'fontSize': '14px',
                        'display': 'block'
                    }),
                    html.Span(f"¥{result['total_sales']:.2f}", style={
                        'fontSize': '24px',
                        'fontWeight': '600',
                        'color': '#1890ff',
                        'display': 'block',
                        'marginTop': '4px'
                    })
                ], style={
                    'flex': '1',
                    'padding': '20px',
                    'background': '#f8f9fa',
                    'borderRadius': '8px',
                    'textAlign': 'center'
                }),
                html.Div([
                    html.Span('订单数量', style={
                        'color': '#666',
                        'fontSize': '14px',
                        'display': 'block'
                    }),
                    html.Span(f"{result['order_count']} 单", style={
                        'fontSize': '24px',
                        'fontWeight': '600',
                        'color': '#52c41a',
                        'display': 'block',
                        'marginTop': '4px'
                    })
                ], style={
                    'flex': '1',
                    'padding': '20px',
                    'background': '#f8f9fa',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'marginLeft': '15px'
                })
            ], style={
                'display': 'flex'
            })
        ])
    return ""

@app.callback(
    Output('advanced-analysis-result', 'children'),
    [Input('btn-sales-prediction', 'n_clicks'),
     Input('btn-product-association', 'n_clicks'),
     Input('btn-customer-segmentation', 'n_clicks')]
)
def update_advanced_analysis(sales_clicks, association_clicks, customer_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-sales-prediction' and sales_clicks > 0:
        # 获取销售预测数据
        response = requests.get('http://localhost:8000/analytics/sales-prediction')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                predictions = data['data']
                
                # 创建预测图表
                dates = [p['date'] for p in predictions]
                sales = [p['predicted_sales'] for p in predictions]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=sales,
                    mode='lines+markers',
                    name='预测销售额',
                    line=dict(color='#faad14', width=2),
                    marker=dict(color='#faad14', size=6)
                ))
                
                fig.update_layout(
                    title='未来7天销售预测',
                    xaxis_title='日期',
                    yaxis_title='销售额 (元)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Segoe UI'),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                
                return html.Div([
                    html.H4('销售预测结果', style={
                        'color': '#333',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'margin': '0 0 15px 0'
                    }),
                    dcc.Graph(
                        figure=fig,
                        config={
                            'displayModeBar': False
                        }
                    ),
                    dash_table.DataTable(
                        data=predictions,
                        columns=[
                            {'name': '日期', 'id': 'date'},
                            {'name': '预测销售额', 'id': 'predicted_sales'}
                        ],
                        style_cell={
                            'textAlign': 'left',
                            'fontFamily': 'Segoe UI',
                            'padding': '10px',
                            'borderBottom': '1px solid #f0f0f0'
                        },
                        style_header={
                            'backgroundColor': 'linear-gradient(135deg, #faad14 0%, #d48806 100%)',
                            'color': 'white',
                            'fontWeight': '600',
                            'padding': '12px',
                            'borderBottom': '2px solid #faad14'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f9f9f9'
                            }
                        ],
                        style_table={
                            'borderRadius': '8px',
                            'overflow': 'hidden',
                            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                            'marginTop': '20px'
                        }
                    )
                ])
            else:
                return html.Div([
                    html.P(f'预测失败: {data.get("message", "未知错误")}', style={
                        'color': '#ff4d4f',
                        'textAlign': 'center',
                        'padding': '40px 0'
                    })
                ])
        else:
            return html.Div([
                html.P('请求失败，请检查服务器状态', style={
                    'color': '#ff4d4f',
                    'textAlign': 'center',
                    'padding': '40px 0'
                })
            ])
    
    elif button_id == 'btn-product-association' and association_clicks > 0:
        # 获取商品关联分析数据
        response = requests.get('http://localhost:8000/analytics/product-association')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                associations = data['data']
                
                if associations:
                    return html.Div([
                        html.H4('商品关联分析结果', style={
                            'color': '#333',
                            'fontSize': '16px',
                            'fontWeight': '600',
                            'margin': '0 0 15px 0'
                        }),
                        dash_table.DataTable(
                            data=associations,
                            columns=[
                                {'name': '购买商品', 'id': 'antecedents'},
                                {'name': '推荐商品', 'id': 'consequents'},
                                {'name': '支持度', 'id': 'support'},
                                {'name': '置信度', 'id': 'confidence'},
                                {'name': '提升度', 'id': 'lift'}
                            ],
                            style_cell={
                                'textAlign': 'left',
                                'fontFamily': 'Segoe UI',
                                'padding': '10px',
                                'borderBottom': '1px solid #f0f0f0'
                            },
                            style_header={
                                'backgroundColor': 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)',
                                'color': 'white',
                                'fontWeight': '600',
                                'padding': '12px',
                                'borderBottom': '2px solid #722ed1'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f9f9f9'
                                }
                            ],
                            style_table={
                                'borderRadius': '8px',
                                'overflow': 'hidden',
                                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'
                            }
                        )
                    ])
                else:
                    return html.Div([
                        html.P('暂无关联数据', style={
                            'color': '#999',
                            'textAlign': 'center',
                            'padding': '40px 0'
                        })
                    ])
            else:
                return html.Div([
                    html.P(f'分析失败: {data.get("message", "未知错误")}', style={
                        'color': '#ff4d4f',
                        'textAlign': 'center',
                        'padding': '40px 0'
                    })
                ])
        else:
            return html.Div([
                html.P('请求失败，请检查服务器状态', style={
                    'color': '#ff4d4f',
                    'textAlign': 'center',
                    'padding': '40px 0'
                })
            ])
    
    elif button_id == 'btn-customer-segmentation' and customer_clicks > 0:
        # 获取客户分析数据
        response = requests.get('http://localhost:8000/analytics/customer-segmentation')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                segment_counts = data['segment_counts']
                
                # 创建客户分布图表
                segments = [s['segment'] for s in segment_counts]
                counts = [s['count'] for s in segment_counts]
                
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=segments,
                    values=counts,
                    hole=0.3,
                    marker_colors=['#eb2f96', '#faad14', '#52c41a']
                ))
                
                fig.update_layout(
                    title='客户分布',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Segoe UI'),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                
                return html.Div([
                    html.H4('客户分析结果', style={
                        'color': '#333',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'margin': '0 0 15px 0'
                    }),
                    dcc.Graph(
                        figure=fig,
                        config={
                            'displayModeBar': False
                        }
                    )
                ])
            else:
                return html.Div([
                    html.P(f'分析失败: {data.get("message", "未知错误")}', style={
                        'color': '#ff4d4f',
                        'textAlign': 'center',
                        'padding': '40px 0'
                    })
                ])
        else:
            return html.Div([
                html.P('请求失败，请检查服务器状态', style={
                    'color': '#ff4d4f',
                    'textAlign': 'center',
                    'padding': '40px 0'
                })
            ])
    
    return ""

if __name__ == '__main__':
    app.run(debug=True, port=8050)
