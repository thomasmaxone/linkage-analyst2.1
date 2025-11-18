import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date
import random

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Police")

# ========== BEAUTIFUL 2025 GLASS THEME ==========
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

ENTITIES = {
    "Person":       {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",       "color": "#ef4444"},
    "Organisation": {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",     "color": "#8b5cf6"},
    "Vehicle":      {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/truck-front-fill.svg", "color": "#3b82f6"},
    "Phone":        {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",        "color": "#10b981"},
    "Bank Account": {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",  "color": "#f59e0b"},
    "Location":     {"icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg",        "color": "#f97316"}
}

# ==== Helper: Entity field definitions per type ====
def get_entity_fields(entity_type):
    if entity_type == "Person":
        return [("label", "Full Name"), ("Phone Number", "Phone Number"), ("DOB", "Date of Birth")]
    if entity_type == "Vehicle":
        return [("label", "Registration"), ("Type", "Vehicle Type"), ("Owner", "Owner")]
    if entity_type == "Bank Account":
        return [("label", "Account Name"), ("BSB", "BSB"), ("Account Number", "Account Number")]
    if entity_type == "Organisation":
        return [("label", "Organisation Name"), ("Type", "Type")]
    if entity_type == "Phone":
        return [("label", "Label"), ("Number", "Phone Number"), ("Provider", "Provider")]
    if entity_type == "Location":
        return [("label", "Label"), ("Address", "Address")]
    return [("label", "Label")]

# ==== State initialization ====
for k in ["library", "canvas", "links", "selected_type", "adding_entity", "pending_entity_type", "pending_entity_coords"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k in ["library", "canvas", "links"] else None if k in ["pending_entity_type", "pending_entity_coords"] else False if k == "adding_entity" else "Person"

if "pending_style" not in st.session_state:
    st.session_state.pending_style = {"color": "#6366f1", "width": 4, "dashes": False, "label": ""}

# ==== LEFT SIDEBAR ====
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Drop Entity Type")
    st.session_state.selected_type = st.radio(
        "Choose type to place",
        options=list(ENTITIES.keys()),
        format_func=lambda x: x,
        index=list(ENTITIES.keys()).index(st.session_state.selected_type)
    )
    if st.button("Add new entity to library"):
        st.session_state.adding_entity = True
        st.session_state.pending_entity_type = st.session_state.selected_type
        st.session_state.pending_entity_coords = None  # Will be placed on canvas by drag/drop

    st.markdown("Click on library entry to drop on random canvas position.")
    st.markdown("</div>", unsafe_allow_html=True)

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

# ===== ADD ENTITY FORM (Sidebar modal-like form) ====
if st.session_state.adding_entity:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Enter Entity Information")
    entity_fields = get_entity_fields(st.session_state.pending_entity_type)
    entity_form = st.sidebar.form(key="entity_form")
    entity_data = {}

    for key, label in entity_fields:
        if "date" in key.lower() or "dob" in key.lower():
            val = entity_form.date_input(label, key=f"f_{key}", value=None)
            entity_data[key] = str(val) if val else ""
        else:
            entity_data[key] = entity_form.text_input(label, key=f"f_{key}")

    submit_entity = entity_form.form_submit_button("Save Entity")
    cancel_entity = entity_form.form_submit_button("Cancel")

    if submit_entity:
        new_ent = {
            "id": str(uuid.uuid4())[:8],
            "type": st.session_state.pending_entity_type,
            "label": entity_data.get("label", f"New {st.session_state.pending_entity_type}"),
            "data": entity_data,
            "icon": ENTITIES[st.session_state.pending_entity_type]["icon"],
            "color": ENTITIES[st.session_state.pending_entity_type]["color"],
            "x": random.randint(-300, 300),
            "y": random.randint(-300, 300),
            "fixed": False
        }
        st.session_state.library.append(new_ent)
        st.session_state.adding_entity = False
        st.session_state.pending_entity_type = None
        st.session_state.pending_entity_coords = None
        st.experimental_rerun()
    if cancel_entity:
        st.session_state.adding_entity = False
        st.session_state.pending_entity_type = None
        st.session_state.pending_entity_coords = None

# ===== MAIN CANVAS AND RIGHT SIDEBAR =====
col_canvas, col_right = st.columns([5, 1])

with col_canvas:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Canvas — Click to place • Click node → node to link")

    net = Network(height="920px", bgcolor="#ffffff", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"enabled": true, "stabilization": {"iterations": 150}},
      "interaction": {"dragNodes": true, "dragView": true, "zoomView": true},
      "nodes": {"font": {"multi": "html", "size": 17}},
      "edges": {"smooth": true, "arrows": "to", "color": {"inherit": false}}
    }
    """)

    for ent in st.session_state.canvas:
        lines = [f"<b>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone Number"): lines.append(ent["data"]["Phone Number"])
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"): lines.append(ent["data"]["Registration"])
        if ent["type"] == "Bank Account": lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account Number','')}")
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b>"] +
            [f"{k}: {v if not isinstance(v,date) else v.strftime('%d/%m/%Y')}"
            for k,v in ent["data"].items() if v]
        )

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

    for link in st.session_state.links:
        net.add_edge(
            link["from"], link["to"],
            label=link.get("label",""),
            color=link.get("color","#6366f1"),
            width=link.get("width",4),
            dashes=link.get("dashes",False)
        )

    # ===== JS Node/Canvas Click Control (insert logic for node/canvas click) =====
    graph_html = net.generate_html()
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
                    document.getElementById('link_status').style.display = "block";
                } else {
                    // Create link
                    fetch(`/link?from=${firstNode}&to=${nodeId}`);
                    waitingForSecondClick = false;
                    firstNode = null;
                    document.getElementById('link_status').innerText = "Link created";
                    document.getElementById('link_status').style.display = "block";
                    setTimeout(() => document.getElementById('link_status').style.display = "none", 2000);
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

# ==== RIGHT SIDEBAR: LINK STYLES AND CONNECT NODES ====
with col_right:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Style")
    link_color = st.color_picker("Color", st.session_state.pending_style.get("color", "#6366f1"))
    link_width = st.slider("Thickness", 1, 12, st.session_state.pending_style.get("width", 4))
    link_dashed = st.checkbox("Dashed line", value=st.session_state.pending_style.get("dashes", False))
    link_label = st.text_input("Label (optional)", value=st.session_state.pending_style.get("label", ""))

    if st.button("Apply to Next Link"):
        st.session_state.pending_style = {
            "color": link_color,
            "width": link_width,
            "dashes": link_dashed,
            "label": link_label or ""
        }
        st.success("Style saved")
    st.markdown("</div>", unsafe_allow_html=True)

    # ==== Connect two nodes sidebar ====
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Connect Entities")
    if len(st.session_state.canvas) >= 2:
        node_list = [(f"{e['type']} {e['label']}", e["id"]) for e in st.session_state.canvas]
        node_id_map = {e["id"]: f"{e['type']} {e['label']}" for e in st.session_state.canvas}
        from_idx = st.selectbox("From node", node_list, index=0, key="from_node_select")
        to_idx = st.selectbox("To node", node_list, index=1, key="to_node_select")

        if st.button("Create Link (from right panel)"):
            st.session_state.links.append({
                "from": from_idx[1],
                "to": to_idx[1],
                "color": link_color,
                "width": link_width,
                "dashes": link_dashed,
                "label": link_label,
            })
            st.success("Link created!")
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ==== Recently on canvas ====
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas[:10]:
        st.markdown(f"**{ent['type']}** {ent['label'][:20]}")
    if len(st.session_state.canvas) > 10:
        st.caption(f"... and {len(st.session_state.canvas) - 10} more")
    st.markdown("</div>", unsafe_allow_html=True)

# ===== HIDDEN ENDPOINTS for JS CALLS (simulate Streamlit reactivity for JS events) =====
try:
    query_params = st.query_params
except AttributeError:
    query_params = st.experimental_get_query_params()

def getparam(key, as_type=str):
    val = query_params.get(key)
    if val is None:
        return None
    if isinstance(val, list):
        val = val[0]
    return as_type(val)

if getparam("place"):
    x = int(getparam("x"))
    y = int(getparam("y"))
    typ = getparam("type")
    # Open entity info form if possible
    st.session_state.adding_entity = True
    st.session_state.pending_entity_type = typ
    st.session_state.pending_entity_coords = (x, y)
    st.experimental_rerun()

# Post-form, for canvas drop assign position
if (not st.session_state.adding_entity and 
    st.session_state.pending_entity_coords is not None and 
    len(st.session_state.library) > 0 
):
    last_entity = st.session_state.library[-1].copy()
    last_entity["x"], last_entity["y"] = st.session_state.pending_entity_coords
    last_entity["fixed"] = False
    if last_entity not in st.session_state.canvas:
        st.session_state.canvas.append(last_entity)
    st.session_state.pending_entity_coords = None
    st.experimental_rerun()

if getparam("link"):
    from_id = getparam("from")
    to_id = getparam("to")
    style = st.session_state.get("pending_style", {"color":"#6366f1","width":4,"dashes":False,"label":""})
    st.session_state.links.append({
        "from": from_id, "to": to_id,
        "color": style["color"],
        "width": style["width"],
        "dashes": style["dashes"],
        "label": style["label"]
    })
    st.rerun()

if getparam("delete"):
    node_id = getparam("node")
    st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != node_id]
    st.session_state.links = [l for l in st.session_state.links if l["from"] != node_id and l["to"] != node_id]
    st.rerun()
