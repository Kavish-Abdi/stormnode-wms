import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- PAGE CONFIGURATION & LOGO ---
st.set_page_config(page_title="StormNode Logistics", page_icon="⚡", layout="wide")

# Load the logo 
try:
    st.sidebar.image("logo1.png")
except:
    st.sidebar.title("⚡ StormNode Logistics")

# --- HELPER FUNCTIONS ---
def render_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 14px;'>"
        "<strong>StormNode Logistics</strong> | Est. 2024<br>"
        "<em>Powering the Connected Supply Chain</em>"
        "</div>", 
        unsafe_allow_html=True
    )

# --- INITIALIZE SYNTHETIC DATABASE (Session State) ---
if 'truck_logs' not in st.session_state:
    # Generate 5 synthetic trucks currently at the dock
    synthetic_trucks = []
    for i in range(5):
        entry_time = datetime.now() - timedelta(minutes=random.randint(15, 120))
        synthetic_trucks.append({
            "Truck_ID": f"TRK-{random.randint(1000, 9999)}", 
            "Entry_Time": entry_time.strftime("%Y-%m-%d %H:%M:%S"), 
            "Exit_Time": "Pending", 
            "Status": "At Dock"
        })
    st.session_state['truck_logs'] = pd.DataFrame(synthetic_trucks)

if 'inventory' not in st.session_state:
    # Generate synthetic inventory
    synthetic_inv = [
        {"Batch_QR": "QR-8821", "Item_Name": "Semiconductors - Type A", "Location": "Aisle 1 - Bin A", "Time_Received": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"},
        {"Batch_QR": "QR-9904", "Item_Name": "Lithium-Ion Batteries", "Location": "Aisle 3 - Cold Storage", "Time_Received": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"},
        {"Batch_QR": "QR-1105", "Item_Name": "Automotive Sensors", "Location": "Aisle 2 - Bin A", "Time_Received": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"}
    ]
    st.session_state['inventory'] = pd.DataFrame(synthetic_inv)

# --- NAVIGATION ---
st.sidebar.markdown("---")
page = st.sidebar.radio("Main Menu", ["About StormNode", "Dockyard Management", "Inventory & QR Tracking", "GPS & Fleet Tracking"])

# ==========================================
# PAGE 1: ABOUT STORMNODE
# ==========================================
if page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    st.markdown("### Powering the Connected Supply Chain")
    
    st.markdown("""
    **StormNode Logistics** is a next-generation freight and warehousing startup designed to bridge the gap between heavy physical freight and cutting-edge digital infrastructure. 
    
    Founded in 2024, our mission is to eliminate supply chain opacity. Traditional logistics rely on manual data entry and fragmented tracking systems. At StormNode, we treat every warehouse, truck, and cargo batch as a "node" in a highly connected, automated neural network.
    
    #### Core Technologies:
    * **Automated Dockyard Sensors:** Replacing manual logs with automated, timestamped truck detection.
    * **Dynamic QR Tracing:** Real-time visibility of inventory from the moment it enters the warehouse to the moment it leaves.
    * **Predictive GPS Routing:** Utilizing live traffic conditions and spatial data to dynamically recalculate Estimated Times of Arrival (ETA).
    
    We don't just move freight; we optimize it.
    """)
    render_footer()

# ==========================================
# PAGE 2: DOCKYARD MANAGEMENT
# ==========================================
elif page == "Dockyard Management":
    st.title("🚛 Dockyard Management")
    st.markdown("Automated gate sensors and real-time dispatch control.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Automated Gate Sensor")
        st.markdown("Simulate a truck passing through the automated RFID gate scanner.")
        if st.button("📡 Auto-Detect Arriving Truck", type="primary"):
            auto_truck_id = f"TRK-{random.randint(1000, 9999)}"
            new_entry = pd.DataFrame([{
                "Truck_ID": auto_truck_id, 
                "Entry_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "Exit_Time": "Pending", 
                "Status": "At Dock"
            }])
            st.session_state['truck_logs'] = pd.concat([st.session_state['truck_logs'], new_entry], ignore_index=True)
            st.success(f"Sensor triggered! {auto_truck_id} logged automatically at {datetime.now().strftime('%H:%M:%S')}")

    with col2:
        st.subheader("Log Truck Exit")
        docked_trucks = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]["Truck_ID"].tolist()
        
        if len(docked_trucks) > 0:
            exit_truck_id = st.selectbox("Select Truck to Dispatch", ["Select a Truck"] + docked_trucks)
            if st.button("Log Exit Timestamp"):
                if exit_truck_id != "Select a Truck":
                    idx = st.session_state['truck_logs'].index[st.session_state['truck_logs']['Truck_ID'] == exit_truck_id].tolist()[-1]
                    st.session_state['truck_logs'].at[idx, "Exit_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
                    st.success(f"Truck {exit_truck_id} exited at {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.info("No trucks currently at the dock.")

    st.markdown("---")
    st.subheader("Live Dockyard Activity Log")
    st.dataframe(st.session_state['truck_logs'], use_container_width=True)
    render_footer()

# ==========================================
# PAGE 3: INVENTORY & QR TRACKING
# ==========================================
elif page == "Inventory & QR Tracking":
    st.title("📦 Inventory & Warehouse Tracing")
    st.markdown("Trace batch locations, receive times, and link them to dispatch trucks.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Scan/Receive New Batch")
        batch_qr = st.text_input("Batch QR / ID Code", placeholder="e.g. QR-5542")
        item_name = st.text_input("Product Description")
        location = st.selectbox("Warehouse Location", ["Aisle 1 - Bin A", "Aisle 1 - Bin B", "Aisle 2 - Bin A", "Aisle 3 - Cold Storage"])
        
        if st.button("Receive Inventory", type="primary"):
            if batch_qr and item_name:
                new_item = pd.DataFrame([{
                    "Batch_QR": batch_qr, "Item_Name": item_name, "Location": location, 
                    "Time_Received": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "Time_Dispatched": "N/A", "Dispatched_On_Truck": "N/A", "Status": "In Warehouse"
                }])
                st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_item], ignore_index=True)
                st.success(f"Batch {batch_qr} stored in {location}.")
            else:
                st.warning("Please fill out QR Code and Product Description.")

    with col2:
        st.subheader("Dispatch Batch")
        in_stock = st.session_state['inventory'][st.session_state['inventory']["Status"] == "In Warehouse"]["Batch_QR"].tolist()
        
        if len(in_stock) > 0:
            dispatch_qr = st.selectbox("Select Batch QR to Dispatch", ["Select a Batch"] + in_stock)
            dispatch_truck = st.text_input("Assign to Truck ID (e.g. TRK-1024)")

            if st.button("Dispatch Inventory"):
                if dispatch_qr != "Select a Batch" and dispatch_truck:
                    idx = st.session_state['inventory'].index[st.session_state['inventory']['Batch_QR'] == dispatch_qr].tolist()[0]
                    st.session_state['inventory'].at[idx, "Time_Dispatched"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state['inventory'].at[idx, "Dispatched_On_Truck"] = dispatch_truck
                    st.session_state['inventory'].at[idx, "Status"] = "In Transit"
                    st.success(f"Batch {dispatch_qr} dispatched on Truck {dispatch_truck}.")
        else:
            st.info("Warehouse is empty.")

    st.markdown("---")
    st.subheader("Warehouse Inventory Database")
    st.dataframe(st.session_state['inventory'], use_container_width=True)
    render_footer()

# ==========================================
# PAGE 4: GPS & FLEET TRACKING
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Traffic Optimization")
    st.markdown("Track active fleet routes, monitor traffic density, and calculate dynamic ETAs.")

    trucks_in_transit = ["TRK-901", "TRK-902", "TRK-903", "TRK-881"]
    selected_truck = st.selectbox("Select Active Truck to Track", trucks_in_transit)

    # Simulating GPS Coordinates (Centered around Dubai)
    lat = 25.2048 + np.random.uniform(-0.1, 0.1)
    lon = 55.2708 + np.random.uniform(-0.1, 0.1)
    
    # Simulating Traffic and ETA math
    distance_remaining = random.randint(15, 120) # km
    
    # Traffic Conditions Logic
    traffic_states = [
        ("🟢 Clear", random.randint(65, 85), 1.0),
        ("🟡 Moderate", random.randint(40, 60), 1.3),
        ("🔴 Heavy", random.randint(15, 35), 2.5)
    ]
    traffic_status, current_speed, traffic_multiplier = random.choice(traffic_states)
    
    # Calculate ETA based on traffic multiplier
    base_eta_hours = distance_remaining / current_speed
    actual_eta_hours = base_eta_hours * traffic_multiplier
    estimated_arrival = datetime.now() + timedelta(hours=actual_eta_hours)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Speed", f"{current_speed} km/h")
    col2.metric("Distance Remaining", f"{distance_remaining} km")
    col3.metric("Traffic Condition", traffic_status)
    col4.metric("Estimated Arrival (ETA)", estimated_arrival.strftime("%I:%M %p"))

    st.markdown("### Live Map Feed")
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_data, zoom=10)
    render_footer()

# --- SIDEBAR ACADEMIC CREDITS ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size: 13px; color: gray;'>"
    "<b>App Developer:</b><br>"
    "[Your Name]<br>"
    "<b>Roll No:</b> [Your Roll Number]<br><br>"
    "<b>SP Jain School of Global Management</b><br>"
    "<i>Under the guidance of Prof. Rajiv Asrekar</i>"
    "</div>", 
    unsafe_allow_html=True
)
