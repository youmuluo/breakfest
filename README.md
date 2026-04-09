# 基于大数据的中式早餐店订单数据分析及可视化系统

## 项目简介

本项目是一个基于Python的中式早餐店订单数据分析及可视化系统，旨在为餐饮零售业的精细化运营提供数据驱动的决策支持。系统采用前后端分离架构，后端基于FastAPI框架开发，前端使用ECharts实现数据可视化，通过Pandas进行数据处理和分析，实现了从数据采集、处理、分析到可视化展示的全链路解决方案。

## 功能特点

### 1. 数据管理功能
- **数据导入**：支持CSV和Excel格式的数据导入，包含数据验证功能
- **数据导出**：支持将分析结果导出为CSV、Excel和PDF格式
- **数据清洗**：自动处理缺失值、异常值，进行数据类型转换

### 2. 数据分析功能
- **销售趋势分析**：分析每日、每周的销售趋势
- **时段销售分析**：分析不同时段的销售分布，识别高峰时段
- **商品销售分析**：热销商品排行、商品关联性分析
- **客户行为分析**：客单价分析、客户分群
- **销售预测**：基于历史数据的销售预测功能

### 3. 数据可视化功能
- **仪表盘展示**：直观展示关键业务指标（KPI）
- **交互式图表**：支持折线图、柱状图、饼图等多种图表类型
- **实时数据更新**：数据自动刷新，实时展示最新分析结果

### 4. 系统管理功能
- **用户认证**：基于JWT的用户认证系统
- **权限管理**：支持管理员和普通用户角色
- **系统监控**：实时监控系统运行状态

## 技术栈

### 后端技术
- **FastAPI**：现代高性能Web框架，支持异步处理
- **SQLAlchemy**：ORM框架，简化数据库操作
- **Pandas**：数据处理和分析核心库
- **NumPy**：数值计算基础库
- **scikit-learn**：机器学习库，用于数据分析和预测

### 前端技术
- **HTML5/CSS3/JavaScript**：前端基础技术
- **ECharts**：数据可视化图表库
- **响应式设计**：支持多设备访问

### 数据库
- **MySQL**：关系型数据库，存储业务数据

### 其他工具
- **PyJWT**：JWT令牌生成和验证
- **FPDF**：PDF文档生成
- **openpyxl**：Excel文件处理
- **psutil**：系统监控

## 项目结构

```
breakfast/
├── main.py                 # 主程序入口，FastAPI应用
├── database.py             # 数据库操作模块
├── analytics.py            # 数据分析模块
├── auth.py                 # 用户认证模块
├── cache.py                # 缓存模块
├── data_import.py          # 数据导入模块
├── pdf_export.py           # PDF导出模块
├── monitoring.py           # 系统监控模块
├── chart_generator.py      # 图表生成模块
├── dash_app.py             # Dash应用（可选）
├── seed_data.py            # 数据库初始化脚本
├── requirements.txt        # 项目依赖列表
├── .gitignore             # Git忽略文件配置
└── README.md              # 项目说明文档
```

## 核心模块说明

### 1. main.py - 主程序入口
- **功能**：定义所有API接口，处理HTTP请求
- **关键接口**：
  - `/dashboard` - 数据仪表盘页面
  - `/total-sales` - 总销售额查询
  - `/sales-trend` - 销售趋势分析
  - `/top-products` - 热销商品排行
  - `/analytics/sales-prediction` - 销售预测

### 2. database.py - 数据库操作模块
- **功能**：封装所有数据库操作，提供数据查询和处理接口
- **核心函数**：
  - `get_sales_trend()` - 获取销售趋势数据
  - `get_top_products()` - 获取热销商品数据
  - `clean_and_process_data()` - 数据清洗和处理
  - `export_sales_report_to_excel()` - 导出销售报告

### 3. analytics.py - 数据分析模块
- **功能**：实现数据分析和机器学习算法
- **核心功能**：
  - `sales_prediction()` - 销售预测（使用时间序列分析）
  - `product_association_analysis()` - 商品关联分析
  - `customer_segmentation()` - 客户分群分析

### 4. auth.py - 用户认证模块
- **功能**：实现用户认证和权限管理
- **技术实现**：基于JWT的认证机制
- **功能特点**：
  - 用户注册和登录
  - 角色权限控制
  - Token验证

### 5. cache.py - 缓存模块
- **功能**：提供数据缓存机制，提高系统性能
- **实现方式**：基于内存的缓存装饰器
- **缓存策略**：支持TTL（Time To Live）设置

## 数据库设计

### 主要数据表

#### 1. products（商品表）
- 存储商品基本信息，包括名称、分类、价格等

#### 2. orders（订单表）
- 存储订单信息，包括订单号、订单时间、总金额等

#### 3. order_items（订单明细表）
- 存储订单明细，关联商品和订单

#### 4. users（用户表）
- 存储系统用户信息，包括用户名、密码、角色等

## 安装和运行

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone [项目地址]
cd breakfast

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置数据库
# 修改database.py中的DATABASE_URL为您的数据库连接信息

# 6. 初始化数据库
python seed_data.py

# 7. 运行项目
uvicorn main:app --reload
```

### 3. 访问系统
- 系统主页：http://localhost:8000
- API文档：http://localhost:8000/docs
- 数据仪表盘：http://localhost:8000/dashboard

## API接口说明

### 数据查询接口
- `GET /products` - 获取所有商品信息
- `GET /total-sales` - 获取总销售额
- `GET /today-sales` - 获取今日销售额
- `GET /sales-trend` - 获取销售趋势
- `GET /top-products` - 获取热销商品排行
- `GET /category-sales` - 获取分类销售数据

### 数据导入导出接口
- `POST /import/csv` - 导入CSV文件
- `POST /import/excel` - 导入Excel文件
- `GET /export/csv` - 导出CSV文件
- `GET /export/excel` - 导出Excel文件
- `GET /export/pdf/sales-report` - 导出PDF销售报告

### 数据分析接口
- `GET /analytics/sales-prediction` - 销售预测
- `GET /analytics/product-association` - 商品关联分析
- `GET /analytics/customer-segmentation` - 客户分群分析

### 用户认证接口
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册（需要管理员权限）
- `GET /auth/me` - 获取当前用户信息

## 系统特点

### 1. 技术先进性
- 采用FastAPI现代Web框架，性能优异
- 使用异步处理，提高并发能力
- 基于Pandas的高效数据处理

### 2. 代码质量
- 完善的类型注解，提高代码可读性
- 详细的文档字符串，便于理解和维护
- 模块化设计，职责清晰

### 3. 功能完整性
- 覆盖数据采集、处理、分析、可视化全流程
- 支持多种数据格式导入导出
- 提供完整的用户认证和权限管理

### 4. 易用性
- 提供交互式API文档
- 直观的数据可视化界面
- 简单的安装和部署流程

## 应用价值

### 1. 经营决策支持
- 通过销售趋势分析，帮助商家制定合理的进货计划
- 通过时段销售分析，优化人员排班
- 通过商品关联分析，设计促销套餐

### 2. 成本控制
- 基于销售预测，减少库存积压
- 识别滞销商品，优化商品结构
- 分析客户消费行为，提高营销效率

### 3. 效率提升
- 自动化数据处理，减少人工统计工作
- 实时数据监控，及时发现问题
- 多维度分析，全面了解经营状况

## 未来展望

### 1. 功能扩展
- 集成外卖平台API，实现多渠道数据整合
- 添加会员管理系统，实现精准营销
- 开发移动端应用，支持随时随地查看数据

### 2. 技术升级
- 引入Spark大数据处理框架，支持更大规模数据分析
- 使用机器学习算法，提高预测准确性
- 优化前端界面，提升用户体验

### 3. 商业化应用
- 开发SaaS版本，服务更多中小餐饮企业
- 提供定制化服务，满足不同客户需求
- 建立数据分析生态，提供增值服务

## 联系方式

如有任何问题或建议，请联系：
- 项目作者：[您的姓名]
- 指导教师：[导师姓名]
- 电子邮箱：[您的邮箱]

---

**本项目为毕业设计作品，仅供学习和研究使用。**
