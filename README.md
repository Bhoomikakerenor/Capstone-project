# 📦 StockSeva — MSME Inventory Management

Odoo-inspired Streamlit UI for small Indian manufacturers & retailers.
Uses **Redis** (real-time cache / pub-sub alerts) + **PostgreSQL** (persistent store).

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Pages
| Page | Description |
|------|-------------|
| 🏠 Dashboard | KPIs, charts, recent transactions, alerts |
| 📦 Inventory | Product list with filters + Add new product |
| 🔄 Transactions | Full log + record new purchase/sale |
| ⚠️ Alerts | Out-of-stock & low-stock with Redis stream |
| 📊 Reports | ABC analysis, supplier & category breakdown |
| ⚙️ Settings | PostgreSQL & Redis config + schema reference |

## Architecture
- **PostgreSQL** → persistent inventory, transactions, config
- **Redis** → HSET per SKU for real-time qty cache, SET for alerts, Pub/Sub for live updates
