# database.py
import sqlite3
import datetime

DB_PATH = "shop.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # 用户表：增加 deposit_address 与 language 字段
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            deposit_address TEXT UNIQUE,
            language TEXT DEFAULT 'EN'
        )
    ''')
    # 商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            category TEXT,
            content TEXT
        )
    ''')
    # 订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            order_time TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    # 已处理交易表（用于去重）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_txs (
            txid TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["balance"] if row else 0

def update_user_balance(user_id, new_balance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

def add_product(code, category, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (code, category, content) VALUES (?, ?, ?)', (code, category, content))
    conn.commit()
    conn.close()

def get_products_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_product_by_code_prefix(prefix):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE code LIKE ?', (f'{prefix}%',))
    row = cursor.fetchone()
    conn.close()
    return row

def create_order(user_id, product_id):
    conn = get_connection()
    cursor = conn.cursor()
    order_time = datetime.datetime.now().isoformat()
    cursor.execute('INSERT INTO orders (user_id, product_id, order_time, status) VALUES (?, ?, ?, ?)',
                   (user_id, product_id, order_time, "完成"))
    conn.commit()
    conn.close()

def is_tx_processed(txid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_txs WHERE txid = ?', (txid,))
    row = cursor.fetchone()
    conn.close()
    return bool(row)

def add_processed_tx(txid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO processed_txs (txid) VALUES (?)', (txid,))
    conn.commit()
    conn.close()

# 以下函数用于处理用户充值地址的分配与查询
def get_user_deposit_address(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT deposit_address FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["deposit_address"] if row and row["deposit_address"] else None

def assign_deposit_address_to_user(user_id, deposit_address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET deposit_address = ? WHERE user_id = ?", (deposit_address, user_id))
    conn.commit()
    conn.close()

def get_all_assigned_deposit_addresses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT deposit_address FROM users WHERE deposit_address IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return [row["deposit_address"] for row in rows if row["deposit_address"]]

def get_user_by_deposit_address(deposit_address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE deposit_address = ?", (deposit_address,))
    row = cursor.fetchone()
    conn.close()
    return row

# 获取和设置用户语言
def get_user_language(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["language"] if row and row["language"] else "EN"

def set_user_language(user_id, lang):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

# 获取指定用户的订单记录（按时间倒序）
def get_orders(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY order_time DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
