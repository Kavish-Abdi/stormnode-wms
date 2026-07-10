import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION & LOGO ---
st.set_page_config(page_title="StormNode Logistics", page_icon="⚡", layout="wide")

# Load the logo 
try:
    st.sidebar.image("logo1.png")
except:
    st.sidebar.title("⚡ StormNode Logistics")

# --- INITIALIZE DATABASE (Session State) ---
if 'truck_logs' not in st.session_state:
    st.session_state['truck_logs'] = pd.DataFrame(columns=["Truck_ID", "Entry_Time", "Exit_Time", "Status"])

if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=["Batch_QR", "Item_Name", "Location", "Time_Received", "Time_Dispatched", "Dispatched_On_Truck", "Status"])

# --- NAVIGATION ---
st.sidebar.markdown("---")
page = st.sidebar.radio("Main Menu", ["Dockyard Management", "Inventory & QR Tracking", "GPS & Fleet Tracking"])

# ==========================================
# PAGE 1: DOCKYARD MANAGEMENT
# ==========================================
if page == "Dockyard Management":
    st.title("🚛 Dockyard Management")
    st.markdown("Record real-time entry and exit timestamps for your fleet.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Log Truck Entry")
        entry_truck_id = st.text_input("Truck ID (Entry)")
        if st.button("Log Entry Timestamp", type="primary"):
            if entry_truck_id:
                new_entry = pd.DataFrame([{
                    "Truck_ID": entry_truck_id, 
                    "Entry_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "Exit_Time": "Pending", 
                    "Status": "At Dock"
                }])
                st.session_state['truck_logs'] = pd.concat([st.session_state['truck_logs'], new_entry], ignore_index=True)
                st.success(f"Truck {entry_truck_id} logged successfully at {datetime.now().strftime('%H:%M:%S')}")
            else:
                st.warning("Please enter a Truck ID.")

    with col2:
        st.subheader("Log Truck Exit")
        docked_trucks = st.session_state['truck_logs'][st.session_state['truck_logs']["Status"] == "At Dock"]["Truck_ID"].tolist()
        exit_truck_id = st.selectbox("Select Truck to Dispatch", ["Select a Truck"] + docked_trucks)
        
        if st.button("Log Exit Timestamp"):
            if exit_truck_id != "Select a Truck":
                idx = st.session_state['truck_logs'].index[st.session_state['truck_logs']['Truck_ID'] == exit_truck_id].tolist()[-1]
                st.session_state['truck_logs'].at[idx, "Exit_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['truck_logs'].at[idx, "Status"] = "Dispatched"
                st.success(f"Truck {exit_truck_id} exited at {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("---")
    st.subheader("Live Dockyard Activity Log")
    st.dataframe(st.session_state['truck_logs'])

# ==========================================
# PAGE 2: INVENTORY & QR TRACKING
# ==========================================
elif page == "Inventory & QR Tracking":
    st.title("📦 Inventory & Warehouse Tracing")
    st.markdown("Trace batch locations, receive times, and link them to dispatch trucks.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Scan/Receive New Batch")
        batch_qr = st.text_input("Batch QR / ID Code")
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
        dispatch_qr = st.selectbox("Select Batch QR to Dispatch", ["Select a Batch"] + in_stock)
        dispatch_truck = st.text_input("Assign to Truck ID")

        if st.button("Dispatch Inventory"):
            if dispatch_qr != "Select a Batch" and dispatch_truck:
                idx = st.session_state['inventory'].index[st.session_state['inventory']['Batch_QR'] == dispatch_qr].tolist()[0]
                st.session_state['inventory'].at[idx, "Time_Dispatched"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['inventory'].at[idx, "Dispatched_On_Truck"] = dispatch_truck
                st.session_state['inventory'].at[idx, "Status"] = "In Transit"
                st.success(f"Batch {dispatch_qr} dispatched on Truck {dispatch_truck}.")

    st.markdown("---")
    st.subheader("Warehouse Inventory Database")
    st.dataframe(st.session_state['inventory'])

# ==========================================
# PAGE 3: GPS & FLEET TRACKING
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & ETA Optimization")
    st.markdown("Track active fleet routes and calculate Estimated Time of Arrival.")

    # Mock data for demonstration purposes
    trucks_in_transit = ["TRK-901", "TRK-902", "TRK-903"]
    selected_truck = st.selectbox("Select Active Truck to Track", trucks_in_transit)

    # Simulating GPS Coordinates (Centered around Dubai)
    lat = 25.2048 + np.random.uniform(-0.05, 0.05)
    lon = 55.2708 + np.random.uniform(-0.05, 0.05)
    
    # Simulating ETA math
    distance_remaining = np.random.randint(15, 120) # km
    current_speed = np.random.randint(40, 85) # km/h
    eta_hours = distance_remaining / current_speed
    estimated_arrival = datetime.now() + timedelta(hours=eta_hours)

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Speed", f"{current_speed} km/h")
    col2.metric("Distance to Destination", f"{distance_remaining} km")
    col3.metric("Estimated Arrival (ETA)", estimated_arrival.strftime("%I:%M %p"))

    st.markdown("### Live Map Feed")
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(map_data, zoom=11)
