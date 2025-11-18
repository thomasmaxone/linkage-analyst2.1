import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date
import random

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Police")

# BEAUTIFUL 2025 GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    .main {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    .glass {background: rgba(255,255,255,0.09); backdrop-filter: blur(16px); border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.12); padding: 1.4rem; box-shadow: 0 8px 32px rgba(0,0,0,0.4);}
    h1 {background: linear-gradient(90deg,#60a5fa,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:3rem; font-weight:800;}
    .stButton>button {background:#3b82f6; color:white; border:none; border-radius:10px; padding:0.6rem 1.2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.caption("Click canvas to place • Drag to move • Click node → node to link")

# REAL PHYSICAL ICONS + COLORS
ENTITIES = {
    "Person":       {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",       "color": "#ef4444"},
    "Organisation": {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",     "color": "#8b5cf6"},
    "Vehicle":      {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/truck-front-fill.svg", "color": "#3b82f6"},
    "Phone":        {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",        "color": "#10b981"},
    "Bank Account": {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",  "color": "#f59e0b"},
    "Location":     {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg",        "color": "#f97316"}
}

# Init
for k in ["library", "canvas", "links", "pending_link", "selected_type"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k != "pending_link" else None
        if k == "selected_type": st.session_state[k] = "Person"

# LEFT SIDEBAR — CHOOSE WHAT TO DROP
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Drop Entity Type")
    st.session_state.selected_type = st.radio(
        "Choose type to place",
        options=list(ENTITIES.keys()),
        format_func=lambda x: x,
        index=list(ENTITIES.keys()).index(st.session_state.selected_type)
    )
    st.markdown("Click anywhere on the white canvas to place")
    st.markdown("</div>", unsafe_allow_html=True)

    True)

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    for e in st.session_state.library:
        if st.button(f"{e['type']} {e['label']}", key=f"lib_{e['id']}"):
            # Add copy to canvas at random position
            copy = e.copy()
            copy.update({"x": random.randint(-500,500), "y": random.randint(-500,500), "fixed": False})
            if copy not in st.session_state.canvas:
                st.session_state.canvas.append(copy)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# CANVAS + RIGHT SIDEBAR
col_canvas, col_right = st.columns([5, 1])

with col_canvas:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Canvas — Click to place • Click node → node to link")

    # Pyvis network
    net = Network(height="920px", bgcolor="#ffffff", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"enabled": true, "stabilization": {"iterations": 150}},
      "interaction": {"dragNodes": true, "dragView": true, "zoomView": true},
      "nodes": {"font": {"multi": "html", "size": 17}},
      "edges": {"smooth": true, "arrows": "to", "color": {"inherit": false}}
    }
    """)

    # Add nodes
    for ent in st.session_state.canvas:
        lines = [f"<b>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone Number"): lines.append(ent["data"]["Phone Number"])
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"): lines.append(ent["data"]["Registration"])
        if ent["type"] == "Bank Account": lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account Number','')}")
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b>"] +
                             [f"{k}: {v if not isinstance(v,date) else v.strftime('%d/%m/%Y')}" 
                              for k,v in ent["data"].items() if v])

        net.add_node(
            ent["id"],
            label=label_html,
            image=ent["icon"],
            title=tooltip,
            color=ent["color"],
            size=55,
            x=ent.get("x",0),
            y=ent.get("y",0)
        )

    # Add links
    for link in st.session_state.links:
        net.add_edge(
            link["from"], link["to"],
            label=link.get("label",""),
            color=link.get("color","#6366f1"),
            width=link.get("width",4),
            dashes=link.get("dashes",False)
        )

    # === MAGIC: CAPTURE CLICKS ON CANVAS ===
    graph_html = net.generate_html()
    # Inject JavaScript to capture node clicks and canvas clicks
    graph_html = graph_html.replace(
        "</head>",
        """
        <script>
        const network = window.network;
        let waitingForSecondClick = false;
        let firstNode = null;

        network.on("click", function(params) {
            if (params.nodes.length === 1) {
                const nodeId = params.nodes[0];
                if (!waitingForSecondClick) {
                    waitingForSecondClick = true;
                    firstNode = nodeId;
                    document.getElementById('link_status').innerText = "Select target node...";
                } else {
                    // Create link
                    fetch(`/link?from=${firstNode}&to=${nodeId}`);
                    waitingForSecondClick = false;
                    firstNode = null;
                    document.getElementById('link_status').innerText = "Link created";
                    setTimeout(() => document.getElementById('link_status').innerText = "", 2000);
                }
            } else if (params.nodes.length === 0 && params.pointer.canvas) {
                // Clicked empty space → place new entity
                const x = params.pointer.canvas.x;
                const y = params.pointer.canvas.y;
                const type = document.getElementById('selected_type').value;
                fetch(`/place?x=${x}&y=${y}&type=${type}`);
            }
        });

        network.on("doubleClick", function(params) {
            if (params.nodes.length === 1) {
                const nodeId = params.nodes[0];
                fetch(`/delete?node=${nodeId}`);
            }
        });
        </script>
        </head>
        """
    )
    graph_html = graph_html.replace(
        "<body>",
        f"<body><input type='hidden' id='selected_type' value='{st.session_state.selected_type}'>"
    )
    graph_html = graph_html.replace(
        "</body>",
        "<div id='link_status' style='position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:#10b981; color:white; padding:12px 24px; border-radius:12px; font-weight:600; z-index:1000; display:none;'></div></body>"
    )

    components.html(graph_html, height=920, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT SIDEBAR — TINY LINK TOOLBAR
with col_right:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Style")
    link_color = st.color_picker("Color", "#6366f1")
    link_width = st.slider("Thickness", 1, 12, 4)
    link_dashed = st.checkbox("Dashed line")
    link_label = st.text_input("Label (optional)")

    if st.button("Apply to Next Link"):
        st.session_state.pending_style = {
            "color": link_color,
            "width": link_width,
            "dashes": link_dashed,
            "label": link_label or ""
        }
        st.success("Style saved")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas[:10]:  # show recent
        st.markdown(f"**{ent['type']}** {ent['label'][:20]}")
    if len(st.session_state.canvas) > 10:
        st.caption(f"... and {len(st.session_state.canvas)-10} more")
    st.markdown("</div>", unsafe_allow_html=True)

# HIDDEN ENDPOINTS FOR JS CALLS
if st.query_params.get("place"):
    x = int(st.query_params["x"])
    y = int(st.query_params["y"])
    typ = st.query_params["type"]
    # create new entity directly on canvas
    data = {"Created": "Canvas drop"}
    label = f"New {typ.lower()}"
    new_ent = {
        "id": str(uuid.uuid4())[:8],
        "type": typ,
        "label": label,
        "data": data,
        "icon": ENTITIES[typ]["icon"],
        "color": ENTITIES[typ]["color"],
        "x": x, "y": y, "fixed": False
    }
    st.session_state.canvas.append(new_ent)
    st.rerun()

if st.query_params.get("link"):
    from_id = st.query_params["from"]
    to_id = st.query_params["to"]
    style = st.session_state.get("pending_style", {"color":"#6366f1","width":4,"dashes":False,"label":""})
    st.session_state.links.append({
        "from": from_id, "to": to_id,
        "color": style["color"],
        "width": style["width"],
        "dashes": style["dashes"],
        "label": style["label"]
    })
    st.rerun()

if st.query_params.get("delete"):
    node_id = st.query_params["node"]
    st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != node_id]
    st.session_state.links = [l for l in st.session_state.links if l["from"] != node_id and l["to"] != node_id]
    st.rerun()
