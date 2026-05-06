import sqlite3
import pandas as pd

DB_PATH = "data/food_tracker.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL UNIQUE,
            cuisine_type    TEXT,
            city            TEXT    DEFAULT 'Bengaluru',
            avg_rating      REAL
        );

        CREATE TABLE IF NOT EXISTS food_items (
            item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            category        TEXT,
            health_category TEXT    CHECK(health_category IN ('Healthy','Moderate','Unhealthy')),
            calories_approx INTEGER
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date      DATE    NOT NULL,
            order_time      TEXT,
            meal_time       TEXT,
            restaurant_id   INTEGER REFERENCES restaurants(restaurant_id),
            item_id         INTEGER REFERENCES food_items(item_id),
            quantity        INTEGER DEFAULT 1,
            base_price      REAL,
            delivery_fee    REAL    DEFAULT 0,
            discount        REAL    DEFAULT 0,
            total_amount    REAL,
            platform        TEXT    CHECK(platform IN ('Zomato','Swiggy','Blinkit'))
        );
    """)

    conn.commit()
    print("✅ Tables created!")
    return conn

def load_csv_to_db(conn):
    df = pd.read_csv("data/processed/food_orders_clean.csv")

    # ── Load restaurants ──────────────────────────────────
    cuisine_map = {
        "Burger King": "Fast Food",   "McDonald's": "Fast Food",
        "Subway": "Sandwiches",       "Zomato Kitchen": "Indian",
        "Freshmenu": "Healthy",       "Box8": "Indian",
        "Starbucks": "Cafe",          "Wow Momo": "Chinese",
        "Oven Story": "Italian",      "Licious": "Non-Veg"
    }
    rating_map = {
        "Burger King": 4.1, "McDonald's": 4.2, "Subway": 4.3,
        "Zomato Kitchen": 4.0, "Freshmenu": 4.4, "Box8": 4.1,
        "Starbucks": 4.5, "Wow Momo": 4.2, "Oven Story": 4.3, "Licious": 4.5
    }
    restaurants = df["restaurant"].unique()
    for r in restaurants:
        conn.execute(
            "INSERT OR IGNORE INTO restaurants (name, cuisine_type, avg_rating) VALUES (?,?,?)",
            (r, cuisine_map.get(r, "Other"), rating_map.get(r, 4.0))
        )
    conn.commit()

    rest_df = pd.read_sql("SELECT restaurant_id, name FROM restaurants", conn)
    rest_map = dict(zip(rest_df["name"], rest_df["restaurant_id"]))

    # ── Load food items ───────────────────────────────────
    calorie_map = {
        "Whopper": 660, "Cheese Fries": 340, "Chocolate Shake": 530,
        "Crispy Chicken": 470, "McAloo Tikki": 190, "McSpicy Paneer": 440,
        "Large Fries": 490, "McFlurry": 340, "Veggie Delight Sub": 230,
        "Chicken Teriyaki": 370, "Multigrain Sandwich": 210,
        "Dal Rice Bowl": 320, "Paneer Butter Masala": 380,
        "Chicken Biryani": 490, "Grilled Chicken Salad": 180,
        "Quinoa Bowl": 290, "Fruit Smoothie": 140, "Rajma Chawal": 350,
        "Butter Chicken": 420, "Paneer Tikka Wrap": 310,
        "Frappuccino": 380, "Cold Brew": 15, "Croissant": 260,
        "Steamed Momos": 180, "Fried Momos": 260, "Momo Soup": 120,
        "Margherita Pizza": 560, "BBQ Chicken Pizza": 650,
        "Pasta": 410, "Grilled Fish": 220,
        "Chicken Kebab": 250, "Mutton Curry": 390
    }
    items = df[["item", "health_category"]].drop_duplicates()
    for _, row in items.iterrows():
        conn.execute(
            "INSERT OR IGNORE INTO food_items (name, health_category, calories_approx) VALUES (?,?,?)",
            (row["item"], row["health_category"], calorie_map.get(row["item"], 300))
        )
    conn.commit()

    item_df  = pd.read_sql("SELECT item_id, name FROM food_items", conn)
    item_map = dict(zip(item_df["name"], item_df["item_id"]))

    # ── Load orders ───────────────────────────────────────
    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO orders
              (order_date, order_time, meal_time, restaurant_id, item_id,
               quantity, base_price, delivery_fee, discount, total_amount, platform)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            str(row["order_date"])[:10],
            row.get("order_time", "19:00"),
            row.get("meal_time", "Dinner"),
            rest_map.get(row["restaurant"]),
            item_map.get(row["item"]),
            int(row.get("quantity", 1)),
            float(row.get("base_price", 0)),
            float(row.get("delivery_fee", 0)),
            float(row.get("discount", 0)),
            float(row.get("total_amount", 0)),
            row.get("platform", "Zomato")
        ))
    conn.commit()
    print(f"✅ Loaded {len(df)} orders into the database!")

def run_sample_queries(conn):
    print("\n" + "="*50)
    print("📊 SAMPLE SQL QUERIES & RESULTS")
    print("="*50)

    queries = {
        "Total spend by platform": """
            SELECT platform,
                   COUNT(*)          AS total_orders,
                   ROUND(SUM(total_amount), 0) AS total_spent
            FROM orders
            GROUP BY platform
            ORDER BY total_spent DESC
        """,
        "Top 5 restaurants by spend": """
            SELECT r.name,
                   COUNT(o.order_id)        AS orders,
                   ROUND(SUM(o.total_amount),0) AS total_spent
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            GROUP BY r.name
            ORDER BY total_spent DESC
            LIMIT 5
        """,
        "Healthy vs Unhealthy spend": """
            SELECT f.health_category,
                   COUNT(*)                     AS items_ordered,
                   ROUND(SUM(o.total_amount),0) AS total_spent,
                   ROUND(SUM(o.total_amount)*100.0/
                     (SELECT SUM(total_amount) FROM orders), 1) AS pct
            FROM orders o
            JOIN food_items f ON o.item_id = f.item_id
            GROUP BY f.health_category
            ORDER BY total_spent DESC
        """,
        "Monthly spend trend": """
            SELECT strftime('%Y-%m', order_date) AS month,
                   COUNT(*)                      AS orders,
                   ROUND(SUM(total_amount), 0)   AS total_spent
            FROM orders
            GROUP BY month
            ORDER BY month
            LIMIT 6
        """,
        "Most ordered meal times": """
            SELECT meal_time,
                   COUNT(*) AS orders,
                   ROUND(AVG(total_amount), 0) AS avg_spend
            FROM orders
            GROUP BY meal_time
            ORDER BY orders DESC
        """
    }

    for title, sql in queries.items():
        print(f"\n🔹 {title}:")
        result = pd.read_sql(sql, conn)
        print(result.to_string(index=False))

if __name__ == "__main__":
    conn = create_database()
    load_csv_to_db(conn)
    run_sample_queries(conn)
    conn.close()
    print(f"\n✅ Database saved at: {DB_PATH}")
    print("📌 Connect Power BI to this .db file using ODBC SQLite driver!")