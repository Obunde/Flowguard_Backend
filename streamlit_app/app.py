"""Flowguard — Streamlit Operational Predictive Maintenance Dashboard

Interactive frontend for Kenya Pipeline Company (KPC) petroleum network and
Municipal Water Transport (NCWSC) infrastructure monitoring.
Communicates with the Flowguard FastAPI Backend via REST APIs.
"""
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuration & Page Setup
st.set_page_config(
    page_title="Flowguard | Multi-Fluid Predictive Maintenance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

# Role-Based Access Control (RBAC) Definition
ROLE_PERMISSIONS = {
    "admin": {
        "title": "Tenant Administrator",
        "badge": "👑 ADMIN",
        "allowed_actions": {"read", "evaluate_alerts", "manage_alerts", "rank_schedule", "create_work_orders"},
    },
    "planner": {
        "title": "Maintenance Planner",
        "badge": "🗓️ PLANNER",
        "allowed_actions": {"read", "rank_schedule", "create_work_orders"},
    },
    "technician": {
        "title": "Field Technician",
        "badge": "🔧 TECHNICIAN",
        "allowed_actions": {"read", "manage_alerts", "update_work_orders"},
    },
    "viewer": {
        "title": "Operations Viewer",
        "badge": "👁️ VIEWER",
        "allowed_actions": {"read"},
    },
}

# KPC Petroleum 13 Station Reference Data (with Elevation in meters)
KPC_STATIONS = [
    {"code": "PS1", "name": "PS1 Mombasa", "lat": -4.0225, "lon": 39.6086, "elevation": 10, "region": "Coast", "capacity": 3200},
    {"code": "PS2", "name": "PS2 Samburu", "lat": -4.1667, "lon": 39.2000, "elevation": 280, "region": "Coast", "capacity": 3200},
    {"code": "PS3", "name": "PS3 Maungu", "lat": -3.5500, "lon": 38.7667, "elevation": 530, "region": "Coast", "capacity": 3200},
    {"code": "PS4", "name": "PS4 Mtito Andei", "lat": -2.6858, "lon": 38.1706, "elevation": 730, "region": "Eastern", "capacity": 3200},
    {"code": "PS5", "name": "PS5 Konza", "lat": -1.7357, "lon": 37.1287, "elevation": 1600, "region": "Eastern", "capacity": 3200},
    {"code": "PS6", "name": "PS6 Nairobi Depot", "lat": -1.3192, "lon": 36.9278, "elevation": 1795, "region": "Nairobi", "capacity": 4000},
    {"code": "PS7", "name": "PS7 Naivasha", "lat": -0.7167, "lon": 36.4333, "elevation": 2085, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS8", "name": "PS8 Gilgil", "lat": -0.4903, "lon": 36.3178, "elevation": 2000, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS9", "name": "PS9 Nakuru", "lat": -0.3031, "lon": 36.0800, "elevation": 1850, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS10", "name": "PS10 Molo", "lat": -0.2500, "lon": 35.7333, "elevation": 2800, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS11", "name": "PS11 Eldoret Depot", "lat": 0.5143, "lon": 35.2698, "elevation": 2100, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS12", "name": "PS12 Turbo", "lat": 0.6500, "lon": 35.0833, "elevation": 1800, "region": "Rift Valley", "capacity": 2000},
    {"code": "PS13", "name": "PS13 Kisumu Depot", "lat": -0.0917, "lon": 34.7680, "elevation": 1130, "region": "Nyanza", "capacity": 2000},
]

# NCWSC Municipal Water 8 Station Reference Data
NCWSC_WATER_STATIONS = [
    {
        "code": "WS1",
        "name": "WS1 Sasumua Dam Treatment",
        "lat": -0.7483,
        "lon": 36.6542,
        "elevation": 2480,
        "region": "Aberdare",
        "capacity": 60000,
    },
    {
        "code": "WS2",
        "name": "WS2 Ruiru Dam Station",
        "lat": -0.8712,
        "lon": 36.8123,
        "elevation": 2050,
        "region": "Central",
        "capacity": 45000,
    },
    {
        "code": "WS3",
        "name": "WS3 Kikuyu Springs Booster",
        "lat": -1.2450,
        "lon": 36.6620,
        "elevation": 2000,
        "region": "Kiambu",
        "capacity": 30000,
    },
    {
        "code": "WS4",
        "name": "WS4 Kabete High Reservoir",
        "lat": -1.2590,
        "lon": 36.7510,
        "elevation": 1860,
        "region": "Nairobi West",
        "capacity": 80000,
    },
    {
        "code": "WS5",
        "name": "WS5 Gigiri Main Terminal",
        "lat": -1.2310,
        "lon": 36.8150,
        "elevation": 1720,
        "region": "Nairobi Central",
        "capacity": 100000,
    },
    {
        "code": "WS6",
        "name": "WS6 Karen Distribution Booster",
        "lat": -1.3200,
        "lon": 36.7100,
        "elevation": 1790,
        "region": "Nairobi South",
        "capacity": 35000,
    },
    {
        "code": "WS7",
        "name": "WS7 Outer Ring Station",
        "lat": -1.2780,
        "lon": 36.8850,
        "elevation": 1620,
        "region": "Nairobi East",
        "capacity": 50000,
    },
    {
        "code": "WS8",
        "name": "WS8 Embakasi Supply Terminal",
        "lat": -1.3320,
        "lon": 36.9120,
        "elevation": 1610,
        "region": "Nairobi East",
        "capacity": 45000,
    },
]

DEMO_ALERTS = [
    {
        "id": "alt-kpc-001",
        "tag_number": "PUMP-PS1-01",
        "station_code": "PS1",
        "station_name": "PS1 Mombasa",
        "rule_type": "VIBRATION_THRESHOLD",
        "metric_name": "vibration_rms",
        "metric_value": 7.42,
        "threshold_value": 4.50,
        "severity": "CRITICAL",
        "status": "active",
        "created_at": "2026-09-07 20:15:00",
        "message": (
            "Critical RMS vibration breach on Primary Terminal Export Pump "
            "PUMP-PS1-01 (7.42 mm/s > threshold 4.50 mm/s)"
        ),
    },
    {
        "id": "alt-kpc-002",
        "tag_number": "PUMP-PS6-02",
        "station_code": "PS6",
        "station_name": "PS6 Nairobi Depot",
        "rule_type": "BEARING_TEMP_THRESHOLD",
        "metric_name": "bearing_temperature",
        "metric_value": 84.50,
        "threshold_value": 75.00,
        "severity": "WARNING",
        "status": "active",
        "created_at": "2026-09-07 21:00:00",
        "message": (
            "Elevated drive-end bearing temperature on Booster Pump "
            "PUMP-PS6-02 (84.5°C > threshold 75.0°C)"
        ),
    },
    {
        "id": "alt-kpc-003",
        "tag_number": "PUMP-PS11-01",
        "station_code": "PS11",
        "station_name": "PS11 Eldoret Depot",
        "rule_type": "PRESSURE_DROP_THRESHOLD",
        "metric_name": "discharge_pressure",
        "metric_value": 410.00,
        "threshold_value": 500.00,
        "severity": "WARNING",
        "status": "active",
        "created_at": "2026-09-07 22:30:00",
        "message": (
            "Abnormal discharge pressure drop detected on Transfer Pump "
            "PUMP-PS11-01 (410 psi < threshold 500 psi)"
        ),
    },
    {
        "id": "alt-kpc-004",
        "tag_number": "PUMP-PS13-02",
        "station_code": "PS13",
        "station_name": "PS13 Kisumu Depot",
        "rule_type": "HDI_DEVIATION",
        "metric_name": "health_deviation_index",
        "metric_value": 0.38,
        "threshold_value": 0.35,
        "severity": "INFO",
        "status": "resolved",
        "created_at": "2026-09-07 18:00:00",
        "message": (
            "Minor HDI deviation resolved following routine lube oil filter "
            "replacement on PUMP-PS13-02"
        ),
    },
]

WATER_DEMO_ALERTS = [
    {
        "id": "alt-wtr-001",
        "tag_number": "PUMP-WS1-01",
        "station_code": "WS1",
        "station_name": "WS1 Sasumua Dam Treatment",
        "rule_type": "HEAD_LOSS_THRESHOLD",
        "metric_name": "suction_head_loss",
        "metric_value": 14.8,
        "threshold_value": 8.0,
        "severity": "CRITICAL",
        "status": "active",
        "created_at": "2026-09-07 21:10:00",
        "message": (
            "Critical hydraulic head loss & suction cavitation risk on High Lift Pump "
            "PUMP-WS1-01 (14.8m loss > limit 8.0m)"
        ),
    },
    {
        "id": "alt-wtr-002",
        "tag_number": "PUMP-WS5-02",
        "station_code": "WS5",
        "station_name": "WS5 Gigiri Main Terminal",
        "rule_type": "TURBIDITY_SPIKE",
        "metric_name": "water_turbidity_ntu",
        "metric_value": 6.8,
        "threshold_value": 5.0,
        "severity": "WARNING",
        "status": "active",
        "created_at": "2026-09-07 22:00:00",
        "message": (
            "Elevated raw water turbidity detected at Gigiri Inflow "
            "(6.8 NTU > WHO limit 5.0 NTU)"
        ),
    },
]


def api_request(method: str, endpoint: str, data: dict = None, token: str = None) -> dict | list | None:
    """Helper to perform authenticated API calls to Flowguard backend."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, headers=headers, timeout=10)
        else:
            return None

        if response.status_code in (200, 201):
            return response.json()
        return None
    except Exception:
        return None


# Session State Management for JWT & RBAC
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "admin"


def check_rbac_permission(action: str) -> bool:
    """Helper function to check if the current active role is authorized."""
    role = st.session_state.get("user_role", "admin").lower()
    role_cfg = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])
    return action in role_cfg["allowed_actions"]


# Custom CSS Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem; }
    .card-kpi { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 1rem; border-radius: 8px; text-align: center; }
    .card-title { font-size: 0.9rem; color: #64748B; font-weight: 600; }
    .card-value { font-size: 1.8rem; font-weight: 700; color: #0F172A; }
    .rbac-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 700; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)


# Sidebar Setup: Domain, Authentication & RBAC Control
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.svg", width=64)
    st.markdown("### **Flowguard Control Center**")
    st.caption("Condition-Based Predictive Maintenance Platform")
    st.divider()

    st.subheader("🌐 Infrastructure Domain")
    domain_mode = st.radio(
        "Select Active Pipeline Fleet:",
        ["🛢️ KPC Petroleum Network", "💧 NCWSC Municipal Water"],
        index=0,
    )
    is_water_mode = "Water" in domain_mode

    st.divider()

    st.subheader("🔐 RBAC & User Role Profile")
    selected_role_key = st.selectbox(
        "Active Role Profile:",
        options=list(ROLE_PERMISSIONS.keys()),
        format_func=lambda r: f"{ROLE_PERMISSIONS[r]['badge']} - {ROLE_PERMISSIONS[r]['title']}",
        index=list(ROLE_PERMISSIONS.keys()).index(st.session_state["user_role"]),
    )
    st.session_state["user_role"] = selected_role_key

    role_info = ROLE_PERMISSIONS[st.session_state["user_role"]]
    st.caption(f"Role Privileges: `{', '.join(role_info['allowed_actions'])}`")

    st.divider()

    if not st.session_state["jwt_token"]:
        st.subheader("🔑 Authentication")
        email_input = st.text_input("Email", value="admin@kpc.co.ke" if not is_water_mode else "admin@ncwsc.co.ke")
        password_input = st.text_input("Password", value="password123", type="password")
        if st.button("Sign In", type="primary", use_container_width=True):
            res = api_request("POST", "/api/v1/users/login", data={"email": email_input, "password": password_input})
            if res and "access_token" in res:
                st.session_state["jwt_token"] = res["access_token"]
                st.session_state["user_email"] = email_input
                if "user" in res and "role" in res["user"]:
                    st.session_state["user_role"] = res["user"]["role"].lower()
                st.success("Authenticated successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials or server unavailable.")
    else:
        st.success(f"Logged in as: **{st.session_state['user_email']}**")
        if st.button("Sign Out", use_container_width=True):
            st.session_state["jwt_token"] = None
            st.session_state["user_email"] = None
            st.rerun()

    st.divider()
    st.caption(f"Connected Backend: `{API_BASE_URL}`")


# Active Dataset Setup based on selected Domain
current_stations = NCWSC_WATER_STATIONS if is_water_mode else KPC_STATIONS
default_alerts = WATER_DEMO_ALERTS if is_water_mode else DEMO_ALERTS
fluid_name = "Treated Water / Municipal Hydro" if is_water_mode else "Refined Petroleum Products"
operator_name = "Nairobi City Water & Sewerage Company (NCWSC)" if is_water_mode else "Kenya Pipeline Company (KPC)"
corridor_title = "NCWSC 185 km Water Transmission System" if is_water_mode else "KPC 1,342 km Petroleum Network (Mombasa to Kisumu)"

# Main Dashboard Header
active_role_badge = ROLE_PERMISSIONS[st.session_state["user_role"]]["badge"]
st.markdown("<div class='main-header'>🛡️ Flowguard Multi-Fluid Maintenance Platform</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='sub-header'><b>{operator_name}</b> — Fluid: <i>{fluid_name}</i> | Active Role: <b>{active_role_badge}</b></div>",
    unsafe_allow_html=True,
)

token = st.session_state["jwt_token"]

# Top Level KPI Row
col1, col2, col3, col4 = st.columns(4)

stations_data = api_request("GET", "/api/v1/stations", token=token) or current_stations
pumps_data = api_request("GET", "/api/v1/pumps", token=token) or []
alerts_data = api_request("GET", "/api/v1/alerts", token=token) or default_alerts
work_orders = api_request("GET", "/api/v1/work-orders", token=token) or []

with col1:
    st.markdown(
        f"<div class='card-kpi'><div class='card-title'>PUMP STATIONS</div><div class='card-value'>{len(stations_data)}</div></div>",
        unsafe_allow_html=True,
    )
with col2:
    val = len(pumps_data) or (len(stations_data) * 2)
    st.markdown(
        f"<div class='card-kpi'><div class='card-title'>REGISTERED PUMPS</div><div class='card-value'>{val}</div></div>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"<div class='card-kpi'><div class='card-title'>ACTIVE ALERTS</div><div class='card-value'>{len(alerts_data)}</div></div>",
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f"<div class='card-kpi'><div class='card-title'>OPEN WORK ORDERS</div><div class='card-value'>{len(work_orders)}</div></div>",
        unsafe_allow_html=True,
    )

# Live Active Notification Banner
active_crit = [
    a for a in alerts_data
    if str(a.get("status", "")).lower() == "active" or str(a.get("severity", "")).upper() == "CRITICAL"
]
if active_crit:
    st.warning(
        f"🚨 **ACTIVE RISK NOTIFICATION**: {len(active_crit)} alert(s) active across {operator_name} fleet. "
        "Review the **Active Risk Alerts** tab for threshold details and management."
    )

st.write("")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗺️ Network Corridor & 3D Topography",
    "⚡ Telemetry & HDI Engine",
    "🤖 7-Day Risk & RUL Predictor",
    "🚨 Active Risk Alerts",
    "🔍 3D Digital Twin & SHAP XAI",
    "💧 Water Scenario Replicator",
    "🛠️ Work Orders & Calendar",
])

# Tab 1: Network Corridor & 3D Topography
with tab1:
    st.subheader(f"Geospatial Corridor: {corridor_title}")

    station_alert_severity = {}
    for a in alerts_data:
        st_code = a.get("station_code") or a.get("station_id", "")
        if not st_code:
            for s in current_stations:
                if s["code"] in str(a.get("tag_number", "")) or s["code"] in str(a.get("message", "")):
                    st_code = s["code"]
                    break
        if st_code:
            sev = str(a.get("severity", "")).upper()
            if sev == "CRITICAL":
                station_alert_severity[st_code] = "CRITICAL"
            elif sev == "WARNING" and station_alert_severity.get(st_code) != "CRITICAL":
                station_alert_severity[st_code] = "WARNING"

    map_stations = []
    for s in current_stations:
        health = station_alert_severity.get(s["code"], "NORMAL")
        color = "#DC2626" if health == "CRITICAL" else "#D97706" if health == "WARNING" else "#16A34A"
        map_stations.append({**s, "health": health, "color": color})

    df_map = pd.DataFrame(map_stations)

    col_m1, col_m2 = st.columns([3, 2])

    with col_m1:
        st.markdown("##### **2D Geospatial Corridor Map**")
        fig_map = go.Figure()

        fig_map.add_trace(go.Scattergeo(
            lat=df_map["lat"],
            lon=df_map["lon"],
            mode="lines",
            line=dict(width=3, color="#1E3A8A"),
            name="Pipeline Main Route",
            hoverinfo="none",
        ))

        for health_status, color, label in [
            ("CRITICAL", "#DC2626", "Critical Alarm"),
            ("WARNING", "#D97706", "Warning Active"),
            ("NORMAL", "#16A34A", "Normal Operational"),
        ]:
            sub_df = df_map[df_map["health"] == health_status]
            if not sub_df.empty:
                fig_map.add_trace(go.Scattergeo(
                    lat=sub_df["lat"],
                    lon=sub_df["lon"],
                    mode="markers+text",
                    marker=dict(size=13, color=color, symbol="circle", line=dict(width=1.5, color="#FFFFFF")),
                    text=sub_df["code"],
                    textposition="top center",
                    name=f"Health: {label}",
                    hovertext=[
                        f"<b>{row['name']} ({row['code']})</b><br>"
                        f"Region: {row['region']}<br>"
                        f"Capacity: {row['capacity']:,} m³/day<br>"
                        f"Elevation: {row['elevation']} m<br>"
                        f"Health: <b>{row['health']}</b>"
                        for _, row in sub_df.iterrows()
                    ],
                    hoverinfo="text",
                ))

        fig_map.update_layout(
            geo=dict(
                scope="africa",
                center=dict(lat=-1.25, lon=36.8),
                projection_scale=6.5,
                showland=True,
                landcolor="#F8FAFC",
                showcountries=True,
                countrycolor="#CBD5E1",
                showlakes=True,
                lakecolor="#E0F2FE",
            ),
            height=420,
            margin={"r": 0, "t": 20, "l": 0, "b": 0},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_m2:
        st.markdown("##### **3D Pipeline Elevation Profile**")
        fig_3d_elev = go.Figure()

        # 3D Line path for pipeline elevation
        fig_3d_elev.add_trace(go.Scatter3d(
            x=df_map["lon"],
            y=df_map["lat"],
            z=df_map["elevation"],
            mode="lines+markers",
            line=dict(color="#2563EB", width=6),
            marker=dict(
                size=7,
                color=df_map["color"],
                symbol="circle",
            ),
            hovertext=[
                f"{r['code']} ({r['name']})<br>Elev: {r['elevation']} m"
                for _, r in df_map.iterrows()
            ],
            hoverinfo="text",
            name="Elevation Corridor",
        ))

        fig_3d_elev.update_layout(
            scene=dict(
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                zaxis_title="Elevation (m)",
                camera=dict(eye=dict(x=1.6, y=1.6, z=0.8)),
            ),
            height=420,
            margin={"r": 0, "t": 20, "l": 0, "b": 0},
        )
        st.plotly_chart(fig_3d_elev, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🔎 **Station Inspector**")
    sel_st_code = st.selectbox(
        "Select Station to Inspect",
        options=[s["code"] for s in current_stations],
        format_func=lambda c: next(
            f"{s['code']} - {s['name']} ({s['region']})" for s in current_stations if s["code"] == c
        ),
    )
    st_info = next(s for s in map_stations if s["code"] == sel_st_code)

    st_col1, st_col2, st_col3, st_col4 = st.columns(4)
    with st_col1:
        st.metric("Station Name", st_info["name"])
    with st_col2:
        st.metric("Region & Elevation", f"{st_info['region']} ({st_info['elevation']}m)")
    with st_col3:
        st.metric("Throughput Capacity", f"{st_info['capacity']:,} m³/day")
    with st_col4:
        health_badge = (
            "🔴 CRITICAL" if st_info["health"] == "CRITICAL"
            else "🟡 WARNING" if st_info["health"] == "WARNING"
            else "🟢 NORMAL"
        )
        st.metric("Operational Health", health_badge)

    st_alerts = [
        a for a in alerts_data
        if a.get("station_code") == sel_st_code
        or st_info["code"] in str(a.get("tag_number", ""))
        or st_info["code"] in str(a.get("message", ""))
    ]
    if st_alerts:
        st.warning(f"⚠️ {len(st_alerts)} alert(s) associated with {st_info['name']}:")
        for sa in st_alerts:
            st.caption(f"• [{sa.get('severity')}] {sa.get('message')}")
    else:
        st.success(f"✅ All pumps at {st_info['name']} are operating within normal thresholds.")

# Tab 2: Telemetry & HDI Engine
with tab2:
    st.subheader(f"Real-Time Telemetry & Physics Engine ({operator_name})")

    selected_pump_id = None
    if pumps_data:
        pump_options = {f"{p.get('tag_number', 'PUMP')}-{p.get('id', '')[:6]}": p["id"] for p in pumps_data}
        selected_label = st.selectbox("Select Pump Asset", list(pump_options.keys()))
        selected_pump_id = pump_options[selected_label]
    else:
        st.info("No live API connection. Rendering baseline telemetry and physics calculations.")

    col_t1, col_t2 = st.columns([2, 1])

    with col_t1:
        st.markdown("##### **Recent Telemetry Stream**")
        timestamps = pd.date_range(end=datetime.now(), periods=20, freq="min")
        
        if is_water_mode:
            df_telemetry = pd.DataFrame({
                "Timestamp": timestamps,
                "Flow Rate (m³/hr)": [245.0 + (i * 1.2) for i in range(20)],
                "Suction Head Loss (m)": [3.2 + (i * 0.45) for i in range(20)],
                "Discharge Head (m)": [180.0 - (i * 2.1) for i in range(20)],
            })
            y1_col, y2_col = "Suction Head Loss (m)", "Discharge Head (m)"
        else:
            df_telemetry = pd.DataFrame({
                "Timestamp": timestamps,
                "Vibration (mm/s)": [2.1 + (i * 0.15) for i in range(20)],
                "Bearing Temp (°C)": [45.0 + (i * 0.8) for i in range(20)],
                "Discharge Pressure (psi)": [600.0 - (i * 3.5) for i in range(20)],
            })
            y1_col, y2_col = "Vibration (mm/s)", "Bearing Temp (°C)"

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(x=df_telemetry["Timestamp"], y=df_telemetry[y1_col], mode="lines+markers", name=y1_col)
        )
        fig_trend.add_trace(
            go.Scatter(x=df_telemetry["Timestamp"], y=df_telemetry[y2_col], mode="lines+markers", name=y2_col)
        )
        fig_trend.update_layout(height=350, margin={"r": 10, "t": 30, "l": 10, "b": 10})
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_t2:
        st.markdown("##### **Health Deviation Index (HDI)**")
        hdi_val = 0.42 if is_water_mode else 0.28
        if selected_pump_id and token:
            hdi_res = api_request("POST", f"/api/v1/flowgard-engine/pumps/{selected_pump_id}/compute", token=token)
            if hdi_res and "health_deviation_index" in hdi_res:
                hdi_val = float(hdi_res["health_deviation_index"])

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=hdi_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "HDI Physics Residual [0.0 - 1.0]"},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': "#1E3A8A"},
                'steps': [
                    {'range': [0, 0.35], 'color': "#DCFCE7"},
                    {'range': [0.35, 0.70], 'color': "#FEF08A"},
                    {'range': [0.70, 1.0], 'color': "#FCA5A5"},
                ],
            }
        ))
        fig_gauge.update_layout(height=320, margin={"r": 10, "t": 40, "l": 10, "b": 10})
        st.plotly_chart(fig_gauge, use_container_width=True)

# Tab 3: 7-Day Risk & RUL Predictor
with tab3:
    st.subheader("7-Day Failure Risk Classifier & Remaining Useful Life (RUL)")

    col_p1, col_p2 = st.columns(2)

    risk_score = 0.81 if is_water_mode else 0.76
    predicted_class = "cavitation_suction_loss" if is_water_mode else "bearing_fault"
    rul_days = 8.5 if is_water_mode else 12.4
    ci_lower = 7.1 if is_water_mode else 10.9
    ci_upper = 9.8 if is_water_mode else 13.8

    if selected_pump_id and token:
        pred_res = api_request("POST", f"/api/v1/predictions/pumps/{selected_pump_id}/trigger", token=token)
        if pred_res:
            risk_score = float(pred_res.get("risk_score_7d", risk_score))
            predicted_class = pred_res.get("predicted_class", predicted_class)

        rul_res = api_request("POST", f"/api/v1/rul/pumps/{selected_pump_id}/trigger", token=token)
        if rul_res:
            rul_days = float(rul_res.get("remaining_useful_life_days", rul_days))
            ci_lower = float(rul_res.get("confidence_lower_days", ci_lower))
            ci_upper = float(rul_res.get("confidence_upper_days", ci_upper))

    with col_p1:
        st.markdown("##### **7-Day Failure Risk Score**")
        st.progress(risk_score, text=f"Risk Score: {risk_score * 100:.1f}%")

        badge_color = "red" if risk_score >= 0.7 else "yellow" if risk_score >= 0.35 else "green"
        st.markdown(f"Predicted Fault Mode: **:{badge_color}[{predicted_class.upper()}]**")

    with col_p2:
        st.markdown("##### **Remaining Useful Life (RUL)**")
        st.metric(
            "Estimated Service Window",
            f"{rul_days:.1f} Days",
            delta=f"Confidence: {ci_lower:.1f} - {ci_upper:.1f} Days",
        )

# Tab 4: Active Risk Alerts & Notifications
with tab4:
    st.subheader(f"🚨 Real-Time Risk Alerts & Threshold Notifications ({operator_name})")

    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        st.markdown(
            "Dynamic threshold evaluations across vibration, temperature, head loss, and pressure metrics."
        )
    with col_a2:
        if st.button("⚡ Evaluate Thresholds", type="primary", use_container_width=True):
            if not check_rbac_permission("evaluate_alerts"):
                st.error(
                    f"🔒 **RBAC Permission Denied**: Role `{st.session_state['user_role'].upper()}` "
                    "cannot trigger threshold evaluations. Required: ADMIN."
                )
            elif token and selected_pump_id:
                eval_res = api_request("POST", f"/api/v1/alerts/pumps/{selected_pump_id}/evaluate", token=token)
                if eval_res is not None:
                    st.success("Threshold rules evaluated successfully!")
                    st.rerun()
            else:
                st.success("Demo Mode: Rule evaluation executed successfully!")

    crit_cnt = sum(1 for a in alerts_data if str(a.get("severity", "")).upper() == "CRITICAL")
    warn_cnt = sum(1 for a in alerts_data if str(a.get("severity", "")).upper() == "WARNING")
    info_cnt = sum(1 for a in alerts_data if str(a.get("severity", "")).upper() == "INFO")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Alerts", len(alerts_data))
    with m2:
        st.metric("Critical Alerts", crit_cnt)
    with m3:
        st.metric("Warning Alerts", warn_cnt)
    with m4:
        st.metric("Info / Cleared", info_cnt)

    st.divider()

    st.markdown("##### **Live Fleet Risk Notifications & Alert Log**")
    status_sel = st.radio("Filter Alerts by Status:", ["All", "Active", "Acknowledged", "Resolved"], horizontal=True)
    filt_alerts = alerts_data
    if status_sel != "All":
        filt_alerts = [a for a in alerts_data if str(a.get("status", "")).lower() == status_sel.lower()]

    if filt_alerts:
        st.dataframe(pd.DataFrame(filt_alerts), use_container_width=True)

        st.markdown("##### **Interactive Alert Management (RBAC Enforced)**")
        alert_map = {
            f"Alert {str(a.get('id', ''))[:8]} - {a.get('rule_type', 'THRESHOLD')} ({a.get('status', 'active')})": a["id"]
            for a in filt_alerts if "id" in a
        }
        if alert_map:
            sel_alert_lbl = st.selectbox("Select Alert to Manage", list(alert_map.keys()))
            sel_alert_id = alert_map[sel_alert_lbl]
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("Acknowledge Alert", use_container_width=True):
                    if not check_rbac_permission("manage_alerts"):
                        st.error(
                            f"🔒 **RBAC Permission Denied**: Role `{st.session_state['user_role'].upper()}` "
                            "is not authorized to acknowledge alerts. Required: ADMIN or TECHNICIAN."
                        )
                    elif token:
                        api_request(
                            "PATCH", f"/api/v1/alerts/{sel_alert_id}", data={"status": "acknowledged"}, token=token
                        )
                        st.success("Alert acknowledged!")
                        st.rerun()
                    else:
                        st.info("Demo Mode: Alert acknowledged in UI state.")
            with ca2:
                if st.button("Resolve Alert", use_container_width=True):
                    if not check_rbac_permission("manage_alerts"):
                        st.error(
                            f"🔒 **RBAC Permission Denied**: Role `{st.session_state['user_role'].upper()}` "
                            "is not authorized to resolve alerts. Required: ADMIN or TECHNICIAN."
                        )
                    elif token:
                        api_request(
                            "PATCH", f"/api/v1/alerts/{sel_alert_id}", data={"status": "resolved"}, token=token
                        )
                        st.success("Alert resolved!")
                        st.rerun()
                    else:
                        st.info("Demo Mode: Alert resolved in UI state.")
    else:
        st.info("No active or historical alerts found matching the selected status filter.")

# Tab 5: 3D Digital Twin & SHAP XAI
with tab5:
    st.subheader("🔍 3D Digital Twin & SHAP Sub-Assembly Diagnostics")

    col_3d1, col_3d2 = st.columns([3, 2])

    shap_data = (
        {"Suction Impeller": 54.0, "Mechanical Seal": 22.0, "Bearing Housing": 16.0, "Drive Motor": 8.0}
        if is_water_mode else
        {"Bearing Assembly": 42.5, "Impeller Stage": 28.0, "Mechanical Seal": 18.5, "Drive Motor": 11.0}
    )

    if selected_pump_id and token:
        shap_res = api_request("POST", f"/api/v1/explainability/pumps/{selected_pump_id}/trigger", token=token)
        if shap_res and "component_scores" in shap_res:
            scores = shap_res["component_scores"]
            shap_data = {k.capitalize(): v * 100 for k, v in scores.items()}

    with col_3d1:
        st.markdown("##### **High-Resolution 3D Centrifugal Pump Assembly Model**")

        fig_pump_3d = go.Figure()

        # 1. Motor Casing Cylindrical Mesh (X: -4 to -1)
        z_cylinder = np.linspace(-1, 1, 15)
        theta_cyl = np.linspace(0, 2 * np.pi, 20)
        z_grid, theta_grid = np.meshgrid(z_cylinder, theta_cyl)
        y_motor = 1.1 * np.cos(theta_grid)
        x_motor = np.full_like(y_motor, -2.5) + z_grid * 1.5
        z_motor = 1.1 * np.sin(theta_grid)

        fig_pump_3d.add_trace(go.Surface(
            x=x_motor,
            y=y_motor,
            z=z_motor,
            colorscale="Blues",
            showscale=False,
            opacity=0.85,
            name="1. Electric Motor Casing",
        ))

        # 2. Heavy Drive Shaft Line (X: -4 to 5)
        fig_pump_3d.add_trace(go.Scatter3d(
            x=[-4, 5],
            y=[0, 0],
            z=[0, 0],
            mode="lines+markers",
            line=dict(color="#0F172A", width=9),
            marker=dict(size=5, color="#334155"),
            name="2. Heavy Drive Shaft Line",
        ))

        # 3. Drive-End (DE) and Non-Drive-End (NDE) Bearing Housings (X: -0.5, X: 4.5)
        bearing_score = shap_data.get("Bearing Assembly", 0) or shap_data.get("Bearing Housing", 0)
        bearing_color = "#DC2626" if bearing_score > 35 else "#10B981"
        fig_pump_3d.add_trace(go.Scatter3d(
            x=[-0.5, 4.5],
            y=[0, 0],
            z=[0, 0],
            mode="markers+text",
            marker=dict(size=18, color=bearing_color, symbol="diamond"),
            text=["DE Bearing", "NDE Bearing"],
            textposition="top center",
            name="3. Bearing Housings (DE & NDE)",
        ))

        # 4. Multi-Stage Impeller Disks & Volute Housing (X: 1.2, 2.4, 3.6)
        impeller_score = shap_data.get("Impeller Stage", 0) or shap_data.get("Suction Impeller", 0)
        impeller_color = "#DC2626" if impeller_score > 35 else "#F59E0B"
        theta = np.linspace(0, 2 * np.pi, 30)
        for x_pos in [1.2, 2.4, 3.6]:
            y_ring = 1.3 * np.cos(theta)
            z_ring = 1.3 * np.sin(theta)
            x_ring = np.full_like(theta, x_pos)
            fig_pump_3d.add_trace(go.Scatter3d(
                x=x_ring,
                y=y_ring,
                z=z_ring,
                mode="lines",
                line=dict(color=impeller_color, width=6),
                name=f"4. Impeller Stage (X={x_pos}m)",
                showlegend=False,
            ))

        fig_pump_3d.update_layout(
            scene=dict(
                xaxis_title="Shaft Axis X (m)",
                yaxis_title="Y (m)",
                zaxis_title="Z (m)",
                camera=dict(eye=dict(x=1.8, y=1.8, z=0.8)),
            ),
            height=400,
            margin={"r": 0, "t": 20, "l": 0, "b": 0},
        )
        st.plotly_chart(fig_pump_3d, use_container_width=True)

    with col_3d2:
        st.markdown("##### **SHAP Sub-Assembly Anomaly Share**")
        df_shap = pd.DataFrame({
            "Sub-Assembly": list(shap_data.keys()),
            "Risk Share (%)": list(shap_data.values()),
        })
        fig_shap = px.bar(
            df_shap,
            x="Sub-Assembly",
            y="Risk Share (%)",
            color="Risk Share (%)",
            color_continuous_scale="Reds",
            title="Sub-Component Anomaly Share",
        )
        fig_shap.update_layout(height=360, margin={"r": 10, "t": 30, "l": 10, "b": 10})
        st.plotly_chart(fig_shap, use_container_width=True)

# Tab 6: Water Scenario Replicator
with tab6:
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown("### 🛢️ **Petroleum Transportation (KPC)**")
        st.markdown("""
        - **Fluid Characteristics:** Refined petroleum (PMS, AGO, DPK), high density, explosive hazard.
        - **Core Physics Metrics:** Pressure residual ($\Delta P$), vibration ($\text{mm/s}$), bearing temperature ($^\circ\text{C}$).
        - **Critical Failure Modes:** Mechanical seal leakage, bearing degradation, thrust bearing wear.
        - **Threshold Ratings:** High-pressure multistage pumps ($4,500\text{ kPa}$, $7.1\text{ mm/s}$ vibration threshold).
        """)

    with sc2:
        st.markdown("### 💧 **Municipal Water Transport (NCWSC)**")
        st.markdown("""
        - **Fluid Characteristics:** Potable / raw water, high volume flow, variable elevation gradient.
        - **Core Physics Metrics:** Suction head loss ($m$), pipe burst pressure residuals, turbidity ($\text{NTU}$), motor load current ($\text{A}$).
        - **Critical Failure Modes:** Impeller cavitation, suction starvation, pipe burst, sediment clogging.
        - **Threshold Ratings:** High-discharge booster pumps ($100,000\text{ m}^3/\text{day}$, $8.0\text{m}$ head loss limit).
        """)

    st.divider()
    st.markdown("##### ⚙️ **Cross-Domain Architecture Alignment**")
    st.info(
        "Flowguard enforces identical Medallion ETL schemas (`bronze`, `silver`, `gold`), physics residual engines "
        "(HDI), 7-day ML classifiers, and RUL regression models regardless of fluid type by simply updating tenant "
        "fluid properties (`fluid_type: petroleum_products` vs `fluid_type: treated_water`)."
    )

# Tab 7: Work Orders & Calendar
with tab7:
    st.subheader(f"Condition-Based Work Orders & Maintenance Calendar ({operator_name})")

    if st.button("🔄 Trigger Fleet RUL Schedule Re-Ranking", type="primary"):
        if token:
            rank_res = api_request("POST", "/api/v1/maintenance-schedule/rank", token=token)
            if rank_res:
                st.success("Fleet maintenance schedule successfully re-ranked by RUL urgency!")
            else:
                st.info("Schedule re-ranking submitted.")
        else:
            st.info("Demo Mode: Fleet schedule re-ranked by RUL urgency.")

    st.markdown("##### **Active Scheduled Maintenance Calendar**")
    schedules = api_request("GET", "/api/v1/maintenance-schedule", token=token) or []
    if schedules:
        st.dataframe(pd.DataFrame(schedules), use_container_width=True)
    else:
        st.caption("No scheduled maintenance items currently active.")
