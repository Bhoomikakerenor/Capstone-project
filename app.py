import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=" MSME Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS (Odoo-inspired, Indian MSME flavor) ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root & Reset ── */
:root {
    --brand:        #875BF7;
    --brand-light:  #EEE9FE;
    --brand-dark:   #6741D9;
    --accent:       #F79009;
    --accent-light: #FEF0C7;
    --danger:       #F04438;
    --danger-light: #FEE4E2;
    --success:      #12B76A;
    --success-light:#D1FADF;
    --info:         #0BA5EC;
    --info-light:   #E0F2FE;
    --bg:           #F8F7FF;
    --surface:      #FFFFFF;
    --border:       #E9E8F5;
    --text:         #1A1523;
    --text-muted:   #6B7280;
    --sidebar-bg:   #1A1523;
    --sidebar-text: #C9C4D4;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: var(--sidebar-text) !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 2px 0;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 4px rgba(26,21,35,0.06);
    transition: box-shadow 0.2s;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { box-shadow: 0 4px 16px rgba(135,91,247,0.12); }
.kpi-label { font-size: 0.75rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.05em; text-transform: uppercase; }
.kpi-value { font-size: 1.85rem; font-weight: 800; color: var(--text); line-height: 1.1; margin: 0.2rem 0; }
.kpi-delta { font-size: 0.78rem; font-weight: 600; }
.kpi-delta.up   { color: var(--success); }
.kpi-delta.down { color: var(--danger); }
.kpi-icon { font-size: 1.6rem; float: right; margin-top: -0.2rem; }

/* ── Section Headers ── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--brand-light);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Top Nav Bar ── */
.top-bar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(26,21,35,0.05);
}
.top-bar-title { font-size: 1.4rem; font-weight: 800; color: var(--brand); letter-spacing: -0.02em; }
.top-bar-sub   { font-size: 0.78rem; color: var(--text-muted); font-weight: 500; }
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.badge-purple { background: var(--brand-light); color: var(--brand-dark); }
.badge-orange { background: var(--accent-light); color: #B45309; }
.badge-red    { background: var(--danger-light); color: #B42318; }
.badge-green  { background: var(--success-light); color: #027A48; }
.badge-blue   { background: var(--info-light);  color: #026AA2; }

/* ── Data table styling ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
[data-testid="stDataFrame"] table { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    padding: 0.4rem 1.1rem !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--brand) !important;
    box-shadow: 0 1px 4px rgba(26,21,35,0.1) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--brand) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 0.45rem 1.2rem !important;
    transition: all 0.2s !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stButton > button:hover {
    background: var(--brand-dark) !important;
    box-shadow: 0 4px 12px rgba(135,91,247,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs & Selects ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > textarea {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
    background: var(--surface) !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(135,91,247,0.15) !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: var(--surface);
    padding: 1rem 1.2rem;
    border-radius: 12px;
    border: 1px solid var(--border);
}

/* ── Alert boxes ── */
.alert-box {
    padding: 0.75rem 1rem;
    border-radius: 10px;
    margin: 0.4rem 0;
    font-size: 0.83rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.alert-box.danger  { background: var(--danger-light);  color: #B42318; border-left: 4px solid var(--danger); }
.alert-box.warning { background: var(--accent-light);  color: #B45309; border-left: 4px solid var(--accent); }
.alert-box.success { background: var(--success-light); color: #027A48; border-left: 4px solid var(--success); }

/* ── Redis/PG pill ── */
.db-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #1A1523; color: #C9C4D4;
    border-radius: 999px; padding: 4px 12px;
    font-size: 0.72rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;
}
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot.green  { background: #12B76A; box-shadow: 0 0 6px #12B76A; }
.dot.red    { background: #F79009; box-shadow: 0 0 6px #F79009; }

/* ── Product row card ── */
.prod-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.prod-avatar {
    width: 34px; height: 34px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)


# ─── MOCK DATA ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    categories = ["Raw Materials", "Finished Goods", "Packaging", "Spare Parts", "Semi-Finished"]
    units      = ["kg", "pcs", "box", "litre", "metre", "roll"]
    warehouses = ["Main Godown – Delhi", "Unit-2 – Noida", "Cold Store – Gurgaon"]
    suppliers  = ["Sharma Traders", "Patel Industries", "Singh & Co.", "Kumar Enterprises", "Mehta Suppliers"]

    random.seed(42)
    n = 60
    skus = [f"SKU-{1000+i}" for i in range(n)]
    names = [
        "Cotton Fabric Roll", "Polypropylene Granules", "Aluminium Sheet 2mm",
        "Packaging Tape 48mm", "Rubber Gasket 10mm", "Brass Fitting 1/2\"",
        "Stainless Rod 6mm", "HDPE Pipe 2\"", "Corrugated Box 12x10",
        "Nylon Thread 20s", "PVC Sheet 1mm", "MS Angle 40x40",
        "Polyester Yarn", "Wooden Pallet", "Kraft Paper Roll",
        "Electric Motor 1HP", "Ball Bearing 6204", "V-Belt A45",
        "Welding Electrode", "Paint Primer White",
    ] * 3
    names = names[:n]

    qty   = [random.randint(0, 500) for _ in range(n)]
    reorder= [random.randint(20, 80)  for _ in range(n)]
    price = [round(random.uniform(15, 2500), 2) for _ in range(n)]

    df = pd.DataFrame({
        "SKU":        skus,
        "Product":    names,
        "Category":   [random.choice(categories) for _ in range(n)],
        "Unit":       [random.choice(units)       for _ in range(n)],
        "Qty":        qty,
        "Reorder":    reorder,
        "Price_INR":  price,
        "Warehouse":  [random.choice(warehouses)  for _ in range(n)],
        "Supplier":   [random.choice(suppliers)   for _ in range(n)],
        "Last_Updated": [
            (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%d %b %Y")
            for _ in range(n)
        ],
    })
    df["Stock_Value"] = (df["Qty"] * df["Price_INR"]).round(2)
    df["Status"] = df.apply(
        lambda r: "Out of Stock" if r["Qty"] == 0
        else ("Low Stock" if r["Qty"] < r["Reorder"] else "In Stock"), axis=1
    )
    return df


@st.cache_data
def load_transactions():
    random.seed(7)
    types = ["Purchase", "Sale", "Transfer", "Adjustment"]
    parties= ["Sharma Traders", "Patel Retail", "Singh Mfg", "Kumar Store", "Internal"]
    n = 80
    return pd.DataFrame({
        "TXN_ID":  [f"TXN-{5000+i}" for i in range(n)],
        "Date":    [(datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%d %b %Y") for _ in range(n)],
        "Type":    [random.choice(types) for _ in range(n)],
        "SKU":     [f"SKU-{random.randint(1000,1059)}" for _ in range(n)],
        "Qty":     [random.randint(1, 200) for _ in range(n)],
        "Party":   [random.choice(parties) for _ in range(n)],
        "Amount_INR": [round(random.uniform(500, 50000), 2) for _ in range(n)],
    })


df    = load_data()
txns  = load_transactions()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0.5rem 1.5rem 0.5rem;">
        <div style="font-size:1.35rem;font-weight:800;color:#875BF7;letter-spacing:-0.02em;">📦 StockSeva</div>
        <div style="font-size:0.72rem;color:#6B7280;margin-top:2px;font-weight:500;">MSME Inventory Platform</div>
        <div style="margin-top:0.8rem;display:flex;gap:6px;flex-wrap:wrap;">
            <span class="db-pill"><span class="dot green"></span>Redis</span>
            <span class="db-pill"><span class="dot red"></span>PostgreSQL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.1em;color:#6B7280;padding:0 0.5rem;margin-bottom:0.4rem;text-transform:uppercase;'>Navigation</div>", unsafe_allow_html=True)

    page = st.radio(
        "", 
        ["🏠  Dashboard", "📦  Inventory", "🔄  Transactions", "⚠️  Alerts", "📊  Reports", "⚙️  Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="padding:0.75rem;background:rgba(135,91,247,0.12);border-radius:10px;border:1px solid rgba(135,91,247,0.2);">
        <div style="font-size:0.72rem;font-weight:700;color:#875BF7;margin-bottom:4px;">🏭 Active Business</div>
        <div style="font-size:0.82rem;font-weight:600;color:#C9C4D4;">Gupta Fasteners Pvt Ltd</div>
        <div style="font-size:0.72rem;color:#6B7280;">GSTIN: 07AAACG1234F1Z5</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">
        <div style="font-size:0.68rem;color:#4B5563;">v1.0.0 · Redis + PostgreSQL</div>
    </div>
    """, unsafe_allow_html=True)


# ─── TOP BAR ────────────────────────────────────────────────────────────────
today_str = datetime.now().strftime("%A, %d %B %Y")
low_count = len(df[df["Status"] == "Low Stock"])
out_count = len(df[df["Status"] == "Out of Stock"])

st.markdown(f"""
<div class="top-bar">
    <div>
        <div class="top-bar-title">📦 StockSeva</div>
        <div class="top-bar-sub">MSME Inventory Management · {today_str}</div>
    </div>
    <div style="display:flex;gap:10px;align-items:center;">
        <span class="badge badge-red">⚠️ {low_count} Low Stock</span>
        <span class="badge badge-orange">🚫 {out_count} Out of Stock</span>
        <span class="badge badge-green">✅ PostgreSQL Connected</span>
        <span class="badge badge-purple">⚡ Redis Active</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if "Dashboard" in page:

    # KPI Row
    total_val   = df["Stock_Value"].sum()
    total_skus  = len(df)
    in_stock    = len(df[df["Status"] == "In Stock"])

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "Total Stock Value",  f"₹{total_val/1e5:.2f}L",  "↑ 8.3% vs last month",  "up",  "💰"),
        (c2, "Total SKUs",         str(total_skus),            "5 new this week",        "up",  "🗂️"),
        (c3, "Low / Out of Stock", f"{low_count} / {out_count}","↑ needs attention",    "down","⚠️"),
        (c4, "In-Stock Items",     str(in_stock),              f"{in_stock/total_skus*100:.0f}% availability","up","✅"),
    ]
    for col, label, val, delta, direction, icon in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label} <span class="kpi-icon">{icon}</span></div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-delta {direction}">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    # Charts Row
    st.markdown('<div class="section-header">📈 Analytics Overview</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns([1.4, 1, 1])

    with ch1:
        # Stock value by category bar
        cat_val = df.groupby("Category")["Stock_Value"].sum().reset_index().sort_values("Stock_Value", ascending=True)
        fig = px.bar(cat_val, x="Stock_Value", y="Category", orientation="h",
                     color="Stock_Value", color_continuous_scale=["#EEE9FE","#875BF7"],
                     labels={"Stock_Value": "Value (₹)", "Category": ""})
        fig.update_layout(
            title="Stock Value by Category",
            title_font=dict(size=13, family="Plus Jakarta Sans"),
            margin=dict(l=0,r=0,t=35,b=0), height=260,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, font=dict(family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=True, gridcolor="#E9E8F5"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        # Status donut
        status_cnt = df["Status"].value_counts().reset_index()
        status_cnt.columns = ["Status", "Count"]
        colors = {"In Stock": "#12B76A", "Low Stock": "#F79009", "Out of Stock": "#F04438"}
        fig2 = px.pie(status_cnt, names="Status", values="Count", hole=0.62,
                      color="Status", color_discrete_map=colors)
        fig2.update_traces(textinfo="percent+label", textfont_size=10)
        fig2.update_layout(
            title="Stock Status Split",
            title_font=dict(size=13, family="Plus Jakarta Sans"),
            margin=dict(l=0,r=0,t=35,b=0), height=260,
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            font=dict(family="Plus Jakarta Sans"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with ch3:
        # Warehouse distribution
        wh = df.groupby("Warehouse")["Stock_Value"].sum().reset_index()
        wh["Warehouse_Short"] = wh["Warehouse"].str.split("–").str[0].str.strip()
        fig3 = px.pie(wh, names="Warehouse_Short", values="Stock_Value", hole=0.55,
                      color_discrete_sequence=["#875BF7","#F79009","#0BA5EC"])
        fig3.update_traces(textinfo="percent+label", textfont_size=10)
        fig3.update_layout(
            title="By Warehouse",
            title_font=dict(size=13, family="Plus Jakarta Sans"),
            margin=dict(l=0,r=0,t=35,b=0), height=260,
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            font=dict(family="Plus Jakarta Sans"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Recent Transactions + Alerts
    col_l, col_r = st.columns([1.5, 1])

    with col_l:
        st.markdown('<div class="section-header">🔄 Recent Transactions</div>', unsafe_allow_html=True)
        recent = txns.head(8)[["TXN_ID","Date","Type","SKU","Qty","Amount_INR","Party"]]
        def color_type(val):
            c = {"Purchase":"#12B76A","Sale":"#875BF7","Transfer":"#0BA5EC","Adjustment":"#F79009"}
            return f"color: {c.get(val,'#333')};font-weight:600"
        st.dataframe(
            recent.style.applymap(color_type, subset=["Type"]),
            use_container_width=True, hide_index=True, height=260
        )

    with col_r:
        st.markdown('<div class="section-header">🚨 Stock Alerts</div>', unsafe_allow_html=True)
        alert_df = df[df["Status"] != "In Stock"].nsmallest(8, "Qty")[["SKU","Product","Qty","Reorder","Status"]]
        for _, row in alert_df.iterrows():
            cls = "danger" if row["Status"] == "Out of Stock" else "warning"
            icon = "🚫" if row["Status"] == "Out of Stock" else "⚠️"
            st.markdown(f"""
            <div class="alert-box {cls}">
                {icon} <strong>{row['SKU']}</strong> — {row['Product'][:28]}
                &nbsp;|&nbsp; Qty: <strong>{row['Qty']}</strong> / Reorder: {row['Reorder']}
            </div>
            """, unsafe_allow_html=True)

    # Trend sparkline
    st.markdown('<div class="section-header">📆 Monthly Transaction Volume</div>', unsafe_allow_html=True)
    months = ["Oct","Nov","Dec","Jan","Feb","Mar"]
    purchase = [random.randint(80,200) for _ in months]
    sales    = [random.randint(60,180) for _ in months]
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=months, y=purchase, name="Purchases", mode="lines+markers",
                              line=dict(color="#875BF7", width=2.5), marker=dict(size=6)))
    fig4.add_trace(go.Scatter(x=months, y=sales, name="Sales", mode="lines+markers",
                              line=dict(color="#F79009", width=2.5), marker=dict(size=6)))
    fig4.update_layout(
        margin=dict(l=0,r=0,t=10,b=0), height=180,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.15, font=dict(size=11)),
        font=dict(family="Plus Jakarta Sans"),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#E9E8F5"),
    )
    st.plotly_chart(fig4, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: INVENTORY
# ════════════════════════════════════════════════════════════════════════════
elif "Inventory" in page:

    tab1, tab2 = st.tabs(["📋  Product List", "➕  Add Product"])

    with tab1:
        st.markdown('<div class="section-header">📋 Inventory Master</div>', unsafe_allow_html=True)

        # Filters
        f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.2])
        with f1: search   = st.text_input("🔍 Search SKU / Product", placeholder="e.g. Cotton, SKU-1002…")
        with f2: cat_filt = st.selectbox("Category", ["All"] + sorted(df["Category"].unique()))
        with f3: wh_filt  = st.selectbox("Warehouse", ["All"] + sorted(df["Warehouse"].unique()))
        with f4: st_filt  = st.selectbox("Status", ["All", "In Stock", "Low Stock", "Out of Stock"])

        filt = df.copy()
        if search:    filt = filt[filt["Product"].str.contains(search, case=False) | filt["SKU"].str.contains(search, case=False)]
        if cat_filt != "All": filt = filt[filt["Category"] == cat_filt]
        if wh_filt  != "All": filt = filt[filt["Warehouse"] == wh_filt]
        if st_filt  != "All": filt = filt[filt["Status"] == st_filt]

        def style_status(val):
            c = {"In Stock":"color:#027A48;font-weight:700", "Low Stock":"color:#B45309;font-weight:700", "Out of Stock":"color:#B42318;font-weight:700"}
            return c.get(val, "")

        display_cols = ["SKU","Product","Category","Unit","Qty","Reorder","Price_INR","Stock_Value","Warehouse","Supplier","Status","Last_Updated"]
        st.dataframe(
            filt[display_cols].style.applymap(style_status, subset=["Status"]),
            use_container_width=True, hide_index=True, height=420
        )
        st.caption(f"Showing {len(filt)} of {len(df)} products  ·  Total Value: ₹{filt['Stock_Value'].sum():,.0f}")

    with tab2:
        st.markdown('<div class="section-header">➕ Add New Product</div>', unsafe_allow_html=True)
        with st.form("add_product_form"):
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1: sku_in   = st.text_input("SKU *", placeholder="SKU-1060")
            with r1c2: name_in  = st.text_input("Product Name *", placeholder="Cotton Yarn 20s")
            with r1c3: cat_in   = st.selectbox("Category", ["Raw Materials","Finished Goods","Packaging","Spare Parts","Semi-Finished"])

            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            with r2c1: qty_in    = st.number_input("Opening Qty", min_value=0, value=0)
            with r2c2: unit_in   = st.selectbox("Unit", ["kg","pcs","box","litre","metre","roll"])
            with r2c3: price_in  = st.number_input("Price (₹)", min_value=0.0, value=0.0, format="%.2f")
            with r2c4: reorder_in= st.number_input("Reorder Level", min_value=0, value=20)

            r3c1, r3c2 = st.columns(2)
            with r3c1: wh_in  = st.selectbox("Warehouse", ["Main Godown – Delhi","Unit-2 – Noida","Cold Store – Gurgaon"])
            with r3c2: sup_in = st.selectbox("Supplier", ["Sharma Traders","Patel Industries","Singh & Co.","Kumar Enterprises","Mehta Suppliers"])

            desc_in = st.text_area("Description / Notes", placeholder="Optional product notes…", height=80)
            submitted = st.form_submit_button("💾 Save to PostgreSQL + Redis Cache")

            if submitted:
                if sku_in and name_in:
                    st.success(f"✅ **{name_in}** ({sku_in}) saved to PostgreSQL and cached in Redis!")
                    st.code(f"""
-- PostgreSQL INSERT
INSERT INTO inventory (sku, name, category, qty, unit, price_inr, reorder_level, warehouse, supplier)
VALUES ('{sku_in}', '{name_in}', '{cat_in}', {qty_in}, '{unit_in}', {price_in}, {reorder_in}, '{wh_in}', '{sup_in}');

-- Redis HSET
HSET inventory:{sku_in} name "{name_in}" qty {qty_in} price {price_in} status "{'In Stock' if qty_in > reorder_in else 'Low Stock'}"
EXPIRE inventory:{sku_in} 3600
""", language="sql")
                else:
                    st.error("⚠️ SKU and Product Name are required fields.")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ════════════════════════════════════════════════════════════════════════════
elif "Transactions" in page:

    tab_t1, tab_t2 = st.tabs(["📜  Transaction Log", "➕  New Transaction"])

    with tab_t1:
        st.markdown('<div class="section-header">📜 Transaction History</div>', unsafe_allow_html=True)

        tc1, tc2, tc3 = st.columns([2, 1.2, 1.2])
        with tc1: t_search = st.text_input("🔍 Search TXN ID / SKU / Party")
        with tc2: t_type   = st.selectbox("Type", ["All","Purchase","Sale","Transfer","Adjustment"])
        with tc3: t_date   = st.date_input("From Date", value=datetime.now() - timedelta(days=30))

        t_filt = txns.copy()
        if t_search: t_filt = t_filt[t_filt["TXN_ID"].str.contains(t_search, case=False) | t_filt["Party"].str.contains(t_search, case=False)]
        if t_type != "All": t_filt = t_filt[t_filt["Type"] == t_type]

        def color_txn(val):
            c = {"Purchase":"color:#027A48;font-weight:700","Sale":"color:#6741D9;font-weight:700",
                 "Transfer":"color:#026AA2;font-weight:700","Adjustment":"color:#B45309;font-weight:700"}
            return c.get(val,"")

        st.dataframe(
            t_filt.style.applymap(color_txn, subset=["Type"]),
            use_container_width=True, hide_index=True, height=450
        )
        st.caption(f"{len(t_filt)} records · Total: ₹{t_filt['Amount_INR'].sum():,.0f}")

    with tab_t2:
        st.markdown('<div class="section-header">➕ Record New Transaction</div>', unsafe_allow_html=True)
        with st.form("new_txn_form"):
            nt1, nt2, nt3 = st.columns(3)
            with nt1: txn_type = st.selectbox("Transaction Type *", ["Purchase","Sale","Transfer","Adjustment"])
            with nt2: txn_sku  = st.text_input("SKU *", placeholder="SKU-1002")
            with nt3: txn_qty  = st.number_input("Quantity *", min_value=1, value=10)

            np1, np2, np3 = st.columns(3)
            with np1: txn_party  = st.text_input("Party / Vendor", placeholder="Sharma Traders")
            with np2: txn_amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, format="%.2f")
            with np3: txn_date   = st.date_input("Date", value=datetime.now())

            txn_notes = st.text_area("Notes", height=70)
            save_txn  = st.form_submit_button("💾 Save Transaction")

            if save_txn and txn_sku:
                new_id = f"TXN-{random.randint(6000,9999)}"
                st.success(f"✅ Transaction **{new_id}** recorded!")
                st.code(f"""
-- PostgreSQL INSERT
INSERT INTO transactions (txn_id, date, type, sku, qty, party, amount_inr, notes)
VALUES ('{new_id}', '{txn_date}', '{txn_type}', '{txn_sku}', {txn_qty}, '{txn_party}', {txn_amount}, '{txn_notes}');

-- Redis: update cached qty
HINCRBY inventory:{txn_sku} qty {'+ ' if txn_type == 'Purchase' else '- '}{txn_qty}
PUBLISH inventory_updates "{{type:{txn_type}, sku:{txn_sku}, qty:{txn_qty}}}"
""", language="sql")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ALERTS
# ════════════════════════════════════════════════════════════════════════════
elif "Alerts" in page:

    st.markdown('<div class="section-header">🚨 Stock Alerts & Notifications</div>', unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Out of Stock <span class="kpi-icon">🚫</span></div>
            <div class="kpi-value" style="color:#F04438;">{out_count}</div>
            <div class="kpi-delta down">Immediate action needed</div>
        </div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Low Stock <span class="kpi-icon">⚠️</span></div>
            <div class="kpi-value" style="color:#F79009;">{low_count}</div>
            <div class="kpi-delta down">Below reorder level</div>
        </div>""", unsafe_allow_html=True)
    with a3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Healthy Stock <span class="kpi-icon">✅</span></div>
            <div class="kpi-value" style="color:#12B76A;">{in_stock}</div>
            <div class="kpi-delta up">No action needed</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">🚫 Out of Stock Items</div>', unsafe_allow_html=True)
    out_df = df[df["Status"]=="Out of Stock"][["SKU","Product","Category","Reorder","Supplier","Warehouse"]]
    st.dataframe(out_df, use_container_width=True, hide_index=True, height=220)

    st.markdown('<div class="section-header">⚠️ Low Stock Items</div>', unsafe_allow_html=True)
    low_df = df[df["Status"]=="Low Stock"].sort_values("Qty")[["SKU","Product","Qty","Reorder","Category","Supplier"]]
    low_df["Gap"] = low_df["Reorder"] - low_df["Qty"]

    fig_low = px.bar(low_df.head(15), x="Product", y=["Qty","Reorder"],
                     barmode="group", color_discrete_sequence=["#875BF7","#F04438"],
                     labels={"value":"Units","variable":""})
    fig_low.update_layout(
        height=280, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans"),
        xaxis=dict(showgrid=False, tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="#E9E8F5"),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_low, use_container_width=True)

    st.markdown("""
    <div class="section-header">⚡ Redis Alert Stream (Live)</div>
    <div style="background:#1A1523;border-radius:12px;padding:1rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#C9C4D4;line-height:1.8;">
        <span style="color:#12B76A;">✓</span> [14:32:07] ALERT: SKU-1005 (Rubber Gasket) → Out of Stock · Redis key: <span style="color:#875BF7;">inventory:SKU-1005</span><br>
        <span style="color:#F79009;">⚠</span> [14:31:54] ALERT: SKU-1018 (V-Belt A45) → Low Stock (qty=8, reorder=25)<br>
        <span style="color:#12B76A;">✓</span> [14:30:22] CACHE HIT: SKU-1002 fetched from Redis in 0.4ms<br>
        <span style="color:#F04438;">✗</span> [14:29:11] ALERT: SKU-1031 → Qty dropped below reorder level<br>
        <span style="color:#0BA5EC;">ℹ</span> [14:28:05] Pub/Sub: inventory_updates channel — 3 subscribers<br>
        <span style="color:#12B76A;">✓</span> [14:27:44] PostgreSQL → Redis cache refreshed for 12 SKUs
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS
# ════════════════════════════════════════════════════════════════════════════
elif "Reports" in page:

    st.markdown('<div class="section-header">📊 Inventory Reports</div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)

    with r1:
        # Top 10 by value
        top10 = df.nlargest(10, "Stock_Value")[["Product","Category","Qty","Stock_Value"]]
        fig_t = px.bar(top10, x="Stock_Value", y="Product", orientation="h",
                       color="Category", color_discrete_sequence=["#875BF7","#F79009","#0BA5EC","#12B76A","#F04438"],
                       labels={"Stock_Value":"Value (₹)","Product":""})
        fig_t.update_layout(
            title="Top 10 Products by Stock Value",
            title_font=dict(size=13,family="Plus Jakarta Sans"),
            height=340, margin=dict(l=0,r=0,t=35,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
            legend=dict(orientation="h", y=-0.18, font=dict(size=10)),
            xaxis=dict(showgrid=True,gridcolor="#E9E8F5"), yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with r2:
        # Supplier distribution
        sup_val = df.groupby("Supplier")["Stock_Value"].sum().reset_index()
        fig_s = px.pie(sup_val, names="Supplier", values="Stock_Value", hole=0.5,
                       color_discrete_sequence=["#875BF7","#F79009","#0BA5EC","#12B76A","#F04438"])
        fig_s.update_traces(textinfo="percent+label", textfont_size=10)
        fig_s.update_layout(
            title="Stock Value by Supplier",
            title_font=dict(size=13,family="Plus Jakarta Sans"),
            height=340, margin=dict(l=0,r=0,t=35,b=0),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            font=dict(family="Plus Jakarta Sans"),
        )
        st.plotly_chart(fig_s, use_container_width=True)

    # ABC Analysis
    st.markdown('<div class="section-header">🔠 ABC Analysis</div>', unsafe_allow_html=True)
    abc = df.copy().sort_values("Stock_Value", ascending=False)
    abc["Cumulative_%"] = (abc["Stock_Value"].cumsum() / abc["Stock_Value"].sum() * 100).round(1)
    abc["ABC"] = abc["Cumulative_%"].apply(lambda x: "A" if x<=70 else ("B" if x<=90 else "C"))

    ac1, ac2 = st.columns([1.3, 1])
    with ac1:
        fig_abc = go.Figure()
        for cls, col in [("A","#875BF7"),("B","#F79009"),("C","#12B76A")]:
            d = abc[abc["ABC"]==cls]
            fig_abc.add_trace(go.Bar(x=d["Product"][:6], y=d["Stock_Value"][:6], name=f"Class {cls}", marker_color=col))
        fig_abc.update_layout(
            barmode="group", height=260, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=False,tickangle=-30), yaxis=dict(showgrid=True,gridcolor="#E9E8F5"),
            legend=dict(orientation="h",y=1.15,font=dict(size=11)),
        )
        st.plotly_chart(fig_abc, use_container_width=True)

    with ac2:
        abc_sum = abc.groupby("ABC").agg(Count=("SKU","count"), TotalValue=("Stock_Value","sum")).reset_index()
        abc_sum["TotalValue"] = abc_sum["TotalValue"].apply(lambda x: f"₹{x:,.0f}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(abc_sum, use_container_width=True, hide_index=True, height=180)
        st.caption("A: Top 70% value · B: Next 20% · C: Bottom 10%")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ════════════════════════════════════════════════════════════════════════════
elif "Settings" in page:

    st.markdown('<div class="section-header">⚙️ System Configuration</div>', unsafe_allow_html=True)

    st1, st2 = st.columns(2)

    with st1:
        st.markdown("**🐘 PostgreSQL Configuration**")
        with st.form("pg_form"):
            pg_host = st.text_input("Host", value="localhost")
            pg_port = st.number_input("Port", value=5432)
            pg_db   = st.text_input("Database", value="msme_inventory")
            pg_user = st.text_input("Username", value="postgres")
            pg_pass = st.text_input("Password", type="password", value="••••••••")
            if st.form_submit_button("🔗 Test Connection"):
                st.success("✅ PostgreSQL connection successful! (mock)")

        st.markdown("**⚡ Redis Configuration**")
        with st.form("redis_form"):
            r_host = st.text_input("Redis Host", value="localhost")
            r_port = st.number_input("Redis Port", value=6379)
            r_db   = st.number_input("Redis DB Index", value=0)
            r_pass = st.text_input("Redis Password", type="password")
            r_ttl  = st.number_input("Cache TTL (seconds)", value=3600, min_value=60)
            if st.form_submit_button("🔗 Test Redis Connection"):
                st.success("✅ Redis PONG received! Latency: 0.3ms (mock)")

    with st2:
        st.markdown("**🏭 Business Settings**")
        with st.form("biz_form"):
            biz_name  = st.text_input("Business Name", value="Gupta Fasteners Pvt Ltd")
            gstin     = st.text_input("GSTIN", value="07AAACG1234F1Z5")
            currency  = st.selectbox("Currency", ["INR ₹", "USD $", "EUR €"])
            fin_year  = st.selectbox("Financial Year Start", ["April", "January"])
            low_thresh= st.number_input("Global Low Stock Threshold (%)", value=30, min_value=5, max_value=100)
            email_alert= st.text_input("Alert Email", value="owner@guptafasteners.com")
            if st.form_submit_button("💾 Save Settings"):
                st.success("✅ Settings saved to PostgreSQL config table.")

        st.markdown("**📦 Database Schema Info**")
        st.code("""
-- PostgreSQL Tables
CREATE TABLE inventory (
  sku         TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  category    TEXT,
  qty         INTEGER DEFAULT 0,
  unit        TEXT,
  price_inr   NUMERIC(12,2),
  reorder_lvl INTEGER DEFAULT 20,
  warehouse   TEXT,
  supplier    TEXT,
  updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
  txn_id     TEXT PRIMARY KEY,
  date       DATE,
  type       TEXT,
  sku        TEXT REFERENCES inventory(sku),
  qty        INTEGER,
  party      TEXT,
  amount_inr NUMERIC(12,2),
  notes      TEXT
);

-- Redis Key Patterns
-- inventory:{sku}   → HASH  (real-time qty cache)
-- alerts:low_stock  → SET   (SKUs below reorder)
-- session:{user_id} → HASH  (user session)
-- inventory_updates → PubSub channel
""", language="sql")
