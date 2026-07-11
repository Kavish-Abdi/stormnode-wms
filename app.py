import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- PAGE CONFIGURATION & LOGO ---
st.set_page_config(page_title="StormNode Logistics", page_icon="⚡", layout="wide")

try:
    st.sidebar.image("logo1.png")
except:
    st.sidebar.title("⚡")

# --- GLOBAL STYLES & CUSTOM BRANDING ---
st.markdown("""
    <style>
    /* Move Streamlit Notifications (Toasts) to the Top Right */
    div[data-testid="stToastContainer"] {
        top: 2rem;
        right: 2rem;
        bottom: auto !important;
        left: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #00D2FF; font-size: 26px; font-weight: bold; margin-top: -15px;'>"
    "StormNode Logistics<br>"
    "<span style='font-size: 14px; color: #00F0FF; font-style: italic;'>Powering the Connected Supply Chain</span>"
    "</div>",
    unsafe_allow_html=True
)

# --- HELPER FUNCTIONS ---
def render_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-family: \"Times New Roman\", Times, serif; color: #C5C6C7; font-size: 14px;'>"
        "<strong>StormNode Logistics</strong> | Est. 2026<br>"
        "<em>Powering the Connected Supply Chain</em>"
        "</div>", 
        unsafe_allow_html=True
    )

# --- GLOBAL AUTOREFRESH & SESSION INIT ---
st_autorefresh(interval=60000, limit=1000, key="global_autorefresh")

if 'trigger_sound' not in st.session_state:
    st.session_state['trigger_sound'] = None

if 'truck_logs' not in st.session_state:
    synthetic_trucks = []
    locations = ["Whse A - Dock 1", "Whse A - Dock 2", "Whse B - Dock 1", "Whse C - Heavy Freight", "Whse C - Cold Chain"]
    for i in range(10):
        entry_time = datetime.now() - timedelta(minutes=random.randint(15, 120))
        synthetic_trucks.append({
            "Truck_ID": f"TRK-{random.randint(1000, 9999)}", 
            "Entry_Time": entry_time.strftime("%Y-%m-%d %H:%M:%S"), 
            "Exit_Time": "Pending" if i % 2 == 0 else (entry_time + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), 
            "Warehouse_Location": random.choice(locations),
            "Status": "At Dock" if i % 2 == 0 else "Dispatched",
            "Last_Updated": entry_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    st.session_state['truck_logs'] = pd.DataFrame(synthetic_trucks)
    st.session_state['last_auto_update'] = datetime.now()
    st.session_state['auto_toggle'] = "entry" 

if 'inventory' not in st.session_state:
    synthetic_inv = []
    items = ["Semiconductors", "Lithium Batteries", "Auto Parts", "Medical Supplies", "Consumer Tech", "Machinery"]
    sides = ["North Wing", "South Wing", "East Wing", "West Wing"]
    for i in range(20):
        synthetic_inv.append({
            "Batch_QR": f"QR-{random.randint(1000, 9999)}", 
            "Item_Name": random.choice(items), 
            "Warehouse_Side": random.choice(sides),
            "Aisle_Number": f"Aisle {random.randint(1, 15)}",
            "Bin_Location": f"Bin {random.choice(['A','B','C','D'])}-{random.randint(1,9)}",
            "Time_Received": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S"), 
            "Time_Dispatched": "N/A", 
            "Dispatched_On_Truck": "N/A", 
            "Status": "In Warehouse"
        })
    st.session_state['inventory'] = pd.DataFrame(synthetic_inv)

# --- NAVIGATION ---
st.sidebar.markdown("---")
page = st.sidebar.radio("Main Menu", [
    "Dockyard Management", 
    "Inventory & QR Tracking", 
    "GPS & Fleet Tracking",
    "About StormNode"
])

# --- GLOBAL BACKGROUND EVENT SIMULATOR ---
now = datetime.now()
if (now - st.session_state['last_auto_update']).total_seconds() >= 58:  
    st.session_state['last_auto_update'] = now
    locations = ["Whse A - Dock 1", "Whse A - Dock 2", "Whse B - Dock 1", "Whse C - Heavy Freight"]
    
    if st.session_state['auto_toggle'] == "entry":
        auto_truck_id = f"TRK-{random.randint(1000, 9999)}"
        new_entry = pd.DataFrame([{
            "Truck_ID": auto_truck_id, 
            "Entry_Time": now.strftime("%Y-%m-%d %H:%M:%S"), 
            "Exit_Time": "Pending", 
            "Warehouse_Location": random.choice(locations),
            "Status": "At Dock",
            "Last_Updated": now.strftime("%Y-%m-%d %H:%M:%S")
        }])
        st.session_state['truck_logs'] = pd.concat([new_entry, st.session_state['truck_logs']], ignore_index=True)
        st.session_state['auto_toggle'] = "exit"
        st.session_state['trigger_sound'] = "entry"
        
        if page != "Dockyard Management":
            st.toast(f"📡 Fleet Update: {auto_truck_id} has arrived at the dock.", icon="🟢")
            
    else:
        docked = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]
        if not docked.empty:
            idx = docked.index[-1]
            t_id = st.session_state['truck_logs'].at[idx, "Truck_ID"]
            st.session_state['truck_logs'].at[idx, "Exit_Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
            st.session_state['truck_logs'].at[idx, "Last_Updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
        
        st.session_state['auto_toggle'] = "entry"
        st.session_state['trigger_sound'] = "exit"
        
        if page != "Dockyard Management":
            st.toast(f"📡 Fleet Update: {t_id} was safely dispatched.", icon="🔴")

# --- PROCESS GLOBAL AUDIO ---
audio_tag = ""
if st.session_state['trigger_sound'] == "entry":
    audio_tag = f"""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2573/2573-preview.mp3?t={time.time()}" type="audio/mpeg"></audio>"""
    st.session_state['trigger_sound'] = None
elif st.session_state['trigger_sound'] == "exit":
    audio_tag = f"""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2574/2574-preview.mp3?t={time.time()}" type="audio/mpeg"></audio>"""
    st.session_state['trigger_sound'] = None

if page != "Dockyard Management" and audio_tag:
    st.markdown(audio_tag, unsafe_allow_html=True)


# ==========================================
# PAGE 1: DOCKYARD MANAGEMENT
# ==========================================
if page == "Dockyard Management":
    st.title("🚛 Dockyard Management")
    st.markdown("Automated gate sensors and real-time dispatch control.")

    df = st.session_state['truck_logs']
    df_docked = df[df["Status"] == "At Dock"]
    df_dispatched = df[df["Status"] == "Dispatched"]

    css_animations = f"""
    {audio_tag}
    <style>
    @keyframes blink-animation-cyan {{
        0% {{ background-color: #00D2FF; color: #000000; }}
        50% {{ background-color: transparent; color: #C5C6C7; }}
        100% {{ background-color: #00D2FF; color: #000000; }}
    }}
    @keyframes blink-animation-green {{
        0% {{ background-color: #00FF55; color: #000000; }}
        50% {{ background-color: transparent; color: #C5C6C7; }}
        100% {{ background-color: #00FF55; color: #000000; }}
    }}
    .blinking-row-cyan {{ animation: blink-animation-cyan 1s linear 10; }}
    .blinking-row-green {{ animation: blink-animation-green 1s linear 10; }}
    .custom-table {{ width: 100%; text-align: left; border-collapse: collapse; color: #C5C6C7; font-size: 14px; margin-bottom: 20px;}}
    .custom-table th, .custom-table td {{ padding: 10px; border-bottom: 1px solid #1F2833; }}
    .custom-table th {{ color: #ffffff; font-weight: bold; background-color: #1A2235; }}
    </style>
    """
    
    st.markdown("---")
    st.subheader("🟢 Active Fleet (At Dock)")
    html_docked = f"{css_animations}<table class='custom-table'><thead><tr><th>Truck ID</th><th>Entry Time</th><th>Exit Time</th><th>Location</th><th>Status</th></tr></thead><tbody>"
    for _, row in df_docked.iterrows():
        update_time = datetime.strptime(row['Last_Updated'], "%Y-%m-%d %H:%M:%S")
        time_diff = (now - update_time).total_seconds()
        row_class = "blinking-row-cyan" if time_diff < 15 else ""
        html_docked += f"<tr class='{row_class}'><td>{row['Truck_ID']}</td><td>{row['Entry_Time']}</td><td>{row['Exit_Time']}</td><td>{row['Warehouse_Location']}</td><td>{row['Status']}</td></tr>"
    html_docked += "</tbody></table>"
    st.markdown(html_docked, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔴 Dispatched Log")
    html_dispatched = f"<table class='custom-table'><thead><tr><th>Truck ID</th><th>Entry Time</th><th>Exit Time</th><th>Location</th><th>Status</th></tr></thead><tbody>"
    for _, row in df_dispatched.iterrows():
        update_time = datetime.strptime(row['Last_Updated'], "%Y-%m-%d %H:%M:%S")
        time_diff = (now - update_time).total_seconds()
        row_class = "blinking-row-green" if time_diff < 15 else ""
        html_dispatched += f"<tr class='{row_class}'><td>{row['Truck_ID']}</td><td>{row['Entry_Time']}</td><td>{row['Exit_Time']}</td><td>{row['Warehouse_Location']}</td><td>{row['Status']}</td></tr>"
    html_dispatched += "</tbody></table>"
    st.markdown(html_dispatched, unsafe_allow_html=True)

    render_footer()

# ==========================================
# PAGE 2: INVENTORY & QR TRACKING
# ==========================================
elif page == "Inventory & QR Tracking":
    st.title("📦 Inventory & Warehouse Tracing")
    st.markdown("Pinpoint exact batch locations and link them to dispatch trucks.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Receive New Batch")
        batch_qr = st.text_input("Batch QR", placeholder="e.g. QR-5542")
        item_name = st.text_input("Product")
        side = st.selectbox("Warehouse Side", ["North Wing", "South Wing", "East Wing", "West Wing"])
        aisle = st.text_input("Aisle Number", placeholder="e.g. Aisle 5")
        bin_loc = st.text_input("Bin Location", placeholder="e.g. Bin B-2")
        
        if st.button("Store Inventory", type="primary"):
            if batch_qr and item_name:
                new_item = pd.DataFrame([{
                    "Batch_QR": batch_qr, "Item_Name": item_name, "Warehouse_Side": side,
                    "Aisle_Number": aisle, "Bin_Location": bin_loc,
                    "Time_Received": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"
                }])
                st.session_state['inventory'] = pd.concat([new_item, st.session_state['inventory']], ignore_index=True)
                st.success(f"Stored {batch_qr} at {side} > {aisle} > {bin_loc}.")
                st.session_state['trigger_sound'] = "entry"
                st.rerun()

    with col2:
        st.subheader("Dispatch Batch")
        in_stock = st.session_state['inventory'][st.session_state['inventory']["Status"] == "In Warehouse"]["Batch_QR"].tolist()
        if in_stock:
            dispatch_qr = st.selectbox("Select Batch QR", ["Select"] + in_stock)
            dispatch_truck = st.text_input("Assign to Truck ID")
            if st.button("Dispatch"):
                if dispatch_qr != "Select" and dispatch_truck:
                    idx = st.session_state['inventory'].index[st.session_state['inventory']['Batch_QR'] == dispatch_qr].tolist()[0]
                    st.session_state['inventory'].at[idx, "Time_Dispatched"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state['inventory'].at[idx, "Dispatched_On_Truck"] = dispatch_truck
                    st.session_state['inventory'].at[idx, "Status"] = "In Transit"
                    st.success(f"Dispatched {dispatch_qr} on {dispatch_truck}.")
                    st.session_state['trigger_sound'] = "exit"
                    st.rerun()

    st.markdown("---")
    st.subheader("Warehouse Inventory Database")
    # THE FIX: Changed to width='stretch' to stop the crash
    st.dataframe(st.session_state['inventory'], width="stretch")
    
    render_footer()

# ==========================================
# PAGE 3: GPS & FLEET TRACKING
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Route Tracing")
    st.markdown("Real-time telemetry and dynamic routing for active fleets.")

    hub_lat, hub_lon = 24.9857, 55.0273
    destinations = [
        {"id": "TRK-901", "dest": "DXB Airport", "d_lat": 25.2532, "d_lon": 55.3657},
        {"id": "TRK-902", "dest": "Dubai Mall", "d_lat": 25.1972, "d_lon": 55.2744},
        {"id": "TRK-903", "dest": "Dubai Marina", "d_lat": 25.0805, "d_lon": 55.1403},
        {"id": "TRK-904", "dest": "Al Maktoum Int", "d_lat": 24.8966, "d_lon": 55.1605},
        {"id": "TRK-905", "dest": "Sharjah Ind", "d_lat": 25.3134, "d_lon": 55.4055}
    ]
    
    fleet_data = []
    for d in destinations:
        progress = float(random.uniform(0.1, 0.9))
        c_lat = float(hub_lat + (d["d_lat"] - hub_lat) * progress)
        c_lon = float(hub_lon + (d["d_lon"] - hub_lon) * progress)
        fleet_data.append({
            "Truck": d["id"], "Destination": d["dest"],
            "start_lat": hub_lat, "start_lon": hub_lon,
            "curr_lat": c_lat, "curr_lon": c_lon,
            "dest_lat": d["d_lat"], "dest_lon": d["d_lon"],
            "speed": random.randint(45, 90), "status": random.choice(["🟢 Clear", "🟡 Moderate"])
        })
    df_fleet = pd.DataFrame(fleet_data)

    # THE FIX: Changed to width='stretch'
    st.dataframe(df_fleet[["Truck", "Destination", "speed", "status"]], width="stretch")

    st.markdown("### Active Route Tracing")
    
    fig = go.Figure()
    
    for d in fleet_data:
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[d['start_lon'], d['curr_lon'], d['dest_lon']],
            lat=[d['start_lat'], d['curr_lat'], d['dest_lat']],
            line=dict(width=2, color='rgba(255, 255, 255, 0.3)'),
            hoverinfo='none'
        ))
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[d['curr_lon']],
            lat=[d['curr_lat']],
            marker=dict(size=14, color='#00D2FF'),
            name=d['Truck'],
            text=f"{d['Truck']} heading to {d['Destination']}",
            hoverinfo='text'
        ))

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_zoom=9,
        mapbox_center={"lat": 25.12, "lon": 55.20},
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False,
        height=500
    )
    
    # Removed the deprecated prop entirely here, Plotly handles width automatically
    st.plotly_chart(fig)
    
    render_footer()

# ==========================================
# PAGE 4: ABOUT STORMNODE
# ==========================================
elif page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    st.markdown("### Powering the Connected Supply Chain")
    st.markdown("""
    **StormNode Logistics** is a next-generation freight and warehousing startup designed to bridge the gap between heavy physical freight and cutting-edge digital infrastructure. 
    
    Founded in 2026, our mission is to eliminate supply chain opacity. Traditional logistics rely on manual data entry and fragmented tracking systems. At StormNode, we treat every warehouse, truck, and cargo batch as a "node" in a highly connected, automated neural network.
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
    "<b>SP Jain School of Global Management</b><br>"
    "<i>Under the guidance of Prof. Rajiv Asrekar</i>"
    "</div>", 
    unsafe_allow_html=True
)
