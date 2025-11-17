import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import base64
import os
import yaml
from yaml.loader import SafeLoader
import plotly.express as px

# ==================== FIXED FOR 2025 STREAMLIT-AUTHENTICATOR ====================
st.set_page_config(page_title="AnalystForge", layout="wide", page_icon="🕵️")

# Simple built-in login (no external dependency issues)
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.sidebar.form("login_form"):
            st.write("### AnalystForge Login")
            username = st.text_input("Username", value="investigator")
            password = st.text_input("Password", type="password", value="analyst2025")
            submit = st.form_submit_button("Login")

            if submit:
                if username == "investigator" and password == "analyst2025":
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Wrong credentials")
        st.stop()
    else:
        st.sidebar.success(f"Logged in as {st.session_state.user}")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

check_login()
# ==============================================================================

st.title("AnalystForge – Open-Source Analyst’s Notebook Clone (2025)")
st.caption("The closest free alternative used by AU law enforcement & OSINT teams")

# Initialise data
if "entities" not in st.session_state:
    st.session_state.entities = pd.DataFrame(columns=["Label", "Type", "PhotoURL", "Notes"])
if "links" not in st.session_state:
    st.session_state.links = pd.DataFrame(columns=["Source", "Target", "Type", "Date"])

tab1, tab2, tab3, tab4 = st.tabs(["Import", "Link Chart", "Timeline", "Export"])

# ====================== IMPORT ======================
with tab1:
    st.header("Import Data")
    c1, c2 = st.columns(2)
    with c1:
        uploaded_entities = st.file_uploader("Entities CSV", type="csv", key="ent")
        if uploaded_entities:
            st.session_state.entities = pd.read_csv(uploaded_entities)
            st.success(f"Loaded {len(st.session_state.entities)} entities")
    with c2:
        uploaded_links = st.file_uploader("Links CSV", type="csv", key="lnk")
        if uploaded_links:
            st.session_state.links = pd.read_csv(uploaded_links)
            st.success(f"Loaded {len(st.session_state.links)} links")

    st.info("Entities → columns: `Label`, `Type` (Person/Phone/Vehicle/etc), `PhotoURL` (optional)\nLinks → `Source`, `Target`, `Type`, `Date` (optional)")

# ====================== LINK CHART ======================
with tab2:
    st.header("Interactive Link Chart (Analyst’s Notebook style)")

    if st.session_state.entities.empty:
        st.warning("Upload entities first")
    else:
        net = Network(height="750px", bgcolor="#0e1117", font_color="#ffffff", directed=True)
        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=200, damping=0.9)

        colors = {
            "Person": "#ff4444", "Phone": "#00C851", "Vehicle": "#33b5e5",
            "Location": "#ffbb33", "Account": "#9c27b0", "Email": "#00bcd4",
            "Organization": "#aa66cc", "default": "#888888"
        }

        # Add entities
        for _, row in st.session_state.entities.iterrows():
            label = str(row.get("Label") or row.get("ID", "Unknown"))
            ent_type = row.get("Type", "default")
            color = colors.get(ent_type, colors["default"])
            photo = row.get("PhotoURL", "")
            notes = row.get("Notes", "")

            if photo and photo.strip():
                net.add_node(label, title=f"<b>{label}</b><br>{ent_type}<br>{notes}",
                             shape="circularImage", image=photo)
            else:
                net.add_node(label, title=f"<b>{label}</b><br>{ent_type}", color=color, size=30)

        # Add links
        for _, row in st.session_state.links.iterrows():
            src = str(row["Source"])
            tgt = str(row["Target"])
            label = row.get("Type", "")
            net.add_edge(src, tgt, label=label, color="#aaaaaa", arrows="to", width=2)

        net.show("chart.html")
        with open("chart.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=750, scrolling=True)

# ====================== TIMELINE ======================
with tab3:
    st.header("Timeline")
    if not st.session_state.links.empty and "Date" in st.session_state.links.columns:
        df = st.session_state.links.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        if not df.empty:
            fig = px.timeline(df.sort_values("Date"),
                              x_start="Date", x_end="Date",
                              y="Type", color="Type",
                              text=df["Source"] + " → " + df["Target"])
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid dates found")
    else:
        st.info("Add a 'Date' column to your links CSV")

# ====================== EXPORT ======================
with tab4:
    st.header("Export")
    if not st.session_state.entities.empty:
        csv = st.session_state.entities.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="entities.csv">Download Entities CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

    if not st.session_state.links.empty:
        csv = st.session_state.links.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="links.csv">Download Links CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

    if st.session_state.entities.empty and st.session_state.links.empty:
        st.info("Nothing to export yet")
