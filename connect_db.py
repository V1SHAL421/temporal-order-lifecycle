import sqlite3
con = sqlite3.connect("./data/order_lifecycle.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, state TEXT, address_json TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)")
cur.execute("CREATE TABLE IF NOT EXISTS payments (payment_id TEXT PRIMARY KEY, order_id TEXT, status TEXT, amount INTEGER, created_at TIMESTAMP, updated_at TIMESTAMP)")
cur.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, order_id TEXT, type TEXT, payload_json TEXT, ts TIMESTAMP)")