# 🏪 Dark Store AI — Inventory Forecasting System

A **functional V1 inventory forecasting system** for quick-commerce dark stores (Blinkit / Zepto / Swiggy Instamart style). Provides demand forecasts, expiry risk scoring, and reorder alerts — all in a human-readable daily ops report.

> **Design philosophy**: Rules first, ML second. Human-readable outputs. Improve step by step.

---

## Project Structure

```
dark-store-ai/
├── data/
│   ├── generate_data.py           # Script to regenerate synthetic data
│   ├── sample_orders.csv          # Synthetic order data (6+ months, 10k+ rows)
│   └── sample_inventory.csv       # Inventory snapshot with expiry info
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Load & validate raw order/inventory data
│   ├── features.py                # Feature engineering for ML models
│   ├── forecaster.py              # Prophet + LightGBM forecasting logic
│   ├── inventory_alerts.py        # Expiry risk scorer + dynamic reorder engine
│   └── report.py                  # Human-readable daily ops report generator
├── notebooks/
│   └── explore_and_forecast.ipynb # Interactive notebook: charts, forecasts, alerts
├── output/
│   └── daily_report.txt           # Generated after running main.py
├── main.py                        # Single entry point — run everything end-to-end
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/pradyumna-hn/dark-store-ai.git
cd dark-store-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Regenerate sample data
python data/generate_data.py

# 4. Run the full pipeline
python main.py

# Run for a different store
python main.py --store STORE_B

# Use LightGBM instead of Prophet
python main.py --method lgbm

# Full options
python main.py --store STORE_A --horizon 7 --top-n 20 --method prophet
```

---

## How to Use the Notebook

```bash
jupyter notebook notebooks/explore_and_forecast.ipynb
```

The notebook walks through:
1. **Data Overview** — load data, show shape, sample rows, basic stats
2. **ABC Analysis** — bar chart of top 20 SKUs by volume
3. **Demand Patterns** — weekday vs weekend line charts for top 3 SKUs
4. **Forecast Visualization** — Prophet chart with confidence intervals
5. **Inventory Alerts** — expiry risk table and reorder alerts
6. **V2 Ideas** — notes on what to build next

---

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║    DARK STORE DAILY OPS REPORT — 2024-01-15 | STORE_A   ║
╚══════════════════════════════════════════════════════════╝

📦 DEMAND FORECAST — NEXT 7 DAYS (Top Items)
───────────────────────────────────────────────────────────────────────────
Item                   | Today |   D+1 |   D+2 |   D+3 |   D+4 |   D+5 |   D+6
Full Cream Milk 1L     |    42 |    38 |    45 |    40 |    51 |    60 |    55
Eggs 12pk              |    28 |    30 |    27 |    32 |    29 |    35 |    38

⚠️  EXPIRY RISK ALERTS
───────────────────────────────────────────────────────────────────────────
🔴 HIGH RISK  — Banana 1kg              | Stock:   80 units | Expires in  2 days | Est. sell:   30 units
🟡 MED RISK   — Curd 400g              | Stock:   50 units | Expires in  3 days | Est. sell:   38 units

🔁 REORDER ALERTS
───────────────────────────────────────────────────────────────────────────
⚡ REORDER NOW — Full Cream Milk 1L    | Current:   15 | Dynamic ROP:   22.0 | Order:   85 units

📊 SUMMARY
───────────────────────────────────────────────────────────────────────────
  Total SKUs monitored   : 20
  Reorder alerts         : 3
  High expiry risk items : 2
  Med expiry risk items  : 1
  Report generated at    : 2024-01-15 06:00:00
```

---

## V2 Ideas

- **Real-time pipeline** — connect to a live POS/WMS system (Kafka, Flink)
- **Per-store model tuning** — each store may have very different demand patterns
- **Supplier scoring** — rank suppliers by lead time reliability and quality
- **Dynamic markdown engine** — auto-generate markdown % for near-expiry items based on demand elasticity
- **Per-customer personalization** — use order history to predict individual demand
- **Anomaly detection** — flag unusual demand spikes (promotions, viral moments)
- **Multi-store replenishment** — balance stock across stores in real time
- **REST API** — expose forecasts and alerts as an API for warehouse management systems

---

## Design Philosophy

> **Rules first, ML second. Human-readable outputs. Improve step by step.**

- Start with simple, interpretable rules (rolling averages, static ROPs) before adding ML complexity
- Every output should be readable by a non-technical store manager
- Build in graceful fallbacks so the system never crashes silently
- Measure forecast accuracy (MAE/MAPE) and improve iteratively