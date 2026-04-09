import random
from datetime import datetime, timedelta
from sqlalchemy import text
from database import engine

DAYS = 14
TOTAL_ORDERS = 1000

CHANNELS = ['堂食', '外卖']
CHANNEL_WEIGHTS = [0.6, 0.4]

CUSTOMER_IDS = [f'CUST{str(i).zfill(4)}' for i in range(1, 201)]

def generate_order_time():
    today = datetime.now()
    day_offset = random.randint(0, DAYS - 1)
    base_day = today - timedelta(days=day_offset)

    r = random.random()
    if r < 0.7:
        hour = random.randint(6, 9)
    elif r < 0.9:
        hour = random.randint(9, 12)
    else:
        hour = random.randint(12, 20)

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return base_day.replace(hour=hour, minute=minute, second=second, microsecond=0)

def generate_channel():
    return random.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0]

def generate_customer_id():
    if random.random() < 0.7:
        return random.choice(CUSTOMER_IDS)
    return None

def main():
    with engine.begin() as conn:

        products = conn.execute(
            text("SELECT id, price FROM products")
        ).fetchall()

        if not products:
            print("请先确保 products 表有数据")
            return

        for i in range(TOTAL_ORDERS):

            order_time = generate_order_time()
            channel = generate_channel()
            customer_id = generate_customer_id()

            item_count = random.randint(1, 4)
            selected = random.sample(products, min(item_count, len(products)))

            total_amount = 0
            order_items = []

            for p in selected:
                quantity = random.randint(1, 3)
                amount = float(p.price) * quantity
                total_amount += amount

                order_items.append((p.id, quantity, round(amount, 2)))

            result = conn.execute(
                text("""
                    INSERT INTO orders (order_no, order_time, total_amount, channel, customer_id)
                    VALUES (:order_no, :order_time, :total_amount, :channel, :customer_id)
                """),
                {
                    "order_no": f"ORD{order_time.strftime('%Y%m%d%H%M%S')}{i}",
                    "order_time": order_time,
                    "total_amount": round(total_amount, 2),
                    "channel": channel,
                    "customer_id": customer_id
                }
            )

            order_id = result.lastrowid

            for item in order_items:
                conn.execute(
                    text("""
                        INSERT INTO order_items (order_id, product_id, quantity, amount)
                        VALUES (:order_id, :product_id, :quantity, :amount)
                    """),
                    {
                        "order_id": order_id,
                        "product_id": item[0],
                        "quantity": item[1],
                        "amount": item[2]
                    }
                )

    print(f"成功生成 {TOTAL_ORDERS} 条订单数据")
    print(f"包含channel字段（堂食60%/外卖40%）")
    print(f"包含customer_id字段（200个模拟客户，70%订单有客户ID）")

if __name__ == "__main__":
    main()
