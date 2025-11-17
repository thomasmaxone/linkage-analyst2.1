import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from datetime import datetime
import base64
import os
import yaml
from yaml.loader import SafeLoader
import plotly.express as px

# ------------------- CONFIG & AUTH -------------------
st.set_page_config(page_title="AnalystForge", layout="wide", page_icon="🕵️")

# Create default config if not exists
if not os.path.exists('config.yaml'):
    config = {
        'credentials': {
            'usernames': {
                'investigator': {
                    'name': 'Investigator',
                    'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXe.jBkL5wnrXdvv7f3zYFG5qw3R5iY8CC'  # password: analyst2025
                }
            }
        },
        'cookie': {'expiry_days': 30, 'key': 'analystforge_key_2025', 'name': 'analystforge_cookie'},
        'preauthorized': ['demo@analystforge.org']
    }
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login to AnalystForge', 'main')

if not authentication_status:
    if authentication_status is False:
        st.error('Username/password incorrect')
    else:
        st.warning('Please enter credentials (try: investigator / analyst2025)')
    st.stop()

# ------------------- MAIN APP -------------------
st.title("🕵️ AnalystForge – Open-Source Analyst’s Notebook Clone")
st.sidebar.success(f"Logged in as {name}")
authenticator.logout('Logout', 'sidebar')

# Initialize session state
if 'entities' not in st.session_state:
    st.session_state.entities = pd.DataFrame(columns=["ID", "Label", "Type", "PhotoURL", "Notes"])
if 'links' not in st.session_state:
    st.session_state.links = pd.DataFrame(columns=["Source", "Target", "Type", "Date", "Strength"])

tab1, tab2, tab3, tab4 = st.tabs(["Import Data", "Link Chart", "Timeline", "Export"])

with tab1:
    st.header("Import Entities & Links")
    c1, c2 = st.columns(2)
    with c1:
        ent_file = st.file_uploader("Entities CSV", type=["csv"])
        if ent_file:
            st.session_state.entities = pd.read_csv(ent_file)
            st.success(f"Loaded {len(st.session_state.entities)} entities")
    with c2:
        link_file = st.file_uploader("Links CSV", type=["csv"])
        if link_file:
            st.session_state.links = pd.read_csv(link_file)
            st.success(f"Loaded {len(st.session_state.links)} links")

    st.info("""
    **Entities CSV columns**: `Label`, `Type` (Person/Phone/Vehicle/Location/etc), `PhotoURL` (optional), `Notes` (optional)  
    **Links CSV columns**: `Source`, `Target`, `Type` (Call/Meets/Transfer), `Date` (optional)
    """)

with tab2:
    st.header("Interactive Link Chart")
    if st.session_state.entities.empty:
        st.warning("Upload entities first")
    else:
        net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True)
        net.force_atlas_2based()

        # Analyst's Notebook style colors
        colors = {
            "Person": "#ff4444", "Phone": "#00C851", "Vehicle": "#33b5e5",
            "Location": "#ffbb33", "Account": "#9c27b0", "Email": "#00bcd4",
            "Organization": "#aa66cc", "default": "#888888"
        }

        for _, row in st.session_state.entities.iterrows():
            label = str(row.get("Label") or row.get("ID", "Unknown"))
            ent_type = row.get("Type", "default")
            color = colors.get(ent_type, colors["default"])
            photo = row.get("PhotoURL", "")
            notes = row.get("Notes", "")
            title = f"<b>{label}</b><br>{ent_type}<br>{notes}"

            if photo and photo.strip():
                net.add_node(label, title=title, shape="circularImage", image=photo, brokenImage="https://via.placeholder.com/50")
            else:
                net.add_node(label, title=title, color=color, size=30)

        for _, row in st.session_state.links.iterrows():
            src = str(row["Source"])
            tgt = str(row["Target"])
            link_type = row.get("Type", "Link")
            net.add_edge(src, tgt, label=link_type, color="#666666", width=2, arrows="to")

        net.show("chart.html")
        with open("chart.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=800, scrolling=True)

with tab3:
    st.header("Timeline")
    if not st.session_state.links.empty and "Date" in st.session_state.links.columns:
        df = st.session_state.links.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        if not df.empty:
            fig = px.timeline(df, x_start="Date", x_end="Date", y="Type", color="Type",
                              text=df["Source"] + " → " + df["Target"], title="Event Timeline")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid dates found")
    else:
        st.info("Add a 'Date' column (YYYY-MM-DD) to your links CSV")

with tab4:
    st.header("Export Data")
    if not st.session_state.entities.empty:
        csv1 = st.session_state.entities.to_csv(index=False)
        b641 = base64.b64encode(csv1.encode()).decode()
        href1 = f'<a href="data:file/csv;base64,{b641}" download="entities.csv">Download Entities CSV</a>'
        st.markdown(href1, unsafe_allow_html=True)

    if not st.session_state.links.empty:
        csv2 = st.session_state.links.to_csv(index=False)
        b642 = base64.b64encode(csv2.encode()).decode()
        href2 = f'<a href="data:file/csv;base64,{b642}" download="links.csv">Download Links CSV</a>'
        st.markdown(href2, unsafe_allow_html=True)

    if st.session_state.entities.empty and st.session_state.links.empty:
        st.info("Nothing to export yet")
