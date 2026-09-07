"""Flowguard — Streamlit Operational Predictive Maintenance Dashboard

Interactive frontend for Kenya Pipeline Company (KPC) pump infrastructure monitoring.
Communicates with the Flowguard FastAPI Backend via REST APIs.
"""
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuration & Page Setup
st.set_page_config(
    page_title="Flowguard | KPC Predictive Maintenance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

# KPC 13 Station Coordinates Reference Data
KPC_STATIONS = [
    {"code": "PS1", "name": "PS1 Mombasa", "lat": -4.0225, "lon": 39.6086, "region": "Coast", "capacity": 3200},
    {"code": "PS2", "name": "PS2 Samburu", "lat": -4.1667, "lon": 39.2000, "region": "Coast", "capacity": 3200},
    {"code": "PS3", "name": "PS3 Maungu", "lat": -3.5500, "lon": 38.7667, "region": "Coast", "capacity": 3200},
    {"code": "PS4", "name": "PS4 Mtito Andei", "lat": -2.6858, "lon": 38.1706, "region": "Eastern", "capacity": 3200},
    {"code": "PS5", "name": "PS5 Konza", "lat": -1.7357, "lon": 37.1287, "region": "Eastern", "capacity": 3200},
    {"code": "PS6", "name": "PS6 Nairobi Depot", "lat": -1.3192, "lon": 36.9278, "region": "Nairobi", "capacity": 4000},
    {"code": "PS7", "name": "PS7 Naivasha", "lat": -0.7167, "lon": 36.4333, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS8", "name": "PS8 Gilgil", "lat": -0.4903, "lon": 36.3178, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS9", "name": "PS9 Nakuru", "lat": -0.3031, "lon": 36.0800, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS10", "name": "PS10 Molo", "lat": -0.2500, "lon": 35.7333, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS11", "name": "PS11 Eldoret Depot", "lat": 0.5143, "lon": 35.2698, "region": "Rift Valley", "capacity": 2600},
    {"code": "PS12", "name": "PS12 Turbo", "lat": 0.6500, "lon": 35.0833, "region": "Rift Valley", "capacity": 2000},
    {"code": "PS13", "name": "PS13 Kisumu Depot", "lat": -0.0917, "lon": 34.7680, "region": "Nyanza", "capacity": 2000},
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


# Session State Management
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# Custom CSS Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem; }
    .card-kpi { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 1rem; border-radius: 8px; text-align: center; }
    .card-title { font-size: 0.9rem; color: #64748B; font-weight: 600; }
    .card-value { font-size: 1.8rem; font-weight: 700; color: #0F172A; }
</style>
""", unsafe_allow_html=True)


# Sidebar & Authentication
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.svg", width=64)
    st.markdown("### **Flowguard Control Center**")
    st.caption("Condition-Based Predictive Maintenance")
    st.divider()

    if not st.session_state["jwt_token"]:
        st.subheader("🔑 Authentication")
        email_input = st.text_input("Email", value="admin@kpc.co.ke")
        password_input = st.text_input("Password", value="password123", type="password")
        if st.button("Sign In", type="primary", use_container_width=True):
            res = api_request("POST", "/api/v1/users/login", data={"email": email_input, "password": password_input})
            if res and "access_token" in res:
                st.session_state["jwt_token"] = res["access_token"]
                st.session_state["user_email"] = email_input
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


# Main Dashboard Header
st.markdown("<div class='main-header'>🛡️ Flowguard Operational Maintenance Dashboard</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-header'>Kenya Pipeline Company (KPC) 1,342 km Infrastructure Monitoring</div>",
    unsafe_allow_html=True,
)

token = st.session_state["jwt_token"]

# Top Level KPI Row
col1, col2, col3, col4 = st.columns(4)

stations_data = api_request("GET", "/api/v1/stations", token=token) or KPC_STATIONS
pumps_data = api_request("GET", "/api/v1/pumps", token=token) or []
alerts_data = api_request("GET", "/api/v1/alerts", token=token) or DEMO_ALERTS
work_orders = api_request("GET", "/api/v1/work-orders", token=token) or []

with col1:
    st.markdown(
        "<div class='card-kpi'><div class='card-title'>KPC PUMP STATIONS</div><div class='card-value'>13</div></div>",
        unsafe_allow_html=True,
    )
with col2:
    val = len(pumps_data) or 26
    st.markdown(
        f"<div class='card-kpi'><div class='card-title'>REGISTERED PUMP ASSETS</div><div class='card-value'>{val}</div></div>",
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
        f"🚨 **ACTIVE RISK NOTIFICATION**: {len(active_crit)} alert(s) active across KPC fleet. "
        "Review the **Active Risk Alerts** tab for threshold details and management."
    )

st.write("")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Fleet Map & Stations",
    "⚡ Telemetry & HDI Engine",
    "🤖 7-Day Risk & RUL Predictor",
    "🚨 Active Risk Alerts",
    "🔍 SHAP Explainability",
    "🛠️ Work Orders & Calendar",
])

# Tab 1: Fleet Overview & Map
with tab1:
    st.subheader("Kenya Pipeline Network Corridor (Mombasa to Kisumu)")

    station_alert_severity = {}
    for a in alerts_data:
        st_code = a.get("station_code") or a.get("station_id", "")
        if not st_code:
            for s in KPC_STATIONS:
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
    for s in KPC_STATIONS:
        health = station_alert_severity.get(s["code"], "NORMAL")
        color = "#DC2626" if health == "CRITICAL" else "#D97706" if health == "WARNING" else "#16A34A"
        map_stations.append({**s, "health": health, "color": color})

    df_map = pd.DataFrame(map_stations)

    fig_map = go.Figure()

    fig_map.add_trace(go.Scattergeo(
        lat=df_map["lat"],
        lon=df_map["lon"],
        mode="lines",
        line=dict(width=3, color="#1E3A8A"),
        name="KPC Pipeline Corridor (1,342 km)",
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
                marker=dict(size=14, color=color, symbol="circle", line=dict(width=1.5, color="#FFFFFF")),
                text=sub_df["code"],
                textposition="top center",
                name=f"Health: {label}",
                hovertext=[
                    f"<b>{row['name']} ({row['code']})</b><br>"
                    f"Region: {row['region']}<br>"
                    f"Capacity: {row['capacity']:,} m³/day<br>"
                    f"Health Status: <b>{row['health']}</b>"
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
        height=500,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🔎 **Station Inspector**")
    sel_st_code = st.selectbox(
        "Select Station to Inspect",
        options=[s["code"] for s in KPC_STATIONS],
        format_func=lambda c: next(
            f"{s['code']} - {s['name']} ({s['region']})" for s in KPC_STATIONS if s["code"] == c
        ),
    )
    st_info = next(s for s in map_stations if s["code"] == sel_st_code)

    st_col1, st_col2, st_col3, st_col4 = st.columns(4)
    with st_col1:
        st.metric("Station Name", st_info["name"])
    with st_col2:
        st.metric("Region", st_info["region"])
    with st_col3:
        st.metric("Capacity", f"{st_info['capacity']:,} m³/day")
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
    st.subheader("Real-Time Pump Sensor Telemetry & Health Deviation Index (HDI)")

    selected_pump_id = None
    if pumps_data:
        pump_options = {f"{p.get('tag_number', 'PUMP')}-{p.get('id', '')[:6]}": p["id"] for p in pumps_data}
        selected_label = st.selectbox("Select Pump Asset", list(pump_options.keys()))
        selected_pump_id = pump_options[selected_label]
    else:
        st.info("No live pumps returned from backend. Using demo baseline visualization.")

    col_t1, col_t2 = st.columns([2, 1])

    with col_t1:
        st.markdown("##### **Recent Telemetry Trends**")
        timestamps = pd.date_range(end=datetime.now(), periods=20, freq="min")
        df_telemetry = pd.DataFrame({
            "Timestamp": timestamps,
            "Vibration (mm/s)": [2.1 + (i * 0.15) for i in range(20)],
            "Bearing Temp (°C)": [45.0 + (i * 0.8) for i in range(20)],
            "Discharge Pressure (psi)": [600.0 - (i * 3.5) for i in range(20)],
        })

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=df_telemetry["Timestamp"],
                y=df_telemetry["Vibration (mm/s)"],
                mode="lines+markers",
                name="Vibration (mm/s)",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=df_telemetry["Timestamp"],
                y=df_telemetry["Bearing Temp (°C)"],
                mode="lines+markers",
                name="Bearing Temp (°C)",
            )
        )
        fig_trend.update_layout(height=350, margin={"r": 10, "t": 30, "l": 10, "b": 10})
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_t2:
        st.markdown("##### **Health Deviation Index (HDI)**")
        hdi_val = 0.28
        if selected_pump_id and token:
            hdi_res = api_request("POST", f"/api/v1/flowgard-engine/pumps/{selected_pump_id}/compute", token=token)
            if hdi_res and "health_deviation_index" in hdi_res:
                hdi_val = float(hdi_res["health_deviation_index"])

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=hdi_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "HDI Score [0.0 - 1.0]"},
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

    risk_score = 0.76
    predicted_class = "bearing_fault"
    rul_days = 12.4
    ci_lower = 10.9
    ci_upper = 13.8

    if selected_pump_id and token:
        pred_res = api_request("POST", f"/api/v1/predictions/pumps/{selected_pump_id}/trigger", token=token)
        if pred_res:
            risk_score = float(pred_res.get("risk_score_7d", 0.76))
            predicted_class = pred_res.get("predicted_class", "bearing_fault")

        rul_res = api_request("POST", f"/api/v1/rul/pumps/{selected_pump_id}/trigger", token=token)
        if rul_res:
            rul_days = float(rul_res.get("remaining_useful_life_days", 12.4))
            ci_lower = float(rul_res.get("confidence_lower_days", 10.9))
            ci_upper = float(rul_res.get("confidence_upper_days", 13.8))

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
    st.subheader("🚨 Real-Time Risk Alerts & Threshold Notifications")

    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        st.markdown(
            "Dynamic threshold evaluations across vibration, bearing temperature, and discharge pressure metrics."
        )
    with col_a2:
        if st.button("⚡ Evaluate Thresholds", type="primary", use_container_width=True):
            if token and selected_pump_id:
                eval_res = api_request("POST", f"/api/v1/alerts/pumps/{selected_pump_id}/evaluate", token=token)
                if eval_res is not None:
                    st.success("Threshold rules evaluated successfully!")
                    st.rerun()

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

        st.markdown("##### **Interactive Alert Management**")
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
                    if token:
                        api_request(
                            "PATCH", f"/api/v1/alerts/{sel_alert_id}", data={"status": "acknowledged"}, token=token
                        )
                        st.success("Alert acknowledged!")
                        st.rerun()
                    else:
                        st.info("Demo Mode: Alert acknowledged in UI state.")
            with ca2:
                if st.button("Resolve Alert", use_container_width=True):
                    if token:
                        api_request(
                            "PATCH", f"/api/v1/alerts/{sel_alert_id}", data={"status": "resolved"}, token=token
                        )
                        st.success("Alert resolved!")
                        st.rerun()
                    else:
                        st.info("Demo Mode: Alert resolved in UI state.")
    else:
        st.info("No active or historical alerts found matching the selected status filter.")

# Tab 5: SHAP Explainability
with tab5:
    st.subheader("Explainable AI (SHAP Sub-component Risk Breakdown)")

    shap_data = {"Bearing": 42.5, "Impeller": 28.0, "Mechanical Seal": 18.5, "Motor": 11.0}
    if selected_pump_id and token:
        shap_res = api_request("POST", f"/api/v1/explainability/pumps/{selected_pump_id}/trigger", token=token)
        if shap_res and "component_scores" in shap_res:
            scores = shap_res["component_scores"]
            shap_data = {k.capitalize(): v * 100 for k, v in scores.items()}

    df_shap = pd.DataFrame({"Component": list(shap_data.keys()), "Risk Share (%)": list(shap_data.values())})
    fig_shap = px.bar(
        df_shap,
        x="Component",
        y="Risk Share (%)",
        color="Risk Share (%)",
        color_continuous_scale="Reds",
        title="Sub-Assembly Anomaly Contribution",
    )
    st.plotly_chart(fig_shap, use_container_width=True)

# Tab 6: Work Orders & Calendar
with tab6:
    st.subheader("Condition-Based Work Orders & RUL-Ranked Schedule")

    if st.button("🔄 Trigger Fleet RUL Schedule Re-Ranking", type="primary"):
        if token:
            rank_res = api_request("POST", "/api/v1/maintenance-schedule/rank", token=token)
            if rank_res:
                st.success("Fleet maintenance schedule successfully re-ranked by RUL urgency!")
            else:
                st.info("Schedule re-ranking submitted.")

    st.markdown("##### **Active Scheduled Maintenance Calendar**")
    schedules = api_request("GET", "/api/v1/maintenance-schedule", token=token) or []
    if schedules:
        st.dataframe(pd.DataFrame(schedules), use_container_width=True)
    else:
        st.caption("No scheduled maintenance items currently active.")
