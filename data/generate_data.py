"""Script to generate synthetic sample data for the dark store AI system."""
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

np.random.seed(42)

# SKU definitions
SKUS = [
    ("SKU_001", "Full Cream Milk 1L", "dairy"),
    ("SKU_002", "Eggs 12pk", "dairy"),
    ("SKU_003", "Bread White 400g", "staples"),
    ("SKU_004", "Banana 1kg", "produce"),
    ("SKU_005", "Onion 1kg", "produce"),
    ("SKU_006", "Tomato 500g", "produce"),
    ("SKU_007", "Curd 400g", "dairy"),
    ("SKU_008", "Butter 100g", "dairy"),
    ("SKU_009", "Rice 1kg", "staples"),
    ("SKU_010", "Atta 5kg", "staples"),
    ("SKU_011", "Potato 1kg", "produce"),
    ("SKU_012", "Paneer 200g", "dairy"),
    ("SKU_013", "Coconut Oil 1L", "staples"),
    ("SKU_014", "Lays Classic 50g", "snacks"),
    ("SKU_015", "Maggi 2min Noodles", "snacks"),
    ("SKU_016", "Tata Tea 250g", "beverages"),
    ("SKU_017", "Amul Ghee 500ml", "dairy"),
    ("SKU_018", "Biscuits Parle-G 800g", "snacks"),
    ("SKU_019", "Mineral Water 1L", "beverages"),
    ("SKU_020", "Orange Juice 1L", "beverages"),
    ("SKU_021", "Green Tea 25bags", "beverages"),
    ("SKU_022", "Almonds 200g", "snacks"),
    ("SKU_023", "Oats 1kg", "staples"),
    ("SKU_024", "Cheese Slice 200g", "dairy"),
    ("SKU_025", "Sugar 1kg", "staples"),
    ("SKU_026", "Salt 1kg", "staples"),
    ("SKU_027", "Mustard Oil 1L", "staples"),
    ("SKU_028", "Choco Pie 6pk", "snacks"),
    ("SKU_029", "Mango Juice 1L", "beverages"),
    ("SKU_030", "Detergent 500g", "staples"),
]

STORES = ["STORE_A", "STORE_B", "STORE_C"]

# Base demand per SKU (ABC pattern: top 20% drive 80% volume)
BASE_DEMAND = {
    "SKU_001": 40, "SKU_002": 35, "SKU_003": 30, "SKU_004": 28, "SKU_005": 25,
    "SKU_006": 22, "SKU_007": 20, "SKU_008": 18, "SKU_009": 16, "SKU_010": 15,
    "SKU_011": 14, "SKU_012": 13, "SKU_013": 12, "SKU_014": 11, "SKU_015": 10,
    "SKU_016": 9, "SKU_017": 8, "SKU_018": 8, "SKU_019": 7, "SKU_020": 7,
    "SKU_021": 6, "SKU_022": 5, "SKU_023": 5, "SKU_024": 5, "SKU_025": 4,
    "SKU_026": 4, "SKU_027": 4, "SKU_028": 3, "SKU_029": 3, "SKU_030": 3,
}

def generate_orders():
    start_date = date(2023, 7, 1)
    end_date = date(2024, 1, 31)
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    rows = []
    order_id = 1
    
    for current_date in dates:
        dow = current_date.weekday()  # 0=Monday, 6=Sunday
        is_weekend = dow >= 5
        weekend_mult = 1.30 if is_weekend else 1.0
        
        # Month-based seasonality factor
        month = current_date.month
        seasonal_mult = {7: 0.9, 8: 1.0, 9: 1.05, 10: 1.1, 11: 1.15, 12: 1.25, 1: 1.2}.get(month, 1.0)
        
        for store_id in STORES:
            store_mult = {"STORE_A": 1.0, "STORE_B": 0.85, "STORE_C": 0.70}.get(store_id, 1.0)
            
            for sku_id, sku_name, category in SKUS:
                base = BASE_DEMAND[sku_id]
                
                # Category seasonal patterns
                cat_mult = 1.0
                if category == "beverages" and month in [12, 1]:
                    cat_mult = 1.3
                elif category == "produce" and dow in [5, 6]:
                    cat_mult = 1.2
                elif category == "dairy" and is_weekend:
                    cat_mult = 1.15
                elif category == "snacks" and is_weekend:
                    cat_mult = 1.25
                
                # Compute expected demand
                expected = base * weekend_mult * seasonal_mult * store_mult * cat_mult
                
                # Add noise
                noise = np.random.normal(0, expected * 0.20)
                daily_demand = max(0, round(expected + noise))
                
                if daily_demand == 0:
                    continue
                
                # Split into individual orders (1-10 units each)
                remaining = daily_demand
                while remaining > 0:
                    qty = min(remaining, np.random.randint(1, 11))
                    rows.append({
                        "order_id": f"ORD_{order_id:07d}",
                        "order_date": current_date.strftime("%Y-%m-%d"),
                        "sku_id": sku_id,
                        "sku_name": sku_name,
                        "quantity": qty,
                        "store_id": store_id,
                        "category": category,
                    })
                    order_id += 1
                    remaining -= qty
    
    return pd.DataFrame(rows)


def generate_inventory():
    rows = []
    for store_id in STORES:
        store_mult = {"STORE_A": 1.0, "STORE_B": 0.85, "STORE_C": 0.70}.get(store_id, 1.0)
        for sku_id, sku_name, category in SKUS:
            base = BASE_DEMAND[sku_id]
            max_stock = int(base * store_mult * 7 * 1.5)
            reorder_point = int(base * store_mult * 2)
            
            # Some items near expiry for testing
            if category in ["dairy", "produce"]:
                expiry_days = np.random.choice([1, 2, 3, 5, 7, 14, 30], p=[0.05, 0.05, 0.10, 0.15, 0.20, 0.25, 0.20])
            else:
                expiry_days = np.random.choice([7, 14, 30, 60, 90, 180], p=[0.05, 0.10, 0.20, 0.30, 0.25, 0.10])
            
            # Some items below reorder point for alert testing
            stock_factor = np.random.choice([0.3, 0.5, 0.7, 1.0, 1.5, 2.0], p=[0.10, 0.10, 0.15, 0.35, 0.20, 0.10])
            current_stock = max(1, int(max_stock * stock_factor))
            
            unit_cost = {
                "dairy": round(np.random.uniform(20, 150), 2),
                "produce": round(np.random.uniform(15, 80), 2),
                "staples": round(np.random.uniform(30, 200), 2),
                "snacks": round(np.random.uniform(10, 100), 2),
                "beverages": round(np.random.uniform(20, 120), 2),
            }[category]
            
            rows.append({
                "sku_id": sku_id,
                "sku_name": sku_name,
                "store_id": store_id,
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "max_stock": max_stock,
                "expiry_days": int(expiry_days),
                "unit_cost": unit_cost,
                "category": category,
            })
    
    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    print("Generating orders data...")
    orders_df = generate_orders()
    orders_df.to_csv("data/sample_orders.csv", index=False)
    print(f"  Generated {len(orders_df):,} order rows")
    
    print("Generating inventory data...")
    inv_df = generate_inventory()
    inv_df.to_csv("data/sample_inventory.csv", index=False)
    print(f"  Generated {len(inv_df):,} inventory rows")
    
    print("Done!")
