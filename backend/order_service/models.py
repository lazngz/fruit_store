import sqlite3

# Initialize database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL
    )''')
    conn.commit()
    conn.close()

# Add a new order
def add_order(product_id, quantity, total_price):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (product_id, quantity, total_price) VALUES (?, ?, ?)',
                   (product_id, quantity, total_price))
    conn.commit()
    conn.close()

# Fetch all orders
def fetch_orders():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    conn.close()
    return orders
