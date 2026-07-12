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

# --- HELPER FUNCTIONS & HIGH-RES ROUTING DATA ---
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
    if progress >= 1.0:
        return route[-1][0], route[-1][1]
    if progress <= 0.0:
        return route[0][0], route[0][1]
    
    total_segments = len(route) - 1
    cont_index = progress * total_segments
    idx = int(cont_index)
    frac = cont_index - idx
    
    lat1, lon1 = route[idx]
    lat2, lon2 = route[idx+1]
    
    curr_lat = lat1 + (lat2 - lat1) * frac
    curr_lon = lon1 + (lon2 - lon1) * frac
    return curr_lat, curr_lon

# --- GLOBAL AUTOREFRESH ---
st_autorefresh(interval=5000, limit=10000, key="global_autorefresh")

if 'trigger_sound' not in st.session_state:
    st.session_state['trigger_sound'] = None

if 'static_fleet_df' not in st.session_state:
    st.session_state['static_fleet_df'] = pd.DataFrame([
        {"Truck ID": "TRK-901", "Destination": "DXB Airport", "Status": "Active En Route"},
        {"Truck ID": "TRK-902", "Destination": "Dubai Mall", "Status": "Active En Route"},
        {"Truck ID": "TRK-903", "Destination": "Dubai Marina", "Status": "Active En Route"},
        {"Truck ID": "TRK-904", "Destination": "Al Maktoum Int", "Status": "Active En Route"},
        {"Truck ID": "TRK-905", "Destination": "Sharjah Ind", "Status": "Active En Route"}
    ])

now_init = datetime.now()
if 'fleet_state' not in st.session_state:
    st.session_state['fleet_state'] = [
        {"id": "TRK-901", "dest": "DXB Airport", "progress": 0.15, "traffic": "Moderate", "color": "#FFBF00", "speed": 62, "eta": (now_init + timedelta(minutes=int(0.85*180))).strftime("%I:%M %p")},
        {"id": "TRK-902", "dest": "Dubai Mall", "progress": 0.40, "traffic": "Heavy Traffic", "color": "#FF3333", "speed": 45, "eta": (now_init + timedelta(minutes=int(0.60*180))).strftime("%I:%M %p")},
        {"id": "TRK-903", "dest": "Dubai Marina", "progress": 0.65, "traffic": "Clear", "color": "#00FF55", "speed": 85, "eta": (now_init + timedelta(minutes=int(0.35*180))).strftime("%I:%M %p")},
        {"id": "TRK-904", "dest": "Al Maktoum Int", "progress": 0.20, "traffic": "Clear", "color": "#00FF55", "speed": 78, "eta": (now_init + timedelta(minutes=int(0.80*180))).strftime("%I:%M %p")},
        {"id": "TRK-905", "dest": "Sharjah Ind", "progress": 0.80, "traffic": "Moderate", "color": "#FFBF00", "speed": 55, "eta": (now_init + timedelta(minutes=int(0.20*180))).strftime("%I:%M %p")}
    ]

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

for t in st.session_state['fleet_state']:
    t['progress'] += random.uniform(0.002, 0.006)
    if t['progress'] >= 1.0:
        t['progress'] = 0.05  
        
    t['speed'] = random.randint(45, 90)
    minutes_left = int((1.0 - t['progress']) * 180)
    t['eta'] = (now + timedelta(minutes=minutes_left)).strftime("%I:%M %p") if t['progress'] <= 0.95 else "Arriving"

if (now - st.session_state['last_auto_update']).total_seconds() >= 58:  
    st.session_state['last_auto_update'] = now
    locations = ["Whse A - Dock 1", "Whse A - Dock 2", "Whse B - Dock 1", "Whse C - Heavy Freight"]
    
    if st.session_state['auto_toggle'] == "entry":
        auto_truck_id = f"TRK-{random.randint(1000, 9999)}"
        new_entry = pd.DataFrame([{
            "Truck_ID": auto_truck_id, "Entry_Time": now.strftime("%Y-%m-%d %H:%M:%S"), 
            "Exit_Time": "Pending", "Warehouse_Location": random.choice(locations),
            "Status": "At Dock", "Last_Updated": now.strftime("%Y-%m-%d %H:%M:%S")
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
    
    css_animations = f"""
    {audio_tag}
    <style>
    @keyframes blink-animation-cyan {{ 0% {{ background-color: #00D2FF; color: #000000; }} 50% {{ background-color: transparent; color: #C5C6C7; }} 100% {{ background-color: #00D2FF; color: #000000; }} }}
    @keyframes blink-animation-green {{ 0% {{ background-color: #00FF55; color: #000000; }} 50% {{ background-color: transparent; color: #C5C6C7; }} 100% {{ background-color: #00FF55; color: #000000; }} }}
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
    for _, row in df[df["Status"] == "At Dock"].iterrows():
        time_diff = (now - datetime.strptime(row['Last_Updated'], "%Y-%m-%d %H:%M:%S")).total_seconds()
        row_class = "blinking-row-cyan" if time_diff < 15 else ""
        html_docked += f"<tr class='{row_class}'><td>{row['Truck_ID']}</td><td>{row['Entry_Time']}</td><td>{row['Exit_Time']}</td><td>{row['Warehouse_Location']}</td><td>{row['Status']}</td></tr>"
    html_docked += "</tbody></table>"
    st.markdown(html_docked, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔴 Dispatched Log")
    html_dispatched = f"<table class='custom-table'><thead><tr><th>Truck ID</th><th>Entry Time</th><th>Exit Time</th><th>Location</th><th>Status</th></tr></thead><tbody>"
    for _, row in df[df["Status"] == "Dispatched"].iterrows():
        time_diff = (now - datetime.strptime(row['Last_Updated'], "%Y-%m-%d %H:%M:%S")).total_seconds()
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
    st.dataframe(st.session_state['inventory'])
    render_footer()

# ==========================================
# PAGE 3: GPS & FLEET TRACKING
# ==========================================
elif page == "GPS & Fleet Tracking":
    st.title("🛰️ Live GPS & Route Tracing")
    st.markdown("Real-time telemetry, dynamic traffic conditions, and ETA tracking for active fleets.")
    st.markdown("👉 **Click directly on a Truck ID row in the table to view its live route!**")

    fleet_data = []
    for d in st.session_state['fleet_state']:
        route_coords = real_routes[d["dest"]]
        c_lat, c_lon = get_interpolated_pos(route_coords, d["progress"])
        fleet_data.append({
            "Truck": d["id"], "Destination": d["dest"],
            "start_lat": route_coords[0][0], "start_lon": route_coords[0][1],
            "curr_lat": c_lat, "curr_lon": c_lon,
            "dest_lat": route_coords[-1][0], "dest_lon": route_coords[-1][1],
            "speed": d["speed"], "Traffic Condition": d["traffic"],
            "Route Color": d["color"], "ETA": d["eta"]
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
        st.subheader(f"📡 Focus Target: {selected_truck}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Speed", f"{live_data['speed']} km/h")
        col2.metric("Traffic Route", live_data['Traffic Condition'])
        col3.metric("Live ETA", live_data['ETA'])
        col4.metric("Destination", live_data['Destination'])
    else:
        st.subheader("📡 Satellite Telemetry: All Active Fleet")
    
    # THE FIX: We provide the correct zoom/center EVERY loop, but rely on uirevision 
    # to block it from resetting your manual panning!
    if selected_truck == "All Active Fleet":
        map_zoom = 9
        map_center = {"lat": 25.12, "lon": 55.20}
        plot_data = fleet_data
    else:
        plot_data = [d for d in fleet_data if d["Truck"] == selected_truck]
        map_zoom = 11.5
        map_center = {"lat": plot_data[0]["curr_lat"], "lon": plot_data[0]["curr_lon"]}

    fig = go.Figure()
    
    for d in plot_data:
        line_color = d['Route Color'] if selected_truck != "All Active Fleet" else 'rgba(255, 255, 255, 0.2)'
        route_coords = real_routes[d['Destination']]
        
        fig.add_trace(go.Scattermap(
            mode="lines",
            lon=[p[1] for p in route_coords], lat=[p[0] for p in route_coords],
            line=dict(width=5, color=line_color), hoverinfo='none'
        ))
        
        if selected_truck != "All Active Fleet":
            fig.add_trace(go.Scattermap(
                mode="markers+text",
                lon=[d['start_lon']], lat=[d['start_lat']],
                marker=dict(size=14, color='white'),
                text="Departure: StormNode Hub", textposition="bottom center",
                textfont=dict(color="white", size=14, weight="bold"), name="Departure", hoverinfo='text'
            ))
            fig.add_trace(go.Scattermap(
                mode="markers+text",
                lon=[d['dest_lon']], lat=[d['dest_lat']],
                marker=dict(size=14, color='#00FF55'),
                text=f"Arrival: {d['Destination']}", textposition="top center",
                textfont=dict(color="#00FF55", size=14, weight="bold"), name="Arrival", hoverinfo='text'
            ))

        marker_text = f"<b>{d['Truck']}</b><br>Traffic: {d['Traffic Condition']}<br>Speed: {d['speed']} km/h<br>ETA: {d['ETA']}"
        fig.add_trace(go.Scattermap(
            mode="markers",
            lon=[d['curr_lon']], lat=[d['curr_lat']],
            marker=dict(size=18, color='#00D2FF'),
            name=d['Truck'], text=marker_text, hoverinfo='text'
        ))

    # THE FIX: uirevision handles the camera state safely now.
    fig.update_layout(
        map=dict(
            style="carto-darkmatter",
            zoom=map_zoom,
            center=map_center
        ),
        uirevision=selected_truck,
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False,
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)
    render_footer()

# ==========================================
# PAGE 4: ABOUT STORMNODE
# ==========================================
elif page == "About StormNode":
    st.title("⚡ About StormNode Logistics")
    st.markdown("### Powering the Connected Supply Chain")
    st.image("https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=1200&q=80", caption="StormNode Next-Generation Fulfillment Center")
    st.markdown("---")
    
    st.subheader("Global Operations At A Glance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Daily Freight Volume", "4,850 Tons", "+12% this week")
    col2.metric("Active Supply Nodes", "244", "+3 active")
    col3.metric("Fleet Efficiency", "94.2%", "+1.5%")
    col4.metric("System Uptime", "99.999%", "Optimal")
    
    st.markdown("---")
    st.markdown("""
    **StormNode Logistics** is a next-generation freight and warehousing platform designed to bridge the gap between heavy physical freight and cutting-edge digital infrastructure. 
    
    Founded in 2026, our mission is to completely eliminate supply chain opacity. Traditional logistics rely on manual data entry, fractured communication, and fragmented tracking systems. At StormNode, we treat every warehouse, dispatch truck, and cargo batch as a vital "node" in a highly connected, automated neural network.
    """)
    
    st.markdown("### Platform Capabilities")
    with st.expander("🏭 Automated Dockyard Management", expanded=True):
        st.write("Real-time sensor integration automates entry logs, dispatch clearances, and staging bay allocations. By utilizing edge-computing at the gates, we eliminate gatehouse bottlenecks, manual processing delays, and driver wait times.")
    with st.expander("📦 Inventory & Granular QR Tracing"):
        st.write("High-fidelity tracing ties exact physical bin locations to active transport routes. Our system ensures 100% chain-of-custody compliance from receipt at the dock to final delivery, reducing lost stock by 98%.")
    with st.expander("🛰️ Neural Routing & Telemetry"):
        st.write("GPS fleet monitoring tracks transit progression dynamically over active satellite overlays. Machine learning algorithms adjust arrival ETAs for predictive warehouse receiving and optimize fuel routes around active traffic events.")
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
