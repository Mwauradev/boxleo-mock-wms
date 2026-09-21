import sqlite3
import random
import os
from datetime import datetime

random.seed(7)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boxleo_mock_wms.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    sku_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (sku_id) REFERENCES inventory(sku_id)
);
""")

# Pull each order with its merchant, so we only assign SKUs that belong to that merchant
orders = cur.execute("SELECT order_id, merchant_id FROM orders").fetchall()
inventory = cur.execute("SELECT sku_id, merchant_id FROM inventory").fetchall()

merchant_skus = {}
for sku_id, merchant_id in inventory:
    merchant_skus.setdefault(merchant_id, []).append(sku_id)

order_items = []
item_id = 1
for order_id, merchant_id in orders:
    available_skus = merchant_skus.get(merchant_id, [])
    if not available_skus:
        continue
    n_lines = random.choice([1, 1, 1, 2, 2, 3])  # most orders are 1 SKU, some multi-item
    chosen_skus = random.sample(available_skus, min(n_lines, len(available_skus)))
    for sku_id in chosen_skus:
        qty = random.randint(1, 5)
        order_items.append((item_id, order_id, sku_id, qty))
        item_id += 1

cur.executemany("INSERT INTO order_items VALUES (?,?,?,?)", order_items)
conn.commit()

print("order_items rows:", len(order_items))
print("Sample:", order_items[:5])
conn.close()
