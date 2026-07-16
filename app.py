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
    .scanner-box { position: relative; width: 100%; height: 60px; background: #1A2235; border: 1px solid #00D2FF; border-radius: 5px; overflow: hidden; display: flex; align-items: center; justify-content: center; color: #00D2FF; font-family: monospace; font-weight: bold; letter-spacing: 2px; }
    .scanner-laser { position: absolute; left: -100%; top: 0; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(0, 210, 255, 0.4), transparent); animation: scan 3s infinite linear; }
    @keyframes scan { 0% { left: -50%; } 100% { left: 100%; } }
    .crypto-terminal { background-color: #0d1117; color: #00FF55; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 5px; height: 250px; overflow-y: hidden; border: 1px solid #30363d; font-size: 13px; line-height: 1.5; }
    .agent-terminal { background-color: #07090e; color: #FFB300; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 5px; height: 280px; overflow-y: hidden; border: 1px solid #FFB30040; font-size: 13px; line-height: 1.6; }
    
    /* Custom Tables & Blinking Rows */
    .custom-table { width: 100%; text-align: left; border-collapse: collapse; color: #C5C6C7; font-size: 14px; margin-bottom: 20px;}
    .custom-table th, .custom-table td { padding: 10px; border-bottom: 1px solid #1F2833; }
    .custom-table th { color: #ffffff; font-weight: bold; background-color: #1A2235; }
    @keyframes flashGreen { 0% {background-color: transparent;} 50% {background-color: rgba(0, 255, 85, 0.25);} 100% {background-color: transparent;} }
    @keyframes flashRed { 0% {background-color: transparent;} 50% {background-color: rgba(255, 51, 51, 0.25);} 100% {background-color: transparent;} }
    .blink-row-green { animation: flashGreen 2s infinite; }
    .blink-row-red { animation: flashRed 2s infinite; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #00D2FF; font-size: 26px; font-weight: bold; margin-top: -15px;'>"
    "StormNode Logistics<br>"
    "<span style='font-size: 14px; color: #00F0FF; font-style: italic;'>Powering the Connected Supply Chain</span>"
    "</div>", unsafe_allow_html=True
)

st.sidebar.markdown("<br><div style='display:flex; align-items:center; justify-content:center; font-family:monospace; color:#C5C6C7;'><div class='pulse-orb'></div> System Online | AI Active</div><br>", unsafe_allow_html=True)

def render_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #C5C6C7; font-size: 14px;'>"
        "<strong>StormNode Logistics</strong> | Est. 2026<br>"
        "<em>Powering the Connected Supply Chain</em>"
        "</div>", unsafe_allow_html=True
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

# GLOBAL VARS FOR ERP
items_list = ["Packaged Grains", "Canned Preserves", "Beverage Pallets", "Snack Cartons", "Ready-to-Eat Meals", "Dairy Alternatives"]
base_costs = {"Packaged Grains": 120, "Canned Preserves": 85, "Beverage Pallets": 210, "Snack Cartons": 65, "Ready-to-Eat Meals": 150, "Dairy Alternatives": 90}
currency_rates = {"Dubai Hub (AED)": 3.67, "Singapore Hub (SGD)": 1.35, "India Hub (INR)": 83.50}

# MASSIVELY SCALED FLEET DATA
if 'static_fleet_df' not in st.session_state:
    st.session_state['static_fleet_df'] = pd.DataFrame([
        {"Truck ID": "TRK-901", "Destination": "DXB Airport", "Status": "Active En Route"},
        {"Truck ID": "TRK-902", "Destination": "Dubai Mall", "Status": "Active En Route"},
        {"Truck ID": "TRK-903", "Destination": "Dubai Marina", "Status": "Active En Route"},
        {"Truck ID": "TRK-904", "Destination": "Al Maktoum Int", "Status": "Active En Route"},
        {"Truck ID": "TRK-905", "Destination": "Sharjah Ind", "Status": "Active En Route"},
        {"Truck ID": "TRK-906", "Destination": "DXB Airport", "Status": "Active En Route"},
        {"Truck ID": "TRK-907", "Destination": "Dubai Mall", "Status": "Active En Route"},
        {"Truck ID": "TRK-908", "Destination": "Al Maktoum Int", "Status": "Active En Route"}
    ])

if 'fleet_state' not in st.session_state:
    st.session_state['fleet_state'] = [
        {"id": "TRK-901", "dest": "DXB Airport", "progress": 0.15, "traffic": "Moderate", "color": "#FFBF00", "speed": 62, "eta": (now + timedelta(minutes=int(0.85*180))).strftime("%I:%M %p")},
        {"id": "TRK-902", "dest": "Dubai Mall", "progress": 0.40, "traffic": "Heavy Traffic", "color": "#FF3333", "speed": 45, "eta": (now + timedelta(minutes=int(0.60*180))).strftime("%I:%M %p")},
        {"id": "TRK-903", "dest": "Dubai Marina", "progress": 0.65, "traffic": "Clear", "color": "#00FF55", "speed": 85, "eta": (now + timedelta(minutes=int(0.35*180))).strftime("%I:%M %p")},
        {"id": "TRK-904", "dest": "Al Maktoum Int", "progress": 0.20, "traffic": "Clear", "color": "#00FF55", "speed": 78, "eta": (now + timedelta(minutes=int(0.80*180))).strftime("%I:%M %p")},
        {"id": "TRK-905", "dest": "Sharjah Ind", "progress": 0.80, "traffic": "Moderate", "color": "#FFBF00", "speed": 55, "eta": (now + timedelta(minutes=int(0.20*180))).strftime("%I:%M %p")},
        {"id": "TRK-906", "dest": "DXB Airport", "progress": 0.35, "traffic": "Clear", "color": "#00FF55", "speed": 82, "eta": (now + timedelta(minutes=int(0.65*180))).strftime("%I:%M %p")},
        {"id": "TRK-907", "dest": "Dubai Mall", "progress": 0.10, "traffic": "Heavy Traffic", "color": "#FF3333", "speed": 35, "eta": (now + timedelta(minutes=int(0.90*180))).strftime("%I:%M %p")},
        {"id": "TRK-908", "dest": "Al Maktoum Int", "progress": 0.55, "traffic": "Moderate", "color": "#FFBF00", "speed": 60, "eta": (now + timedelta(minutes=int(0.45*180))).strftime("%I:%M %p")}
    ]

# MASSIVELY SCALED DOCKYARD LOGS
if 'truck_logs' not in st.session_state:
    synthetic_trucks = []
    locations = ["Whse A - Dock 1", "Whse A - Dock 2", "Whse A - Dock 3", "Whse B - Dock 1", "Whse B - Dock 2", "Whse C - Heavy Freight", "Whse C - Cold Chain"]
    for i in range(40):  
        entry_time = now - timedelta(minutes=random.randint(15, 300))
        offset = random.randint(-45, 45)
        scheduled_eta = entry_time + timedelta(minutes=offset)
        kpi = "🔴 Late" if offset < -15 else ("🟢 Early" if offset > 15 else "🔵 On-Time")
        synthetic_trucks.append({
            "Truck_ID": f"TRK-{random.randint(1000, 9999)}", "Scheduled_ETA": scheduled_eta.strftime("%Y-%m-%d %H:%M:%S"),
            "Entry_Time": entry_time.strftime("%Y-%m-%d %H:%M:%S"), "KPI_Status": kpi,
            "Exit_Time": "Pending" if i % 3 == 0 else (entry_time + timedelta(minutes=random.randint(30, 90))).strftime("%Y-%m-%d %H:%M:%S"), 
            "Warehouse_Location": random.choice(locations), "Status": "At Dock" if i % 3 == 0 else "Dispatched",
            "Last_Updated": entry_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    st.session_state['truck_logs'] = pd.DataFrame(synthetic_trucks)
    st.session_state['last_auto_update'] = now
    st.session_state['auto_toggle'] = "entry" 

# MASSIVELY SCALED INVENTORY
if 'inventory' not in st.session_state:
    synthetic_inv = []
    sides = ["North Wing", "South Wing", "East Wing", "West Wing"]
    for i in range(120): 
        item = random.choice(items_list)
        time_received = now - timedelta(days=random.randint(1, 90))
        max_life = random.choice([30, 60, 90, 120])
        synthetic_inv.append({
            "Batch_QR": f"QR-{random.randint(1000, 9999)}", "Item_Name": item, 
            "Unit_Cost_USD": base_costs[item], "Warehouse_Side": random.choice(sides),
            "Aisle_Number": f"Aisle {random.randint(1, 15)}", "Bin_Location": f"Bin {random.choice(['A','B','C','D','E'])}",
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

# --- GLOBAL BACKGROUND EVENT SIMULATOR (NOTIFICATIONS RESTORED) ---
current_co2 = 0
for t in st.session_state['fleet_state']:
    t['progress'] += random.uniform(0.002, 0.006)
    if t['progress'] >= 1.0: t['progress'] = 0.05  
    t['speed'] = random.randint(45, 90)
    minutes_left = int((1.0 - t['progress']) * 180)
    t['eta'] = (now + timedelta(minutes=minutes_left)).strftime("%I:%M %p") if t['progress'] <= 0.95 else "Arriving"
    current_co2 += round((t["progress"] * 100) * 0.35 * 2.68, 2)

st.session_state['total_carbon_tax_accrued'] = round(current_co2 * 0.05, 2)

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
        st.toast(f"📡 Computer Vision: {auto_truck_id} plate scanned at main gate.", icon="🟢")
    else:
        docked = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]
        t_id = "Unknown"
        if not docked.empty:
            idx = docked.index[-1]
            t_id = st.session_state['truck_logs'].at[idx, "Truck_ID"]
            st.session_state['truck_logs'].at[idx, "Exit_Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
            st.session_state['truck_logs'].at[idx, "Last_Updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['auto_toggle'] = "entry"
        st.session_state['trigger_sound'] = "exit"
        if t_id != "Unknown":
            st.toast(f"📡 Fleet Update: {t_id} departed.", icon="🔴")

audio_tag = ""
if st.session_state['trigger_sound'] == "entry":
    audio_tag = f"""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2573/2573-preview.mp3?t={time.time()}" type="audio/mpeg"></audio>"""
    st.session_state['trigger_sound'] = None
elif st.session_state['trigger_sound'] == "exit":
    audio_tag = f"""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2574/2574-preview.mp3?t={time.time()}" type="audio/mpeg"></audio>"""
    st.session_state['trigger_sound'] = None

if audio_tag:
    st.markdown(audio_tag, unsafe_allow_html=True)

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
# PAGE 1: DOCKYARD MANAGEMENT (BLINKING ROWS RESTORED)
# ==========================================
if page == "Dockyard Management":
    st.title("🚛 Dockyard Management")
    st.markdown("Automated gate sensors, real-time dispatch control, and high-volume KPI tracking.")
    
    df = st.session_state['truck_logs']
    latest_update = df.sort_values(by="Last_Updated", ascending=False).iloc[0]
    last_time = datetime.strptime(latest_update['Last_Updated'], "%Y-%m-%d %H:%M:%S")
    time_since = int((now - last_time).total_seconds())
    
    if latest_update['Status'] == "At Dock":
        msg = f"ENTRY SCANNED: {latest_update['Truck_ID']} | BAY: {latest_update['Warehouse_Location']}"
        b_color = "#00FF55"
    else:
        msg = f"EXIT SCANNED: {latest_update['Truck_ID']} | DISPATCH ROUTED"
        b_color = "#FF3333"
        
    scanner_html = f"""
    <div style="position: relative; width: 100%; height: 60px; background: #1A2235; 
         border: 2px solid {b_color}; border-radius: 5px; overflow: hidden;
         display: flex; align-items: center; justify-content: space-between; padding: 0 20px; color: {b_color};
         font-family: monospace; font-size: 15px; font-weight: bold; letter-spacing: 1px;
         box-shadow: 0 0 15px {b_color}40;">
        <div style="z-index: 2;">[LIVE AI GATE] ⚡ {msg}</div>
        <div style="z-index: 2;">TIME SINCE SCAN: {time_since}s</div>
        <div class="scanner-laser"></div>
    </div>
    <br>
    """
    st.markdown(scanner_html, unsafe_allow_html=True)
    
    st.subheader(f"🟢 Active Fleet at Dock ({len(df[df['Status'] == 'At Dock'])} Units)")
    html_docked = f"<table class='custom-table'><thead><tr><th>Truck ID</th><th>Scheduled ETA</th><th>Actual Entry</th><th>KPI Status</th><th>Location</th><th>Status</th></tr></thead><tbody>"
    for i, (_, row) in enumerate(df[df["Status"] == "At Dock"].iterrows()):
        row_class = "blink-row-green" if i == 0 else ""
        html_docked += f"<tr class='{row_class}'><td>{row['Truck_ID']}</td><td>{row['Scheduled_ETA']}</td><td>{row['Entry_Time']}</td><td>{row['KPI_Status']}</td><td>{row['Warehouse_Location']}</td><td>{row['Status']}</td></tr>"
    html_docked += "</tbody></table>"
    st.markdown(html_docked, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"🔴 Historical Dispatched Log ({len(df[df['Status'] == 'Dispatched'])} Units)")
    html_dispatched = f"<div style='max-height: 400px; overflow-y: auto;'><table class='custom-table'><thead><tr><th>Truck ID</th><th>Scheduled ETA</th><th>Entry Time</th><th>Exit Time</th><th>KPI Status</th><th>Location</th></tr></thead><tbody>"
    for i, (_, row) in enumerate(df[df["Status"] == "Dispatched"].iterrows()):
        row_class = "blink-row-red" if i == 0 else ""
        html_dispatched += f"<tr class='{row_class}'><td>{row['Truck_ID']}</td><td>{row['Scheduled_ETA']}</td><td>{row['Entry_Time']}</td><td>{row['Exit_Time']}</td><td>{row['KPI_Status']}</td><td>{row['Warehouse_Location']}</td></tr>"
    html_dispatched += "</tbody></table></div>"
    st.markdown(html_dispatched, unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 2: INVENTORY & QR TRACKING
# ==========================================
elif page == "Inventory & QR Tracking":
    st.title("📦 Inventory & Blockchain Securitization")
    st.markdown("Pinpoint exact batch locations, monitor shelf-life degradation, and secure dispatches to an immutable ledger.")
    
    inv_df = get_enriched_inventory()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Receive New Batch")
        batch_qr = st.text_input("Batch QR", placeholder="e.g. QR-5542")
        item_name = st.selectbox("Product", items_list)
        side = st.selectbox("Warehouse Side", ["North Wing", "South Wing", "East Wing", "West Wing"])
        aisle = st.text_input("Aisle Number", placeholder="e.g. Aisle 5")
        bin_loc = st.text_input("Bin Location", placeholder="e.g. Bin B-2")
        max_shelf_life = st.number_input("Max Shelf Life (Days)", min_value=1, value=90)
        
        if st.button("Store Inventory", type="primary"):
            if batch_qr and item_name:
                new_item = pd.DataFrame([{
                    "Batch_QR": batch_qr, "Item_Name": item_name, "Unit_Cost_USD": base_costs[item_name], "Warehouse_Side": side,
                    "Aisle_Number": aisle, "Bin_Location": bin_loc,
                    "X_Coord": random.randint(1, 20), "Y_Coord": random.randint(1, 15), "Z_Coord": random.randint(1, 5),
                    "Time_Received": now.strftime("%Y-%m-%d %H:%M:%S"), 
                    "Max_Shelf_Life_Days": max_shelf_life,
                    "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"
                }])
                st.session_state['inventory'] = pd.concat([new_item, st.session_state['inventory']], ignore_index=True)
                st.success(f"Stored {batch_qr} at {side} > {aisle} > {bin_loc}.")
                st.session_state['trigger_sound'] = "entry"
                st.rerun()

    with col2:
        st.subheader("Smart Contract Dispatch")
        in_stock = inv_df[inv_df["Status"] == "In Warehouse"]["Batch_QR"].tolist()
        docked_df = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]
        available_trucks = docked_df["Truck_ID"].tolist()
        
        if in_stock:
            dispatch_qr = st.selectbox("Select Batch QR to Dispatch", ["Select"] + in_stock)
            if available_trucks:
                st.info(f"🚚 Valid Transporters at Dock: **{', '.join(available_trucks)}**")
            else:
                st.warning("⚠️ No physical transporters detected at gates.")
                
            dispatch_truck = st.text_input("Execute Contract: Assign to Truck ID")
            if st.button("Execute Dispatch & Mint Hash", type="primary"):
                if dispatch_qr != "Select" and dispatch_truck:
                    if dispatch_truck not in available_trucks:
                        st.error(f"❌ Invalid Transport Protocol: '{dispatch_truck}' is not currently at the dock.")
                    else:
                        idx = st.session_state['inventory'].index[st.session_state['inventory']['Batch_QR'] == dispatch_qr].tolist()[0]
                        st.session_state['inventory'].at[idx, "Time_Dispatched"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state['inventory'].at[idx, "Dispatched_On_Truck"] = dispatch_truck
                        st.session_state['inventory'].at[idx, "Status"] = "In Transit"
                        
                        t_idx = st.session_state['truck_logs'].index[st.session_state['truck_logs']['Truck_ID'] == dispatch_truck].tolist()[0]
                        st.session_state['truck_logs'].at[t_idx, "Exit_Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state['truck_logs'].at[t_idx, "Status"] = "Dispatched"
                        st.session_state['truck_logs'].at[t_idx, "Last_Updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        
                        raw_data = f"{dispatch_qr}-{dispatch_truck}-{now.isoformat()}"
                        tx_hash = hashlib.sha256(raw_data.encode()).hexdigest()
                        log_entry = f"[{now.strftime('%H:%M:%S')}] TX_HASH: 0x{tx_hash[:20]}... 🟢 SECURED: {dispatch_qr} -> {dispatch_truck}"
                        st.session_state['blockchain_ledger'].insert(0, log_entry)
                        st.success(f"✅ Cryptographic Contract Executed. Load secured.")
                        st.session_state['trigger_sound'] = "exit"
                        st.rerun()

    st.markdown("#### 🔗 Live Immutable Ledger Terminal")
    ledger_content = "<br>".join(st.session_state['blockchain_ledger'])
    st.markdown(f'<div class="crypto-terminal">{ledger_content}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

    st.subheader(f"🟦 3D Warehouse Digital Twin ({len(inv_df[inv_df['Status'] == 'In Warehouse'])} Pallets)")
    st.markdown("Interactive 3D scatter matrix mirroring physical storage architecture. **Click and drag to rotate.**")
    current_stock = inv_df[inv_df["Status"] == "In Warehouse"]
    
    if not current_stock.empty:
        fig_3d = go.Figure(data=[go.Scatter3d(
            x=current_stock['X_Coord'], y=current_stock['Y_Coord'], z=current_stock['Z_Coord'],
            mode='markers', text=current_stock['Batch_QR'] + "<br>" + current_stock['Item_Name'] + "<br>Health: " + current_stock['Shelf_Life_Health'],
            hoverinfo='text',
            marker=dict(size=6, color=current_stock['Z_Coord'], colorscale='Tealgrn', opacity=0.9, line=dict(width=1, color='white'))
        )])
        fig_3d.update_layout(
            margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                xaxis_title='Aisle Grid (X)', yaxis_title='Rack Grid (Y)', zaxis_title='Vertical Shelf (Z)',
                xaxis=dict(gridcolor='#333', backgroundcolor='rgba(0,0,0,0)'),
                yaxis=dict(gridcolor='#333', backgroundcolor='rgba(0,0,0,0)'),
                zaxis=dict(gridcolor='#333', backgroundcolor='rgba(0,0,0,0)'),
                camera=dict(eye=dict(x=1.5, y=1.5, z=0.5))
            ), height=550
        )
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("Warehouse is currently completely empty.")

    st.markdown("---")
    st.subheader("Warehouse Inventory Database (Live Shelf Life)")
    display_cols = ['Batch_QR', 'Item_Name', 'Warehouse_Side', 'Age_Days', 'Max_Shelf_Life_Days', 'Shelf_Life_Health', 'Status']
    st.dataframe(inv_df[display_cols], use_container_width=True, height=350)
    render_footer()

# ==========================================
# PAGE 3: ERP & GLOBAL PROCUREMENT
# ==========================================
elif page == "ERP & Global Procurement":
    st.title("⚙️ ERP & Global Intermodal Procurement")
    st.markdown("Full-suite enterprise resource planning integrated with AI forecasting, cross-border currency exchanges, and ESG governance.")
    
    inv_df = get_enriched_inventory()
    current_stock = inv_df[inv_df["Status"] == "In Warehouse"]
    
    capital_locked = current_stock['Unit_Cost_USD'].sum()
    carbon_tax = st.session_state['total_carbon_tax_accrued']
    
    is_peak_window = now.weekday() in [3, 4] 
    ai_multiplier = 1.5 if is_peak_window else 1.0
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Locked (Inventory)", f"${capital_locked:,.2f}")
    c2.metric("ESG Carbon Tax Accrued", f"${carbon_tax:,.2f}")
    c3.metric("AI Demand Forecast", "Surge Expected" if is_peak_window else "Stable Baseline")
    c4.metric("Dynamic Stock Multiplier", f"{ai_multiplier}x")
    st.markdown("---")

    erp_records = []
    for item in items_list:
        count = len(current_stock[current_stock['Item_Name'] == item])
        base_safety = 15 
        dynamic_safety = int(base_safety * ai_multiplier)
        status = "Optimal"
        if count <= dynamic_safety:
            status = "🔴 Auto-Order Triggered"
            if f"AUTO_ORDER_{item}" not in " ".join(st.session_state['erp_order_logs'][:5]):
                order_qty = (dynamic_safety * 2) - count
                best_hub, best_rate = random.choice(list(currency_rates.items()))
                local_cost = round(base_costs[item] * best_rate, 2)
                st.session_state['erp_order_logs'].insert(0, f"[{now.strftime('%H:%M:%S')}] 🤖 AI CROSS-BORDER EXECUTION: Bought {order_qty}x {item} from {best_hub} @ {local_cost} local currency.")
                st.session_state['erp_order_logs'].insert(0, f"[{now.strftime('%H:%M:%S')}] AUTO_ORDER_{item}_LOGGED")
        elif count <= dynamic_safety + 4:
            status = "🟠 Approaching AI Threshold"
        erp_records.append({"Product": item, "Live Stock": count, "Dynamic AI Safety": dynamic_safety, "ERP Status": status})
        
    colA, colB = st.columns([1.5, 1])
    with colA:
        st.subheader("Global Inventory & AI Thresholds")
        st.dataframe(pd.DataFrame(erp_records), use_container_width=True)
        
        st.subheader("Supplier Health Matrix (Lead Times)")
        supplier_data = pd.DataFrame([
            {"Supplier Code": "SUP-IND-01", "Region": "India", "Avg Lead Time": "3.2 Days", "On-Time %": "98%", "Grade": "🟢 A (Prime)"},
            {"Supplier Code": "SUP-DXB-99", "Region": "Dubai", "Avg Lead Time": "1.1 Days", "On-Time %": "99%", "Grade": "🟢 A (Prime)"},
            {"Supplier Code": "SUP-SGP-42", "Region": "Singapore", "Avg Lead Time": "5.6 Days", "On-Time %": "82%", "Grade": "🟠 C (Risk)"}
        ])
        st.dataframe(supplier_data, hide_index=True, use_container_width=True)

    with colB:
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
                st.session_state['erp_order_logs'].insert(0, f"[{now.strftime('%H:%M:%S')}] INTERMODAL PO: {mo_qty} pallets {mo_item} via {transport_mode}. Cost: ${cost}. ESG Impact: {esg_impact}.")
                st.success(f"Dispatched via {transport_mode} | Transit: {time_est} | Logistics Cost: ${cost}")

    st.markdown("#### 📡 Global AI Action & Intermodal Log")
    st.markdown(f'<div class="crypto-terminal">{"<br>".join(st.session_state["erp_order_logs"])}</div>', unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 4: GPS & FLEET TRACKING
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Route Tracing")
    st.markdown("Real-time telemetry, dynamic traffic conditions, and ETA tracking for active fleets.")
    st.markdown("👉 **Click directly on a Truck ID row in the table to view its live route!**")

    st.warning("⚠️ **AI WEATHER ALERT:** Severe Sandstorm Detected near E11 Highway (Sharjah Boundary). Adjusting ETA predictions dynamically.", icon="🌪️")

    fleet_data = []
    for d in st.session_state['fleet_state']:
        route_coords = real_routes[d["dest"]]
        c_lat, c_lon = get_interpolated_pos(route_coords, d["progress"])
        fuel_burn = round((d["progress"] * 100) * 0.35, 1)
        co2_emissions = round(fuel_burn * 2.68, 1) 
        fleet_data.append({
            "Truck": d["id"], "Destination": d["dest"],
            "start_lat": route_coords[0][0], "start_lon": route_coords[0][1],
            "curr_lat": c_lat, "curr_lon": c_lon,
            "dest_lat": route_coords[-1][0], "dest_lon": route_coords[-1][1],
            "speed": d["speed"], "Traffic Condition": d["traffic"],
            "Route Color": d["color"], "ETA": d["eta"],
            "fuel": fuel_burn, "co2": co2_emissions, "progress": d["progress"]
        })

    try:
        selection_event = st.dataframe(
            st.session_state['static_fleet_df'],
            on_select="rerun",
            selection_mode="single-row",
            key="truck_selection_table" 
        )
        if selection_event.selection.rows:
            selected_truck = st.session_state['static_fleet_df'].iloc[selection_event.selection.rows[0]]["Truck ID"]
        else:
            selected_truck = "All Active Fleet"
    except Exception:
        st.dataframe(st.session_state['static_fleet_df'])
        selected_truck = st.selectbox("🎯 Target ID Focus:", ["All Active Fleet"] + st.session_state['static_fleet_df']["Truck ID"].tolist())

    st.markdown("---")
    
    if selected_truck != "All Active Fleet":
        live_data = next(item for item in fleet_data if item["Truck"] == selected_truck)
        st.subheader(f"📡 Focus Target: {selected_truck} | ESG Telemetry Active")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Speed", f"{live_data['speed']} km/h")
        col2.metric("Traffic Route", live_data['Traffic Condition'])
        col3.metric("Live Fuel Burn", f"{live_data['fuel']} L")
        col4.metric("CO2 Emissions", f"{live_data['co2']} kg")
        
        plot_data = [d for d in fleet_data if d["Truck"] == selected_truck]
        map_zoom = 11.5
        map_center = {"lat": plot_data[0]["curr_lat"], "lon": plot_data[0]["curr_lon"]}
    else:
        st.subheader(f"📡 Satellite Telemetry: All Active Fleet ({len(fleet_data)} Transports)")
        plot_data = fleet_data
        map_zoom = 9
        map_center = {"lat": 25.12, "lon": 55.20}
    
    map_layout = dict(style="carto-darkmatter", zoom=map_zoom, center=map_center)
    fig = go.Figure()
    
    fig.add_trace(go.Scattermap(
        mode="markers", lon=[55.33], lat=[25.26], 
        marker=dict(size=80, color='rgba(255, 140, 0, 0.3)'),
        name="Anomaly", text="⚠️ Severe Sandstorm Zone", hoverinfo='text'
    ))
    
    for d in plot_data:
        line_color = d['Route Color'] if selected_truck != "All Active Fleet" else 'rgba(255, 255, 255, 0.2)'
        route_coords = real_routes[d['Destination']]
        
        fig.add_trace(go.Scattermap(
            mode="lines", lon=[p[1] for p in route_coords], lat=[p[0] for p in route_coords],
            line=dict(width=5, color=line_color), hoverinfo='none'
        ))
        
        if selected_truck != "All Active Fleet":
            fig.add_trace(go.Scattermap(
                mode="markers+text", lon=[d['start_lon']], lat=[d['start_lat']],
                marker=dict(size=14, color='white'), text="Departure: StormNode Hub",
                textposition="bottom center", textfont=dict(color="white", size=14, weight="bold"), hoverinfo='text'
            ))
            fig.add_trace(go.Scattermap(
                mode="markers+text", lon=[d['dest_lon']], lat=[d['dest_lat']],
                marker=dict(size=14, color='#00FF55'), text=f"Arrival: {d['Destination']}",
                textposition="top center", textfont=dict(color="#00FF55", size=14, weight="bold"), hoverinfo='text'
            ))

        marker_text = f"<b>{d['Truck']}</b><br>Speed: {d['speed']} km/h<br>ETA: {d['ETA']}<br>CO2: {d['co2']}kg"
        fig.add_trace(go.Scattermap(
            mode="markers", lon=[d['curr_lon']], lat=[d['curr_lat']],
            marker=dict(size=16, color='#00D2FF'), name=d['Truck'], text=marker_text, hoverinfo='text'
        ))

    fig.update_layout(
        map=map_layout, uirevision=selected_truck, margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False, height=600
    )
    st.plotly_chart(fig, use_container_width=True)
    render_footer()

# ==========================================
# PAGE 5: AI PREDICTIVE ANALYTICS
# ==========================================
elif page == "AI Predictive Analytics":
    st.title("🧠 AI Predictive Analytics Forecast")
    st.markdown("Machine Learning algorithms calculating expected dockyard capacity constraints over the next 7 days.")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Forecasting Model", "Random Forest Regressor")
    col2.metric("Historical Data Fed", "8.4 Million Rows")
    col3.metric("Prediction Accuracy", "96.4%", "+2.1%")
    st.markdown("---")

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    expected_trucks = [120, 145, 130, 190, 240, 100, 85]
    
    fig_ml = go.Figure()
    
    fig_ml.add_trace(go.Scatter(
        x=days, y=expected_trucks, mode='lines+markers',
        line=dict(color='#00D2FF', width=4, shape='spline'),
        marker=dict(size=10, color='white'), name="Predicted Traffic"
    ))
    
    fig_ml.add_shape(
        type="rect", x0="Thu", y0=180, x1="Fri", y1=260,
        fillcolor="rgba(255, 51, 51, 0.2)", line=dict(width=0), layer="below"
    )
    fig_ml.add_annotation(
        x="Fri", y=240, text="🚨 Critical Bottleneck Predicted",
        showarrow=True, arrowhead=1, ax=0, ay=-40,
        font=dict(color="#FF3333", size=14, weight="bold")
    )

    fig_ml.update_layout(
        title="7-Day Forward Telemetry Forecast (Trucks per Day)",
        xaxis=dict(showgrid=False, color="#C5C6C7"),
        yaxis=dict(title="Volume", gridcolor="#333", color="#C5C6C7"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=450
    )
    st.plotly_chart(fig_ml, use_container_width=True)
    
    st.error("🚨 **Root Cause Diagnostic:** Neural network cross-referencing indicates an unscheduled high-capacity **railway freight exchange** is overlapping with our peak Friday outbound highway dispatch window. This intermodal collision will exhaust available staging bays.")
    
    st.markdown("---")
    st.subheader("🤖 Agentic AI Self-Healing Command Terminal")
    st.markdown("Embedded autonomous agents collaborating natively inside the software architecture to resolve constraints.")
    
    # Generate shifting conversation logs based on active clock ticks
    t_sec = int(time.time()) % 20
    if t_sec < 5:
        step_log = f"[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: Friday railway bottleneck intercepted. Capacity limit threshold reached. Ping @CBA_AGENT.<br>[{now.strftime('%H:%M:%S')}] [SYSTEM]: Awaiting Agent negotiation protocols..."
    elif t_sec < 10:
        step_log = f"[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: Friday railway bottleneck intercepted. Capacity limit threshold reached. Ping @CBA_AGENT.<br>[{now.strftime('%H:%M:%S')}] [CBA_AGENT]: Acknowledged. Pinging spot-carrier APIs to execute dynamic holding container buffer contracts..."
    elif t_sec < 15:
        step_log = f"[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: Friday railway bottleneck intercepted.<br>[{now.strftime('%H:%M:%S')}] [CBA_AGENT]: Spot rate contract successfully renegotiated at -8% baseline via automated API handshake.<br>[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: Rerouting commands broadcasted. Diverting 40% of highway inbound trucks to Secondary Holding Zone B in real-time."
    else:
        step_log = f"[{now.strftime('%H:%M:%S')}] [CBA_AGENT]: Spot contract renegotiated at -8% baseline via automated API handshake.<br>[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: Diverting 40% of highway inbound trucks to Secondary Holding Zone B in real-time.<br>[{now.strftime('%H:%M:%S')}] [LCA_AGENT]: <b>[AUTO-EXECUTE SUCCESS]</b> 3D Digital Twin updated. Staging cross-docking bays 3 & 4 completely cleared for early railway offload."

    st.markdown(f'<div class="agent-terminal"><span style="color:#00FF55;">[STATUS: AUTONOMOUSLY HEALING DEVIATION]</span><br><br>{step_log}</div>', unsafe_allow_html=True)
    render_footer()

# ==========================================
# PAGE 6: ABOUT STORMNODE (MASSIVELY EXPANDED)
# ==========================================
elif page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    st.markdown("### Powering the Connected Supply Chain")
    st.image("https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=1200&q=80", caption="StormNode Next-Generation Fulfillment Center")
    st.markdown("---")
    
    st.subheader("Global Operations At A Glance")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_eff = go.Figure(go.Indicator(
            mode = "gauge+number", value = 94.2, title = {'text': "Fleet Efficiency (%)"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00D2FF"}}
        ))
        fig_eff.update_layout(height=220, margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#C5C6C7"})
        st.plotly_chart(fig_eff, use_container_width=True)
    with col2:
        fig_up = go.Figure(go.Indicator(
            mode = "gauge+number", value = 99.9, title = {'text': "System Uptime (%)"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00FF55"}}
        ))
        fig_up.update_layout(height=220, margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#C5C6C7"})
        st.plotly_chart(fig_up, use_container_width=True)
    with col3:
        fig_ai = go.Figure(go.Indicator(
            mode = "gauge+number", value = 1.2, title = {'text': "AI Latency (ms)"},
            gauge = {'axis': {'range': [None, 5]}, 'bar': {'color': "#FFB300"}}
        ))
        fig_ai.update_layout(height=220, margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#C5C6C7"})
        st.plotly_chart(fig_ai, use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    **StormNode Logistics** is a next-generation freight and warehousing platform designed to completely bridge the gap between heavy physical freight and cutting-edge digital infrastructure. 
    
    Built natively on Python for unparalleled data analytics and automated task processing, our architecture treats every warehouse, dispatch truck, and cargo batch as a vital "node" in a highly connected, self-healing neural network. This prototype demonstrates enterprise-grade logistics capabilities optimized specifically for complex, high-velocity distribution models.
    """)
    
    st.markdown("### 📦 Strategic Focus: Packaged Foods Sector")
    st.markdown("""
    The architecture of StormNode is heavily optimized for the rapidly expanding Packaged Foods and FMCG sectors. This vertical faces unique challenges: highly volatile seasonal demand, strict shelf-life constraints, and heavy reliance on cold-chain integrity. 
    
    Our proprietary **Dynamic Inventory Engine** calculates the exact age of every pallet in real-time, assigning a live health matrix to ensure expiring stock is autonomously rotated and dispatched before capital loss occurs. Coupled with our predictive Random Forest machine learning models, the system ensures that regional food distribution centers never face critical staging bottlenecks that could compromise perishable cargo.
    """)

    st.markdown("### 🧠 Platform Capabilities")
    with st.expander("🏭 Automated Dockyard Management & IoT", expanded=True):
        st.write("Real-time physical sensor integration automates entry logs, dispatch clearances, and staging bay allocations. By utilizing edge-computing at the physical gates, StormNode eliminates manual gatehouse processing delays, drastically reducing idle times and fuel burn for massive heavy-freight fleets.")
    with st.expander("📦 Inventory & Blockchain Chain-of-Custody"):
        st.write("High-fidelity tracing ties exact physical bin locations to active transport routes using a 3D Cartesian Coordinate Digital Twin. To prevent fraud and theft, every dispatch is locked into an immutable ledger using SHA-256 cryptographic hashing, guaranteeing a 100% transparent chain of custody from the manufacturer to the end-consumer.")
    with st.expander("⚙️ Agentic AI & Enterprise Resource Planning (ERP)"):
        st.write("StormNode utilizes bleeding-edge Agentic AI—digital employees embedded directly in the software. When constraints are detected, these AI agents negotiate spot rates, trigger automated purchase orders, and reroute trucks completely autonomously. The global ERP engine actively monitors live capital lock-up and calculates ESG carbon taxes in real-time.")
    
    st.markdown("---")
    st.markdown("### 🚂 Our Vision: The Intermodal Railway Future")
    st.markdown("""
    The ultimate evolution of StormNode lies far beyond the highway. Our technical roadmap is heavily focused on **Intermodal Freight and High-Capacity Railway Integration** across critical international trade triangles. 
    
    The global railway sector forms the absolute backbone of sustainable logistics. As this platform matures, our vision is to seamlessly bridge the gap between regional truck dockyards and high-speed intermodal rail networks. By unifying freight tracking across vital global hubs—specifically optimizing the flow of goods between **Dubai, Singapore, and India**—StormNode will provide an unbroken, financially optimized, and environmentally conscious chain of custody across massive, multi-continental geographical regions.
    """)
    
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
