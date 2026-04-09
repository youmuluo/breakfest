from fpdf import FPDF
import pandas as pd
from database import clean_and_process_data
from datetime import date

class PDF(FPDF):
    def header(self):
        """PDF头部"""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '早餐店销售分析报告', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'生成日期: {date.today().isoformat()}', 0, 1, 'R')
        self.ln(10)
    
    def footer(self):
        """PDF页脚"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')
    
    def chapter_title(self, title):
        """章节标题"""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        """章节内容"""
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()
    
    def table(self, data, headers):
        """表格"""
        # 设置表格宽度
        col_width = self.w / (len(headers) + 1)
        
        # 表头
        self.set_font('Arial', 'B', 10)
        for header in headers:
            self.cell(col_width, 10, header, 1, 0, 'C')
        self.ln()
        
        # 数据行
        self.set_font('Arial', '', 9)
        for row in data:
            for item in row:
                self.cell(col_width, 10, str(item), 1, 0, 'C')
            self.ln()

def export_sales_report_to_pdf(filename='sales_report.pdf'):
    """导出销售报告为PDF"""
    try:
        # 获取数据
        df = clean_and_process_data()
        
        # 计算统计数据
        total_sales = df['total_amount'].sum()
        order_count = df['order_no'].nunique()
        avg_order_value = total_sales / order_count if order_count > 0 else 0
        
        # 按日期分组
        daily_sales = df.groupby('date').agg({
            'total_amount': 'sum',
            'order_no': 'nunique'
        }).reset_index()
        daily_sales.columns = ['日期', '销售额', '订单数']
        
        # 按商品分组
        product_sales = df.groupby('name').agg({
            'quantity': 'sum',
            'item_amount': 'sum'
        }).reset_index()
        product_sales.columns = ['商品名称', '销售数量', '销售金额']
        product_sales = product_sales.sort_values('销售数量', ascending=False).head(10)
        
        # 按类别分组
        category_sales = df.groupby('category').agg({
            'item_amount': 'sum'
        }).reset_index()
        category_sales.columns = ['类别', '销售金额']
        category_sales = category_sales.sort_values('销售金额', ascending=False)
        
        # 创建PDF
        pdf = PDF()
        pdf.add_page()
        
        # 摘要部分
        pdf.chapter_title('一、销售摘要')
        summary = f"""
总销售额: ¥{total_sales:.2f}
订单数量: {order_count} 单
客单价: ¥{avg_order_value:.2f}
数据时间范围: {df['date'].min()} 至 {df['date'].max()}
"""
        pdf.chapter_body(summary)
        
        # 每日销售数据
        pdf.chapter_title('二、每日销售数据')
        daily_data = daily_sales.values.tolist()
        pdf.table(daily_data, ['日期', '销售额', '订单数'])
        
        # 商品销售排行
        pdf.chapter_title('三、商品销售排行')
        product_data = product_sales.values.tolist()
        pdf.table(product_data, ['商品名称', '销售数量', '销售金额'])
        
        # 类别销售分布
        pdf.chapter_title('四、类别销售分布')
        category_data = category_sales.values.tolist()
        pdf.table(category_data, ['类别', '销售金额'])
        
        # 保存PDF
        pdf.output(filename)
        return filename
    except Exception as e:
        raise Exception(f'导出PDF失败: {str(e)}')

def export_weekly_report_to_pdf(filename='weekly_report.pdf'):
    """导出周报告为PDF"""
    try:
        # 获取数据
        df = clean_and_process_data()
        
        # 计算上周数据
        from datetime import timedelta
        last_week_start = date.today() - timedelta(days=14)
        last_week_end = date.today() - timedelta(days=7)
        last_week_data = df[(df['date'] >= last_week_start) & (df['date'] < last_week_end)]
        
        # 计算统计数据
        total_sales = last_week_data['total_amount'].sum()
        order_count = last_week_data['order_no'].nunique()
        avg_order_value = total_sales / order_count if order_count > 0 else 0
        
        # 按日期分组
        daily_sales = last_week_data.groupby('date').agg({
            'total_amount': 'sum',
            'order_no': 'nunique'
        }).reset_index()
        daily_sales.columns = ['日期', '销售额', '订单数']
        
        # 按商品分组
        product_sales = last_week_data.groupby('name').agg({
            'quantity': 'sum',
            'item_amount': 'sum'
        }).reset_index()
        product_sales.columns = ['商品名称', '销售数量', '销售金额']
        product_sales = product_sales.sort_values('销售数量', ascending=False).head(10)
        
        # 创建PDF
        pdf = PDF()
        pdf.add_page()
        
        # 摘要部分
        pdf.chapter_title('一、周销售摘要')
        summary = f"""
周销售总额: ¥{total_sales:.2f}
订单数量: {order_count} 单
客单价: ¥{avg_order_value:.2f}
统计周期: {last_week_start} 至 {last_week_end}
"""
        pdf.chapter_body(summary)
        
        # 每日销售数据
        pdf.chapter_title('二、每日销售数据')
        daily_data = daily_sales.values.tolist()
        pdf.table(daily_data, ['日期', '销售额', '订单数'])
        
        # 爆款商品
        pdf.chapter_title('三、爆款商品')
        product_data = product_sales.values.tolist()
        pdf.table(product_data, ['商品名称', '销售数量', '销售金额'])
        
        # 保存PDF
        pdf.output(filename)
        return filename
    except Exception as e:
        raise Exception(f'导出PDF失败: {str(e)}')
