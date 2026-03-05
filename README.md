# 🏪 Dark Store AI — Inventory Forecasting System

A **functional V1 inventory forecasting system** for quick-commerce dark stores (Blinkit / Zepto / Swiggy Instamart style). Provides demand forecasts, expiry risk scoring, and reorder alerts — all in a human-readable daily ops report.

> **Design philosophy**: Rules first, ML second. Human-readable outputs. Improve step by step.

---

## ⚡ Quick Start (under 2 minutes)

> **Requires Python 3.8+**

```bash
# 1. Clone
git clone https://github.com/pradyumna-hn/dark-store-ai.git
cd dark-store-ai

# 2. Install core dependencies (fast path — no Prophet needed)
pip install pandas numpy lightgbm scikit-learn matplotlib seaborn

# 3. Run! (uses LightGBM — fastest way to get a working report)
python main.py --method lgbm
```

That's it. A daily ops report is printed to your terminal **and** saved to `output/daily_report.txt`.

> 💡 **Want Prophet instead?** It's more accurate but requires extra setup — see [Full Installation](#setup--full-installation) below.

---

## 🖥️ All Run Options

```bash
# Default store (STORE_A), LightGBM, 7-day forecast, top 20 SKUs
python main.py --method lgbm

# Switch store
python main.py --store STORE_B --method lgbm
python main.py --store STORE_C --method lgbm

# Change forecast horizon (e.g. 14 days)
python main.py --method lgbm --horizon 14

# Analyse fewer SKUs (faster)
python main.py --method lgbm --top-n 5

# Use Prophet (more accurate, slower to install — see notes below)
python main.py --method prophet

# Custom data files
python main.py --orders path/to/orders.csv --inventory path/to/inventory.csv

# Full options reference
python main.py --help
```

### CLI Options Reference

| Option | Default | Description |
|---|---|---|
| `--store` | `STORE_A` | Store to report on (`STORE_A`, `STORE_B`, `STORE_C`) |
| `--method` | `prophet` | Forecasting engine: `lgbm` (fast) or `prophet` (accurate) |
| `--horizon` | `7` | Days ahead to forecast |
| `--top-n` | `20` | Number of top SKUs to include |
| `--orders` | `data/sample_orders.csv` | Path to a custom orders CSV |
| `--inventory` | `data/sample_inventory.csv` | Path to a custom inventory CSV |
| `--output-dir` | `output/` | Directory to save `daily_report.txt` |

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

## Setup — Full Installation

Install **all** dependencies (including Prophet for best forecast accuracy):

```bash
pip install -r requirements.txt
```

> ⚠️ **Prophet install note:** Prophet needs `cmdstan` (a C++ compiler) which can fail on some machines.
> If `pip install prophet` errors, try:
> ```bash
> pip install pystan==2.19.1.1
> pip install prophet
> ```
> Or use `--method lgbm` — it gives good results without any extra setup.

```bash
# (Optional) Regenerate the sample data from scratch
python data/generate_data.py

# Run with Prophet (best accuracy)
python main.py --method prophet
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