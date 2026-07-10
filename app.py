import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import pydeck as pdk
from streamlit_autorefresh import st_autorefresh

# --- PAGE CONFIGURATION & LOGO ---
st.set_page_config(page_title="StormNode Logistics", page_icon="⚡", layout="wide")

try:
    st.sidebar.image("logo1.png")
except:
    st.sidebar.title("⚡")

# --- CUSTOM BRANDING (TIMES NEW ROMAN & BRIGHT) ---
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
        "<div style='text-align: center; color: #C5C6C7; font-size: 14px;'>"
        "<strong>StormNode Logistics</strong> | Est. 2024<br>"
        "<em>Powering the Connected Supply Chain</em>"
        "</div>", 
        unsafe_allow_html=True
    )

# --- INITIALIZE SYNTHETIC DATABASE (Session State) ---
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

# ==========================================
# PAGE 1: DOCKYARD MANAGEMENT
# ==========================================
if page == "Dockyard Management":
    # Autorefresh isolated to this page to prevent global crashes
    count = st_autorefresh(interval=60000, limit=1000, key="dockyard_auto")
    
    st.title("🚛 Dockyard Management")
    st.markdown("Automated gate sensors and real-time dispatch control.")

    # AUTOMATED LIVE ENTRY/EXIT LOGIC
    now = datetime.now()
    if (now - st.session_state['last_auto_update']).total_seconds() >= 60:
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
            st.toast(f"📡 Sensor Alert: {auto_truck_id} arrived automatically.", icon="🟢")
            st.session_state['auto_toggle'] = "exit"
            
        else:
            docked = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]
            if not docked.empty:
                idx = docked.index[-1]
                t_id = st.session_state['truck_logs'].at[idx, "Truck_ID"]
                st.session_state['truck_logs'].at[idx, "Exit_Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
                st.session_state['truck_logs'].at[idx, "Last_Updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
                st.toast(f"📡 Sensor Alert: {t_id} dispatched automatically.", icon="🔴")
            st.session_state['auto_toggle'] = "entry"

    # STYLING FUNCTION FOR NEW ROWS
    def highlight_recent(row):
        try:
            update_time = datetime.strptime(row['Last_Updated'], "%Y-%m-%d %H:%M:%S")
            if (now - update_time).total_seconds() < 65:
                # Returns a bright cyan highlight for 60 seconds
                return ['background-color: rgba(0, 210, 255, 0.4); color: white;'] * len(row)
        except:
            pass
        return [''] * len(row)

    # SPLIT DATA INTO TWO TABLES
    df = st.session_state['truck_logs']
    df_docked = df[df["Status"] == "At Dock"].drop(columns=["Last_Updated"])
    df_dispatched = df[df["Status"] == "Dispatched"].drop(columns=["Last_Updated"])

    st.markdown("---")
    st.subheader("🟢 Active Fleet (At Dock)")
    st.dataframe(df_docked.style.apply(highlight_recent, axis=1), use_container_width=True)

    st.markdown("---")
    st.subheader("🔴 Dispatched Log")
    st.dataframe(df_dispatched.style.apply(highlight_recent, axis=1), use_container_width=True)

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

    st.markdown("---")
    st.subheader("Warehouse Inventory Database")
    st.dataframe(st.session_state['inventory'], use_container_width=True)
    
    render_footer()

# ==========================================
# PAGE 3: GPS & FLEET TRACKING (LIVE ROUTING)
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Route Tracing")
    st.markdown("Real-time telemetry and dynamic routing for active fleets.")

    # Fleet Data
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

    st.dataframe(df_fleet[["Truck", "Destination", "speed", "status"]], use_container_width=True)

    st.markdown("### Active Route Tracing")
    
    layer_routes = pdk.Layer(
        "LineLayer",
        df_fleet,
        get_source_position=["start_lon", "start_lat"],
        get_target_position=["dest_lon", "dest_lat"],
        get_color=[100, 100, 100, 150],
        get_width=3,
    )
    
    layer_trucks = pdk.Layer(
        "ScatterplotLayer",
        df_fleet,
        get_position=["curr_lon", "curr_lat"],
        get_color=[0, 210, 255, 255], 
        get_radius=800,
        pickable=True
    )
    
    view_state = pdk.ViewState(latitude=25.12, longitude=55.20, zoom=9, pitch=45)
    st.pydeck_chart(pdk.Deck(layers=[layer_routes, layer_trucks], initial_view_state=view_state, tooltip={"text": "{Truck} routing to {Destination}"}))
    
    render_footer()

# ==========================================
# PAGE 4: ABOUT STORMNODE
# ==========================================
elif page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    st.markdown("### Powering the Connected Supply Chain")
    st.markdown("""
    **StormNode Logistics** is a next-generation freight and warehousing startup designed to bridge the gap between heavy physical freight and cutting-edge digital infrastructure. 
    
    Founded in 2024, our mission is to eliminate supply chain opacity. Traditional logistics rely on manual data entry and fragmented tracking systems. At StormNode, we treat every warehouse, truck, and cargo batch as a "node" in a highly connected, automated neural network.
    """)
    render_footer()

# --- SIDEBAR ACADEMIC CREDITS ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size: 13px; color: #C5C6C7;'>"
    "<b>App Developer:</b><br>"
    "Syed Ali Kavish Abdi<br>"
    "<b>Batch:</b> MGB OCT 25<br>"
    "<b>Roll No:</b> MS25GLS138<br><br>"
    "<b>SP Jain School of Global Management</b><br>"
    "<i>Under the guidance of Prof. Rajiv Asrekar</i>"
    "</div>", 
    unsafe_allow_html=True
)
