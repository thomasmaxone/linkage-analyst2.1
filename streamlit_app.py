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

# ------------------- CONFIG & AUTH (optional - remove if you don't want login) -------------------
st.set_page_config(page_title="AnalystForge", layout="wide", page_icon="🕵️")

# Create default credentials if no config file
if not os.path.exists('config.yaml'):
    config = {
        'credentials': {
            'usernames': {
                'investigator': {
                    'name': 'Investigator',
                    'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXe.jBkL5wnrXdvv7f3zYFG5qw3R5iY8CC'  # password = "analyst2025"
                }
            }
        },
        'cookie': {'expiry_days': 30, 'key': 'random_key', 'name': 'analystforge_cookie'},
        'preauthorized': ['demo@analystforge.org']
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login to AnalystForge', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
if authentication_status == None:
    st.warning('Please enter your username and password (try investigator / analyst2025)')
    st.stop()

# ------------------- MAIN APP -------------------
st.sidebar.image("https://i.imgur.com/0J7g9Zk.png", width=200)  # AnalystForge logo
st.title("🕵️ AnalystForge – Open-Source Analyst’s Notebook (v10 Theme)")

# Session state
if 'entities' not in st.session_state:
    st.session_state.entities = pd.DataFrame(columns=["ID", "Label", "Type", "PhotoURL", "Notes"])
if 'links' not in st.session_state:
    st.session_state.links = pd.DataFrame(columns=["Source", "Target", "Type", "Date", "Strength"])

tab1, tab2, tab3, tab4 = st.tabs(["Import Data", "Link Chart", "Timeline", "Export"])

with tab1:
    st.header("Import Entities & Links")
    col1, col2 = st.columns(2)
    with col1:
        ent_file = st.file_uploader("Entities CSV", type=["csv"])
        if ent_file:
            st.session_state.entities = pd.read_csv(ent_file)
            st.success(f"Loaded {len(st.session_state.entities)} entities")
    with col2:
        link_file = st.file_uploader("Links CSV", type=["csv"])
        if link_file:
            st.session_state.links = pd.read_csv(link_file)
            st.success(f"Loaded {len(st.session_state.links)} links")

    st.info("Required columns → Entities: Label, Type (Person/Phone/Vehicle/etc), PhotoURL (optional)\nLinks: Source, Target, Type (Call/Meets/Transfer)")

with tab2:
    st.header("Interactive Link Chart (Analyst’s Notebook Style)")

    if not st.session_state.entities.empty:
        net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True, notebook=True)
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "springLength": 250,
              "springStrength": 0.04
            }
          },
          "edges": {
            "arrows": "to",
            "smooth": false,
            "color": "#666666"
          },
          "nodes": {
            "font": {"size": 16, "face": "tahoma"},
            "borderWidth": 2
          }
        }
        """)

        # Entity type → color & shape (exact ANB style)
        type_style = {
            "Person": {"color": "#ff4444", "shape": "dot"},
            "Phone": {"color": "#00C851", "shape": "square"},
            "Vehicle": {"color": "#33b5e5", "shape": "triangle"},
            "Location": {"color": "#ffbb33", "shape": "diamond"},
            "Account": {"color": "#9c27b0", "shape": "box"},
            "Email": {"color": "#00bcd4", "shape": "ellipse"},
            "default": {"color": "#888888", "shape": "dot"}
        }

        for _, row in st.session_state.entities.iterrows():
            label = row.get("Label", row.get("ID", "Unknown"))
            ent_type = row.get("Type", "default")
            style = type_style.get(ent_type, type_style["default"])
            photo = row.get("PhotoURL", "")
            title = row.get("Notes", "")
            if photo:
                net.add_node(label, label=label, title=f"<img src='{photo}' width='200px'><br>{title}", 
                            shape="image", image=photo, **style, size=40)
            else:
                net.add_node(label, label=label, title=title, **style, size=35)

        for _, row in st.session_state.links.iterrows():
            src = row["Source"]
            tgt = row["Target"]
            link_type = row.get("Type", "Link")
            color = {"Call": "#00ff00", "Transfer": "#ff9800", "Meets": "#ff4444"}.get(link_type, "#666666")
            net.add_edge(src, tgt, title=link_type, label=link_type, color=color, width=3)

        net.show("analystforge.html")
        components.html(open("analystforge.html", "r", encoding="utf-8").read(), height=800)
    else:
        st.warning("Upload entities first")

with tab3:
    st.header("Timeline View")
    if not st.session_state.links.empty and "Date" in st.session_state.links.columns:
        timeline_df = st.session_state.links[["Source", "Target", "Type", "Date"]].copy()
        timeline_df["Date"] = pd.to_datetime(timeline_df["Date"])
        fig = px.timeline(timeline_df, x_start="Date", x_end="Date", y="Type", color="Type", text="Source → Target")
        fig.update_layout(template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add links with a 'Date' column to see timeline")

with tab4:
    st.header("Export")
    col1, col2 = st.columns(2)
    with col1:
        csv_ent = st.session_state.entities.to_csv(index=False)
        b64 = base64.b64encode(csv_ent.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}' download="entities.csv">Download Entities CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    with col2:
        csv_link = st.session_state.links.to_csv(index=False)
        b64 = base64.b64encode(csv_link.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}' download="links.csv">Download Links CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

# Logout
authenticator.logout('Logout', 'sidebar')
st.sidebar.success(f"Logged in as {name}")
