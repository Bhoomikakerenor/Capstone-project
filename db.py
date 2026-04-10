import psycopg2
import psycopg2.pool
import redis
import json
import pandas as pd

# ── Connection Pooling (reuse connections instead of creating new ones) ──
_pg_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=10,
    host="localhost",
    database="mydatabase",
    user="myuser",
    password="mysecretpassword",
    port=5432
)

_redis_client = redis.Redis(host = "127.0.0.1", port = 6379, db = 0, decode_responses = True)

TABLE = '"Dataset_for_NGD"'
CACHE_TTL = 600
HIT_THRESHOLD = 3

def get_pg_conn():
    return _pg_pool.getconn()

def release_pg_conn(conn):
    _pg_pool.putconn(conn)

def get_redis():
    return _redis_client

# ── Single product lookup with caching ──
def get_product(product_id):
    r = get_redis()
    cache_key = f"product:{product_id}"

    cached = r.get(cache_key)
    if cached:
        r.zincrby("product:hits", 1, cache_key)
        return json.loads(cached), True  # (data, from_cache)

    conn = get_pg_conn()
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {TABLE} WHERE "Product ID" = %s', (product_id,))
        row = cur.fetchone()
        if not row:
            return None, False
        cols = [desc[0] for desc in cur.description]
        product = dict(zip(cols, row))
    finally:
        release_pg_conn(conn)  # Always return connection to pool

    hits = r.zincrby("product:hits", 1, cache_key)
    if hits >= HIT_THRESHOLD:
        r.setex(cache_key, CACHE_TTL, json.dumps(product))

    return product, False

# ── Dashboard & Inventory: query Postgres directly ──
def get_all_products():
    conn = get_pg_conn()
    try:
        return pd.read_sql(f'SELECT * FROM {TABLE} ORDER BY "Product ID"', conn)
    finally:
        release_pg_conn(conn)

# ── Alerts ──
def get_low_stock(threshold=10):
    conn = get_pg_conn()
    try:
        return pd.read_sql(
            f'SELECT * FROM {TABLE} WHERE "Products in Store" <= %s AND "Products in Store" > 0',
            conn, params=[threshold,]
        )
    finally:
        release_pg_conn(conn)

def get_out_of_stock():
    conn = get_pg_conn()
    try:
        return pd.read_sql(f'SELECT * FROM {TABLE} WHERE "Products in Store" = 0', conn)
    finally:
        release_pg_conn(conn)

# ── Top accessed products (Reports) ──
def get_top_products(n=10):
    r = get_redis()
    top_keys = r.zrevrange("product:hits", 0, n - 1, withscores=True)
    results = []
    for cache_key, score in top_keys:
        cached = r.get(cache_key)
        if cached:
            product = json.loads(cached)
            product["Access Count"] = int(score)
            results.append(product)
    return results

# ── Invalidate on update/delete ──
def invalidate_product(product_id):
    get_redis().delete(f"product:{product_id}")


# ── Place an order (reduce stock in Postgres + invalidate Redis cache) ──
def place_order(product_id: int, quantity: int):
    conn = get_pg_conn()
    try:
        cur = conn.cursor()

        # Check current stock
        cur.execute('SELECT "Products in Store", "Title of Products" FROM "Dataset_for_NGD" WHERE "Product ID" = %s', (product_id,))
        row = cur.fetchone()
        if not row:
            return False, "Product not found."

        current_stock, title = row
        if current_stock < quantity:
            return False, f"Insufficient stock. Only {current_stock} units available."

        # Deduct stock
        cur.execute(
            'UPDATE "Dataset_for_NGD" SET "Products in Store" = "Products in Store" - %s WHERE "Product ID" = %s',
            (quantity, product_id)
        )
        # Increment sold count
        cur.execute(
            'UPDATE "Dataset_for_NGD" SET "Products Sold" = "Products Sold" + %s WHERE "Product ID" = %s',
            (quantity, product_id)
        )
        conn.commit()

        # Invalidate Redis cache for this product
        get_redis().delete(f"product:{product_id}")

        return True, f"Order placed for {quantity} units of '{title}'."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        release_pg_conn(conn)


# ── Restock a product (increase stock in Postgres + invalidate Redis cache) ──
def restock_product(product_id: int, quantity: int):
    conn = get_pg_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT "Title of Products" FROM "Dataset_for_NGD" WHERE "Product ID" = %s', (product_id,))
        row = cur.fetchone()
        if not row:
            return False, "Product not found."

        cur.execute(
            'UPDATE "Dataset_for_NGD" SET "Products in Store" = "Products in Store" + %s WHERE "Product ID" = %s',
            (quantity, product_id)
        )
        conn.commit()
        get_redis().delete(f"product:{product_id}")
        return True, f"Restocked {quantity} units for '{row[0]}'."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        release_pg_conn(conn)


def add_product(title, price, discount, in_store, sold):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mydatabase",
            user="myuser",
            password="mysecretpassword",
            port=5432
        )
        cur = conn.cursor()
        cur.execute('SELECT MAX("Product ID") FROM "Dataset_for_NGD"')
        row = cur.fetchone()
        max_id = row[0] if row and row[0] is not None else 0
        new_id = max_id + 1
        print(type(new_id), type(title), type(price), type(discount), type(in_store), type(sold))
        cur.execute('''
            INSERT INTO "Dataset_for_NGD" 
            ("Product ID", "Title of Products", "Price ($)", "Discount (%%)", "Products in Store", "Products Sold")
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (new_id, title, price, discount, in_store, sold))
        conn.commit()
        conn.close()
        return True, f"Product added with ID {new_id}."
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return False, str(e)
    


def remove_product(product_id):
    conn = get_pg_conn()
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM "Dataset_for_NGD" WHERE "Product ID" = %s', (product_id,))
        if cur.rowcount == 0:
            return False, "Product not found."
        conn.commit()
        get_redis().delete(f"product:{product_id}")
        return True, "Product removed successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        release_pg_conn(conn)