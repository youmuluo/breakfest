from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import os

# 数据库相关导入
from database import (
    test_connection,
    get_all_products,
    get_total_sales,
    get_top_products,
    get_sales_trend,
    get_time_period_sales,
    get_today_sales,
    get_avg_order_value,
    get_category_sales,
    get_sales_trend_7d,
    get_weekly_hot_products,
    get_specific_time_period_sales,
    export_data_to_csv,
    export_data_to_excel,
    export_sales_report_to_excel,
    export_weekly_report_to_excel
)

# 数据导入相关导入
from data_import import import_csv_file, import_excel_file, validate_data

# 分析相关导入
from analytics import (
    sales_prediction,
    product_association_analysis,
    customer_segmentation,
    sales_forecast_by_category
)

# 认证相关导入
from auth import get_user_manager

# PDF导出相关导入
from pdf_export import export_sales_report_to_pdf, export_weekly_report_to_pdf

# 监控相关导入
from monitoring import get_monitor

app = FastAPI(
    title="早餐店数据分析系统",
    description="用于早餐店销售数据的分析、预测和管理",
    version="1.0.0"
)

@app.get("/")
def root() -> dict:
    """根路径"""
    return {"message": "FastAPI working"}

@app.get("/test-db")
def test_db() -> dict:
    """测试数据库连接"""
    return {"result": str(test_connection())}

@app.get("/products")
def products() -> list:
    """获取所有商品信息"""
    return get_all_products()

@app.get("/total-sales")
def total_sales() -> dict:
    """获取总销售额"""
    return get_total_sales()

@app.get("/top-products")
def top_products() -> list:
    """获取热销商品排行"""
    return get_top_products()

@app.get("/sales-trend")
def sales_trend() -> list:
    """获取销售趋势"""
    return get_sales_trend()

@app.get("/time-period-sales")
def time_period_sales() -> list:
    """获取时段销售分布"""
    return get_time_period_sales()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    """数据仪表盘"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>早餐店数据分析系统</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f7fa; }
            h1 { text-align: center; }
            .kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
            .kpi { flex: 1; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); text-align: center; }
            .kpi h2 { margin: 0; font-size: 18px; color: #666; }
            .kpi p { font-size: 28px; margin: 10px 0 0 0; color: #1890ff; }
            .chart { background: white; padding: 20px; margin-bottom: 30px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
            .card { background: white; padding: 20px; margin-bottom: 30px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>

        <h1>早餐店数据分析系统</h1>

        <div class="kpi-container">
            <div class="kpi">
                <h2>总销售额</h2>
                <p id="totalSales">加载中...</p>
            </div>
            <div class="kpi">
                <h2>今日销售额</h2>
                <p id="todaySales">加载中...</p>
            </div>
            <div class="kpi">
                <h2>客单价</h2>
                <p id="avgOrderValue">加载中...</p>
            </div>
        </div>

        <div class="chart">
            <h2>销售趋势</h2>
            <div id="trend" style="width: 100%; height: 400px;"></div>
        </div>
        <div class="chart">
            <h2>时段销售分布</h2>
            <div id="timePeriod" style="width: 100%; height: 400px;"></div>
        </div>

        <div class="chart">
            <h2>热销商品排行</h2>
            <div id="top" style="width: 100%; height: 400px;"></div>
        </div>
        <div class="card">
            <h3>销售结构占比</h3>
            <div id="categoryPie" style="height: 350px;"></div>
        </div>

        <script>
            // 获取总销售额
            fetch('/total-sales')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('totalSales').innerText = data.total_sales + " 元";
                });

            // 获取今日销售额
            fetch('/today-sales')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('todaySales').innerText = data.today_sales + " 元";
                });

            // 获取销售趋势
            fetch('/sales-trend')
                .then(res => res.json())
                .then(data => {
                    const chart = echarts.init(document.getElementById('trend'));
                    chart.setOption({
                        tooltip: {},
                        xAxis: { type: 'category', data: data.map(i => i.date) },
                        yAxis: { type: 'value' },
                        series: [{ data: data.map(i => i.total), type: 'line', smooth: true }]
                    });
                });

            // 获取热销商品
            fetch('/top-products')
                .then(res => res.json())
                .then(data => {
                    const chart = echarts.init(document.getElementById('top'));
                    chart.setOption({
                        tooltip: {},
                        xAxis: { type: 'category', data: data.map(i => i.name) },
                        yAxis: { type: 'value' },
                        series: [{ data: data.map(i => i.total_quantity), type: 'bar' }]
                    });
                });

            // 获取客单价
            fetch('/avg-order-value')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('avgOrderValue').innerText = data.avg_order_value + " 元";
                });

            // 获取销售结构占比
            fetch('/category-sales')
                .then(res => res.json())
                .then(data => {
                    const chart = echarts.init(document.getElementById('categoryPie'));
                    chart.setOption({
                        tooltip: { trigger: 'item' },
                        series: [{
                            type: 'pie',
                            radius: '60%',
                            data: data.map(item => ({
                                name: item.category,
                                value: item.total_sales
                            }))
                        }]
                    });
                });
        </script>

    </body>
    </html>
    """

@app.get("/today-sales")
def today_sales() -> dict:
    """获取今日销售额"""
    return get_today_sales()

@app.get("/avg-order-value")
def avg_order_value() -> dict:
    """获取客单价"""
    return get_avg_order_value()

@app.get("/category-sales")
def category_sales() -> list:
    """获取分类销售数据"""
    return get_category_sales()

@app.get("/sales-trend-7d")
def sales_trend_7d() -> list:
    """获取近7天销售趋势"""
    return get_sales_trend_7d()

@app.get("/weekly-hot-products")
def weekly_hot_products() -> list:
    """获取上周爆款菜品"""
    return get_weekly_hot_products()

@app.get("/time-period-sales/{start_hour}/{end_hour}")
def time_period_sales_by_hours(start_hour: int, end_hour: int) -> dict:
    """获取特定时间段销售数据"""
    return get_specific_time_period_sales(start_hour, end_hour)

@app.get("/export/csv")
def export_csv() -> FileResponse:
    """导出数据为CSV文件"""
    filename = export_data_to_csv()
    return FileResponse(filename, filename=filename, media_type='text/csv')

@app.get("/export/excel")
def export_excel() -> FileResponse:
    """导出数据为Excel文件"""
    filename = export_data_to_excel()
    return FileResponse(filename, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/export/sales-report")
def export_sales_report() -> FileResponse:
    """导出销售报告为Excel文件"""
    filename = export_sales_report_to_excel()
    return FileResponse(filename, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/export/weekly-report")
def export_weekly_report() -> FileResponse:
    """导出周报告为Excel文件"""
    filename = export_weekly_report_to_excel()
    return FileResponse(filename, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.post("/import/csv")
async def import_csv(file: UploadFile = File(...)) -> dict:
    """导入CSV文件数据"""
    # 保存临时文件
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # 验证文件
        validation = validate_data(temp_path, 'csv')
        if not validation['valid']:
            return {"success": False, "message": validation['message']}
        
        # 导入数据
        result = import_csv_file(temp_path)
        return result
    finally:
        # 确保临时文件被删除
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/import/excel")
async def import_excel(file: UploadFile = File(...)) -> dict:
    """导入Excel文件数据"""
    # 保存临时文件
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # 验证文件
        validation = validate_data(temp_path, 'excel')
        if not validation['valid']:
            return {"success": False, "message": validation['message']}
        
        # 导入数据
        result = import_excel_file(temp_path)
        return result
    finally:
        # 确保临时文件被删除
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/validate/csv")
async def validate_csv(file: UploadFile = File(...)) -> dict:
    """验证CSV文件数据"""
    # 保存临时文件
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # 验证文件
        result = validate_data(temp_path, 'csv')
        return result
    finally:
        # 确保临时文件被删除
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/validate/excel")
async def validate_excel(file: UploadFile = File(...)) -> dict:
    """验证Excel文件数据"""
    # 保存临时文件
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # 验证文件
        result = validate_data(temp_path, 'excel')
        return result
    finally:
        # 确保临时文件被删除
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/analytics/sales-prediction")
def predict_sales(days: int = 7) -> dict:
    """预测未来销售额"""
    return sales_prediction(days)

@app.get("/analytics/product-association")
def product_association() -> dict:
    """商品关联分析"""
    return product_association_analysis()

@app.get("/analytics/customer-segmentation")
def segment_customers() -> dict:
    """客户消费行为分析"""
    return customer_segmentation()

@app.get("/analytics/category-forecast")
def category_forecast() -> dict:
    """按商品类别预测销售额"""
    return sales_forecast_by_category()

# 用户认证相关接口

# 依赖项：获取当前用户
def get_current_user(authorization: str = Header(None)) -> dict:
    """获取当前用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    
    token = authorization.split(" ")[1] if " " in authorization else authorization
    user_manager = get_user_manager()
    result = user_manager.verify_token(token)
    
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['message'])
    
    return result['user']

# 依赖项：验证管理员权限
def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """验证管理员权限"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user

@app.post("/auth/login")
def login(username: str, password: str) -> dict:
    """用户登录"""
    user_manager = get_user_manager()
    return user_manager.authenticate_user(username, password)

@app.post("/auth/register")
def register(username: str, password: str, role: str = 'user', current_user: dict = Depends(get_admin_user)) -> dict:
    """用户注册（需要管理员权限）"""
    user_manager = get_user_manager()
    return user_manager.create_user(username, password, role)

@app.get("/auth/users")
def get_users(current_user: dict = Depends(get_admin_user)) -> list:
    """获取用户列表（需要管理员权限）"""
    user_manager = get_user_manager()
    return user_manager.get_all_users()

@app.put("/auth/users/{user_id}/role")
def update_user_role(user_id: int, role: str, current_user: dict = Depends(get_admin_user)) -> dict:
    """更新用户角色（需要管理员权限）"""
    user_manager = get_user_manager()
    return user_manager.update_user_role(user_id, role)

@app.delete("/auth/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(get_admin_user)) -> dict:
    """删除用户（需要管理员权限）"""
    user_manager = get_user_manager()
    return user_manager.delete_user(user_id)

@app.get("/auth/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前用户信息"""
    return current_user

# PDF导出接口

@app.get("/export/pdf/sales-report")
def export_pdf_sales_report() -> FileResponse:
    """导出销售报告为PDF"""
    try:
        filename = export_sales_report_to_pdf()
        return FileResponse(filename, media_type='application/pdf', filename='sales_report.pdf')
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/export/pdf/weekly-report")
def export_pdf_weekly_report() -> FileResponse:
    """导出周报告为PDF"""
    try:
        filename = export_weekly_report_to_pdf()
        return FileResponse(filename, media_type='application/pdf', filename='weekly_report.pdf')
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# 系统监控接口

@app.get("/monitoring/metrics")
def get_monitoring_metrics() -> dict:
    """获取系统监控指标"""
    monitor = get_monitor()
    return monitor.get_metrics()

@app.get("/monitoring/status")
def get_monitoring_status() -> dict:
    """获取系统状态摘要"""
    monitor = get_monitor()
    return monitor.get_status_summary()

@app.post("/monitoring/clear-alerts")
def clear_monitoring_alerts() -> dict:
    """清空预警信息"""
    monitor = get_monitor()
    monitor.clear_alerts()
    return {"message": "预警信息已清空"}