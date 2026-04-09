from sqlalchemy import text
from database import engine

def create_tables():
    """创建所有数据库表"""
    with engine.begin() as conn:
        # 创建商品表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category (category)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        # 创建订单表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_no VARCHAR(50) UNIQUE NOT NULL,
                order_time DATETIME NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                channel VARCHAR(20) DEFAULT '堂食',
                customer_id VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_order_time (order_time),
                INDEX idx_channel (channel)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        # 创建订单明细表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id),
                INDEX idx_order_id (order_id),
                INDEX idx_product_id (product_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        
        print("✅ 所有表创建成功！")

def insert_sample_products():
    """插入示例商品数据"""
    products = [
        # 包子类
        ('猪肉包子', '包子', 2.50, '新鲜猪肉馅包子'),
        ('牛肉包子', '包子', 3.50, '精选牛肉馅包子'),
        ('青菜包子', '包子', 1.50, '新鲜青菜包子'),
        ('豆沙包子', '包子', 1.80, '香甜豆沙包子'),
        ('鲜肉大包', '包子', 3.00, '超大鲜肉包子'),
        
        # 粥类
        ('小米粥', '粥', 2.00, '营养小米粥'),
        ('南瓜粥', '粥', 2.50, '香甜南瓜粥'),
        ('皮蛋瘦肉粥', '粥', 4.00, '经典皮蛋瘦肉粥'),
        ('八宝粥', '粥', 3.00, '营养八宝粥'),
        ('白粥', '粥', 1.50, '清淡白粥'),
        
        # 豆浆油条类
        ('豆浆', '饮品', 2.00, '现磨豆浆'),
        ('甜豆浆', '饮品', 2.50, '加糖豆浆'),
        ('油条', '主食', 2.00, '香脆油条'),
        ('茶叶蛋', '主食', 1.50, '五香茶叶蛋'),
        
        # 饼类
        ('葱油饼', '饼', 3.00, '香酥葱油饼'),
        ('手抓饼', '饼', 4.00, '美味手抓饼'),
        ('煎饼果子', '饼', 5.00, '特色煎饼果子'),
        
        # 其他
        ('豆腐脑', '其他', 3.00, '嫩滑豆腐脑'),
        ('小笼包', '包子', 6.00, '一笼6个小笼包'),
        ('蒸饺', '其他', 5.00, '美味蒸饺'),
    ]
    
    with engine.begin() as conn:
        # 先检查是否已有数据
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        if result.scalar() > 0:
            print("⚠️  products表已有数据，跳过插入")
            return
        
        # 插入商品数据
        for name, category, price, description in products:
            conn.execute(
                text("INSERT INTO products (name, category, price, description) VALUES (:name, :category, :price, :description)"),
                {'name': name, 'category': category, 'price': price, 'description': description}
            )
        
        print(f"✅ 成功插入 {len(products)} 个商品！")

def main():
    print("开始初始化数据库...")
    print("=" * 50)
    
    try:
        create_tables()
        print()
        insert_sample_products()
        print()
        print("=" * 50)
        print("🎉 数据库初始化完成！")
        print("提示：现在可以运行 python seed_data.py 来生成订单数据")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

if __name__ == "__main__":
    main()
