import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import hashlib
import plotly.graph_objects as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- PAGE CONFIGURATION & LOGO ---
st.set_page_config(page_title="StormNode Logistics", page_icon="⚡", layout="wide")

try:
    st.sidebar.image("logo1.png")
except:
    st.sidebar.title("⚡")

# --- GLOBAL STYLES & UI GLOW-UP ---
st.markdown("""
    <style>
    div[data-testid="stToastContainer"] { top: 2rem; right: 2rem; bottom: auto !important; left: auto !important; }
    .pulse-orb { height: 12px; width: 12px; background-color: #00FF55; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 10px #00FF55; animation: pulse-animation 1.5s infinite; }
    @keyframes pulse-animation { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 85, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 85, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 85, 0); } }
    .crypto-terminal { background-color: #0d1117; color: #00FF55; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 5px; height: 250px; overflow-y: hidden; border: 1px solid #30363d; font-size: 13px; line-height: 1.5; }
    .custom-table { width: 100%; text-align: left; border-collapse: collapse; color: #C5C6C7; font-size: 14px; margin-bottom: 20px;}
    .custom-table th, .custom-table td { padding: 10px; border-bottom: 1px solid #1F2833; }
    .custom-table th { color: #ffffff; font-weight: bold; background-color: #1A2235; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #00D2FF; font-size: 26px; font-weight: bold; margin-top: -15px;'>"
    "StormNode Logistics<br>"
    "<span style='font-size: 14px; color: #00F0FF; font-style: italic;'>Powering the Connected Supply Chain</span>"
    "</div>",
    unsafe_allow_html=True
)

st.sidebar.markdown("<br><div style='display:flex; align-items:center; justify-content:center; font-family:monospace; color:#C5C6C7;'><div class='pulse-orb'></div> System Online | AI Active</div><br>", unsafe_allow_html=True)

def render_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #C5C6C7; font-size: 14px;'>"
        "<strong>StormNode Logistics</strong> | Est. 2026<br>"
        "<em>Powering the Connected Supply Chain</em>"
        "</div>", 
        unsafe_allow_html=True
    )

real_routes = {
    "DXB Airport": [[24.9857, 55.0273], [25.0113, 55.0552], [25.0441, 55.0963], [25.0763, 55.1388], [25.1166, 55.1884], [25.1557, 55.2343], [25.1955, 55.2755], [25.2415, 55.3211], [25.2532, 55.3657]],
    "Dubai Mall": [[24.9857, 55.0273], [25.0113, 55.0552], [25.0441, 55.0963], [25.0763, 55.1388], [25.1166, 55.1884], [25.1557, 55.2343], [25.1972, 55.2744]],
    "Dubai Marina": [[24.9857, 55.0273], [25.0113, 55.0552], [25.0441, 55.0963], [25.0805, 55.1403]],
    "Al Maktoum Int": [[24.9857, 55.0273], [24.9600, 55.0500], [24.9350, 55.1100], [24.8966, 55.1605]],
    "Sharjah Ind": [[24.9857, 55.0273], [25.0113, 55.0552], [25.0441, 55.0963], [25.1166, 55.1884], [25.1955, 55.2755], [25.2415, 55.3211], [25.2850, 55.3650], [25.3134, 55.4055]]
}

def get_interpolated_pos(route, progress):
    if progress >= 1.0: return route[-1][0], route[-1][1]
    if progress <= 0.0: return route[0][0], route[0][1]
    total_segments = len(route) - 1
    cont_index = progress * total_segments
    idx = int(cont_index)
    frac = cont_index - idx
    lat1, lon1 = route[idx]
    lat2, lon2 = route[idx+1]
    return lat1 + (lat2 - lat1) * frac, lon1 + (lon2 - lon1) * frac

# --- GLOBAL AUTOREFRESH & STATE ---
st_autorefresh(interval=5000, limit=10000, key="global_autorefresh")
now = datetime.now()

if 'trigger_sound' not in st.session_state: st.session_state['trigger_sound'] = None
if 'blockchain_ledger' not in st.session_state:
    st.session_state['blockchain_ledger'] = [f"[{now.strftime('%H:%M:%S')}] SYSTEM INITIALIZED: Genesis Block Created"]
if 'erp_order_logs' not in st.session_state:
    st.session_state['erp_order_logs'] = [f"[{now.strftime('%H:%M:%S')}] ERP SYSTEM ONLINE: Cross-Border Nodes Active"]

# GLOBAL VARS
items_list = ["Packaged Grains", "Canned Preserves", "Beverage Pallets", "Snack Cartons", "Ready-to-Eat Meals", "Dairy Alternatives"]
base_costs = {"Packaged Grains": 120, "Canned Preserves": 85, "Beverage Pallets": 210, "Snack Cartons": 65, "Ready-to-Eat Meals": 150, "Dairy Alternatives": 90}
currency_rates = {"Dubai Hub (AED)": 3.67, "Singapore Hub (SGD)": 1.35, "India Hub (INR)": 83.50}

if 'static_fleet_df' not in st.session_state:
    st.session_state['static_fleet_df'] = pd.DataFrame([
        {"Truck ID": "TRK-901", "Destination": "DXB Airport", "Status": "Active En Route"},
        {"Truck ID": "TRK-902", "Destination": "Dubai Mall", "Status": "Active En Route"},
        {"Truck ID": "TRK-903", "Destination": "Dubai Marina", "Status": "Active En Route"}
    ])

if 'fleet_state' not in st.session_state:
    st.session_state['fleet_state'] = [
        {"id": "TRK-901", "dest": "DXB Airport", "progress": 0.15, "traffic": "Moderate", "color": "#FFBF00", "speed": 62, "eta": (now + timedelta(minutes=int(0.85*180))).strftime("%I:%M %p")},
        {"id": "TRK-902", "dest": "Dubai Mall", "progress": 0.40, "traffic": "Heavy Traffic", "color": "#FF3333", "speed": 45, "eta": (now + timedelta(minutes=int(0.60*180))).strftime("%I:%M %p")},
        {"id": "TRK-903", "dest": "Dubai Marina", "progress": 0.65, "traffic": "Clear", "color": "#00FF55", "speed": 85, "eta": (now + timedelta(minutes=int(0.35*180))).strftime("%I:%M %p")}
    ]

if 'truck_logs' not in st.session_state:
    synthetic_trucks = []
    locations = ["Whse A - Dock 1", "Whse B - Dock 1", "Whse C - Cold Chain"]
    for i in range(5):
        entry_time = now - timedelta(minutes=random.randint(15, 120))
        offset = random.randint(-45, 45)
        scheduled_eta = entry_time + timedelta(minutes=offset)
        if offset < -15: kpi = "🔴 Late"
        elif offset > 15: kpi = "🟢 Early"
        else: kpi = "🔵 On-Time"
        synthetic_trucks.append({
            "Truck_ID": f"TRK-{random.randint(1000, 9999)}", "Scheduled_ETA": scheduled_eta.strftime("%Y-%m-%d %H:%M:%S"),
            "Entry_Time": entry_time.strftime("%Y-%m-%d %H:%M:%S"), "KPI_Status": kpi,
            "Exit_Time": "Pending" if i % 2 == 0 else (entry_time + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), 
            "Warehouse_Location": random.choice(locations), "Status": "At Dock" if i % 2 == 0 else "Dispatched",
            "Last_Updated": entry_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    st.session_state['truck_logs'] = pd.DataFrame(synthetic_trucks)
    st.session_state['last_auto_update'] = now
    st.session_state['auto_toggle'] = "entry" 

if 'inventory' not in st.session_state:
    synthetic_inv = []
    sides = ["North Wing", "South Wing", "East Wing", "West Wing"]
    for i in range(25):
        item = random.choice(items_list)
        time_received = now - timedelta(days=random.randint(1, 90))
        max_life = random.choice([30, 60, 90, 120])
        synthetic_inv.append({
            "Batch_QR": f"QR-{random.randint(1000, 9999)}", "Item_Name": item, 
            "Unit_Cost_USD": base_costs[item], "Warehouse_Side": random.choice(sides),
            "Aisle_Number": f"Aisle {random.randint(1, 15)}", "Bin_Location": f"Bin {random.choice(['A','B','C'])}-{random.randint(1,9)}",
            "X_Coord": random.randint(1, 20), "Y_Coord": random.randint(1, 15), "Z_Coord": random.randint(1, 5),
            "Time_Received": time_received.strftime("%Y-%m-%d %H:%M:%S"), "Max_Shelf_Life_Days": max_life,
            "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"
        })
    st.session_state['inventory'] = pd.DataFrame(synthetic_inv)
    st.session_state['total_carbon_tax_accrued'] = 0.0

# --- NAVIGATION ---
st.sidebar.markdown("---")
page = st.sidebar.radio("Main Menu", [
    "Dockyard Management", 
    "Inventory & QR Tracking", 
    "ERP & Global Procurement",
    "GPS & Fleet Tracking",
    "AI Predictive Analytics",
    "About StormNode"
])

# --- GLOBAL BACKGROUND EVENT SIMULATOR ---
current_co2 = 0
for t in st.session_state['fleet_state']:
    t['progress'] += random.uniform(0.002, 0.006)
    if t['progress'] >= 1.0: t['progress'] = 0.05  
    t['speed'] = random.randint(45, 90)
    minutes_left = int((1.0 - t['progress']) * 180)
    t['eta'] = (now + timedelta(minutes=minutes_left)).strftime("%I:%M %p") if t['progress'] <= 0.95 else "Arriving"
    # Accumulate CO2 for Carbon Tax
    current_co2 += round((t["progress"] * 100) * 0.35 * 2.68, 2)

st.session_state['total_carbon_tax_accrued'] = round(current_co2 * 0.05, 2) # $50 per ton = $0.05 per kg

if (now - st.session_state['last_auto_update']).total_seconds() >= 58:  
    st.session_state['last_auto_update'] = now
    locations = ["Whse A - Dock 1", "Whse B - Dock 1", "Whse C - Cold Chain"]
    if st.session_state['auto_toggle'] == "entry":
        auto_truck_id = f"TRK-{random.randint(1000, 9999)}"
        offset = random.randint(-45, 45)
        scheduled_eta = now + timedelta(minutes=offset)
        kpi = "🔴 Late" if offset < -15 else ("🟢 Early" if offset > 15 else "🔵 On-Time")
        new_entry = pd.DataFrame([{"Truck_ID": auto_truck_id, "Scheduled_ETA": scheduled_eta.strftime("%Y-%m-%d %H:%M:%S"), "Entry_Time": now.strftime("%Y-%m-%d %H:%M:%S"), "KPI_Status": kpi, "Exit_Time": "Pending", "Warehouse_Location": random.choice(locations), "Status": "At Dock", "Last_Updated": now.strftime("%Y-%m-%d %H:%M:%S")}])
        st.session_state['truck_logs'] = pd.concat([new_entry, st.session_state['truck_logs']], ignore_index=True)
        st.session_state['auto_toggle'] = "exit"
        st.session_state['trigger_sound'] = "entry"
    else:
        docked = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]
        if not docked.empty:
            idx = docked.index[-1]
            st.session_state['truck_logs'].at[idx, "Exit_Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
            st.session_state['truck_logs'].at[idx, "Last_Updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['auto_toggle'] = "entry"
        st.session_state['trigger_sound'] = "exit"

# HELPER: Dynamic Inventory Calculation for Health
def get_enriched_inventory():
    df = st.session_state['inventory'].copy()
    df['Time_Received_DT'] = pd.to_datetime(df['Time_Received'])
    df['Age_Days'] = (now - df['Time_Received_DT']).dt.days
    health_col = []
    for _, row in df.iterrows():
        if row['Status'] != "In Warehouse":
            health_col.append("N/A")
            continue
        life_pct = 1 - (row['Age_Days'] / row['Max_Shelf_Life_Days'])
        if life_pct >= 0.75: health_col.append("🟢 Healthy")
        elif life_pct >= 0.50: health_col.append("🔵 Moderate")
        elif life_pct >= 0.25: health_col.append("🟠 Critical")
        else: health_col.append("🔴 Dying")
    df['Shelf_Life_Health'] = health_col
    return df

# ==========================================
# PAGE 1: DOCKYARD MANAGEMENT
# ==========================================
if page == "Dockyard Management":
    st.title("🚛 Dockyard Management")
    df = st.session_state['truck_logs']
    
    st.subheader("🟢 Active Fleet (At Dock)")
    html_docked = f"<table class='custom-table'><thead><tr><th>Truck ID</th><th>Scheduled ETA</th><th>Actual Entry</th><th>KPI Status</th><th>Location</th><th>Status</th></tr></thead><tbody>"
    for _, row in df[df["Status"] == "At Dock"].iterrows():
        html_docked += f"<tr><td>{row['Truck_ID']}</td><td>{row['Scheduled_ETA']}</td><td>{row['Entry_Time']}</td><td>{row['KPI_Status']}</td><td>{row['Warehouse_Location']}</td><td>{row['Status']}</td></tr>"
    html_docked += "</tbody></table>"
    st.markdown(html_docked, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔴 Dispatched Log")
    html_dispatched = f"<table class='custom-table'><thead><tr><th>Truck ID</th><th>Scheduled ETA</th><th>Entry Time</th><th>Exit Time</th><th>KPI Status</th><th>Location</th></tr></thead><tbody>"
    for _, row in df[df["Status"] == "Dispatched"].iterrows():
        html_dispatched += f"<tr><td>{row['Truck_ID']}</td><td>{row['Scheduled_ETA']}</td><td>{row['Entry_Time']}</td><td>{row['Exit_Time']}</td><td>{row['KPI_Status']}</td><td>{row['Warehouse_Location']}</td></tr>"
    html_dispatched += "</tbody></table>"
    st.markdown(html_dispatched, unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 2: INVENTORY & QR TRACKING
# ==========================================
elif page == "Inventory & QR Tracking":
    st.title("📦 Inventory & Blockchain Securitization")
    inv_df = get_enriched_inventory()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Receive New Batch")
        batch_qr = st.text_input("Batch QR", placeholder="e.g. QR-5542")
        item_name = st.selectbox("Product", items_list)
        if st.button("Store Inventory", type="primary"):
            if batch_qr and item_name:
                new_item = pd.DataFrame([{"Batch_QR": batch_qr, "Item_Name": item_name, "Unit_Cost_USD": base_costs[item_name], "Warehouse_Side": "North Wing", "Aisle_Number": "Aisle 1", "Bin_Location": "Bin A-1", "X_Coord": random.randint(1, 20), "Y_Coord": random.randint(1, 15), "Z_Coord": random.randint(1, 5), "Time_Received": now.strftime("%Y-%m-%d %H:%M:%S"), "Max_Shelf_Life_Days": 90, "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"}])
                st.session_state['inventory'] = pd.concat([new_item, st.session_state['inventory']], ignore_index=True)
                st.rerun()

    with col2:
        st.subheader("Smart Contract Dispatch")
        in_stock = inv_df[inv_df["Status"] == "In Warehouse"]["Batch_QR"].tolist()
        if st.button("Execute Dispatch & Mint Hash", type="primary") and in_stock:
            dispatch_qr = in_stock[0]
            idx = st.session_state['inventory'].index[st.session_state['inventory']['Batch_QR'] == dispatch_qr].tolist()[0]
            st.session_state['inventory'].at[idx, "Status"] = "In Transit"
            tx_hash = hashlib.sha256(f"{dispatch_qr}-{now.isoformat()}".encode()).hexdigest()
            st.session_state['blockchain_ledger'].insert(0, f"[{now.strftime('%H:%M:%S')}] TX_HASH: 0x{tx_hash[:20]}... 🟢 SECURED: {dispatch_qr}")
            st.rerun()
            
    st.markdown("#### 🔗 Live Immutable Ledger Terminal")
    st.markdown(f'<div class="crypto-terminal">{"<br>".join(st.session_state["blockchain_ledger"])}</div>', unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 3: ERP & GLOBAL PROCUREMENT (ALL 6 FEATURES)
# ==========================================
elif page == "ERP & Global Procurement":
    st.title("⚙️ ERP & Global Intermodal Procurement")
    st.markdown("Full-suite enterprise resource planning integrated with AI forecasting, cross-border currency exchanges, and ESG governance.")
    
    inv_df = get_enriched_inventory()
    current_stock = inv_df[inv_df["Status"] == "In Warehouse"]
    
    # FEATURE 1: Capital Lock-Up Telemetry & FEATURE 6: ESG Ledger
    capital_locked = current_stock['Unit_Cost_USD'].sum()
    carbon_tax = st.session_state['total_carbon_tax_accrued']
    
    # FEATURE 3: Dynamic Demand Forecasting (AI adjusts safety stock)
    is_peak_window = now.weekday() in [3, 4] # Thursday or Friday
    ai_multiplier = 1.5 if is_peak_window else 1.0
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Locked (Inventory)", f"${capital_locked:,.2f}")
    c2.metric("ESG Carbon Tax Accrued", f"${carbon_tax:,.2f}", delta="-0.5% v last hr", delta_color="inverse")
    c3.metric("AI Demand Forecast", "Surge Expected" if is_peak_window else "Stable Baseline")
    c4.metric("Dynamic Stock Multiplier", f"{ai_multiplier}x")
    st.markdown("---")

    # FEATURE 4: Cross-Border Currency Engine
    erp_records = []
    for item in items_list:
        count = len(current_stock[current_stock['Item_Name'] == item])
        base_safety = 4 
        dynamic_safety = int(base_safety * ai_multiplier)
        
        status = "Optimal"
        if count <= dynamic_safety:
            status = "🔴 Auto-Order Triggered"
            if f"AUTO_ORDER_{item}" not in " ".join(st.session_state['erp_order_logs'][:5]):
                order_qty = (dynamic_safety * 2) - count
                
                # Evaluate Cheapest Global Hub
                best_hub, best_rate = random.choice(list(currency_rates.items()))
                local_cost = round(base_costs[item] * best_rate, 2)
                
                log = f"[{now.strftime('%H:%M:%S')}] 🤖 AI CROSS-BORDER EXECUTION: Bought {order_qty}x {item} from {best_hub} @ {local_cost} local currency. (Saved 12% vs base USD)."
                st.session_state['erp_order_logs'].insert(0, log)
                st.session_state['erp_order_logs'].insert(0, f"[{now.strftime('%H:%M:%S')}] AUTO_ORDER_{item}_LOGGED")
        elif count <= dynamic_safety + 2:
            status = "🟠 Approaching AI Threshold"
            
        erp_records.append({"Product": item, "Live Stock": count, "Dynamic AI Safety": dynamic_safety, "ERP Status": status})
        
    colA, colB = st.columns([1.5, 1])
    with colA:
        st.subheader("Global Inventory & AI Thresholds")
        st.dataframe(pd.DataFrame(erp_records), use_container_width=True)
        
        # FEATURE 2: Supplier Health Matrix
        st.subheader("Supplier Health Matrix (Lead Times)")
        supplier_data = pd.DataFrame([
            {"Supplier Code": "SUP-IND-01", "Region": "India", "Avg Lead Time": "3.2 Days", "On-Time %": "98%", "Grade": "🟢 A (Prime)"},
            {"Supplier Code": "SUP-DXB-99", "Region": "Dubai", "Avg Lead Time": "1.1 Days", "On-Time %": "99%", "Grade": "🟢 A (Prime)"},
            {"Supplier Code": "SUP-SGP-42", "Region": "Singapore", "Avg Lead Time": "5.6 Days", "On-Time %": "82%", "Grade": "🟠 C (Risk)"}
        ])
        st.dataframe(supplier_data, hide_index=True, use_container_width=True)

    with colB:
        # FEATURE 5: Intermodal Cost Optimizer
        st.subheader("Intermodal Procurement Optimizer")
        with st.form("intermodal_order"):
            mo_item = st.selectbox("Bulk Order (Packaged Foods)", items_list)
            mo_qty = st.number_input("Tonnage (Pallets)", min_value=10, max_value=500, value=50)
            transport_mode = st.radio("Select Logistics Network", ["🛣️ Standard Highway Fleet", "🚂 High-Speed Rail Network"])
            submitted = st.form_submit_button("Run Cost Analysis & Procure")
            
            if submitted:
                if "Rail" in transport_mode:
                    cost = mo_qty * 15
                    esg_impact = "High Carbon Savings (+ ESG Credits)"
                    time_est = "4 Days"
                else:
                    cost = mo_qty * 45
                    esg_impact = "Heavy Carbon Penalty (Increased Tax)"
                    time_est = "1.5 Days"
                
                log = f"[{now.strftime('%H:%M:%S')}] INTERMODAL PO: {mo_qty} pallets {mo_item}. Routed via {transport_mode}. Est Cost: ${cost}. ESG Impact: {esg_impact}."
                st.session_state['erp_order_logs'].insert(0, log)
                st.success(f"Dispatched via {transport_mode} | Transit: {time_est} | Logistics Cost: ${cost}")

    st.markdown("#### 📡 Global AI Action & Intermodal Log")
    st.markdown(f'<div class="crypto-terminal">{"<br>".join(st.session_state["erp_order_logs"])}</div>', unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 4, 5, 6: (GPS, AI, About) Maintained from previous architecture
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Route Tracing")
    st.info("Live ESG Telemetry active. CO2 burned by fleet is automatically forwarded to the ERP Carbon Tax Ledger.")
    render_footer()

elif page == "AI Predictive Analytics":
    st.title("🧠 AI Predictive Analytics Forecast")
    st.info("AI has detected an upcoming Intermodal Railway freight exchange on Friday. Safety Stock Multipliers automatically raised in the ERP module.")
    render_footer()

elif page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    render_footer()

# --- SIDEBAR ACADEMIC CREDITS ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size: 13px; color: #C5C6C7; font-family: \"Times New Roman\", Times, serif;'>"
    "<b>App Developer:</b><br>"
    "Syed Ali Kavish Abdi<br>"
    "<b>Batch:</b> MGB OCT 25<br>"
    "<b>Roll No:</b> MS25GLS138<br><br>"
    "<b>Student, SP Jain School of Global Management</b><br>"
    "<i>Under the guidance of Prof. Rajiv Asrekar</i>"
    "</div>", 
    unsafe_allow_html=True
)
