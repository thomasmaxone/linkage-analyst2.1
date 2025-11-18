import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# MODERN GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    .main {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    .glass {
        background: rgba(255,255,255,0.09);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.12);
        padding: 1.8rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 1.2rem;
    }
    .stButton > button {
        background: linear-gradient(45deg,#3b82f6,#8b5cf6);
        color:white; border:none; border-radius:14px;
        padding:1rem 2rem; font-weight:600;
        box-shadow:0 6px 25px rgba(59,130,246,0.5);
        transition:all 0.3s;
    }
    .stButton > button:hover {
        transform:translateY(-4px);
        box-shadow:0 12px 35px rgba(59,130,246,0.7);
    }
    h1 {
        background: linear-gradient(90deg,#60a5fa,#c084fc);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        font-size:3.2rem; font-weight:800;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.caption("Australian Law Enforcement • Full i2 Replacement • 2025–2026")

# ENTITY COLORS & ICONS
ENTITY_CONFIG = {
    "Person":       {"color": "#ef4444", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg"},
    "Organisation": {"color": "#8b5cf6", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg"},
    "Vehicle":      {"color": "#3b82f6", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg"},
    "Phone":        {"color": "#10b981", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg"},
    "Bank Account": {"color": "#f59e0b", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg"},
    "Location":     {"color": "#f97316", "icon": "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"}
}

# Init
for k in ["library", "canvas", "links", "form_counter"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k != "form_counter" else 0

# SIDEBAR — ADD ENTITY TO LIBRARY
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 1. Add Entity to Library")

    entity_type = st.selectbox("Type", list(ENTITY_CONFIG.keys()), key=f"type_{st.session_state.form_counter}")

    with st.form(key=f"form_{st.session_state.form_counter}", clear_on_submit=True):
        data = {}
        if entity_type == "Person":
            c1,c2 = st.columns(2)
            with c1: data["First"] = st.text_input("First Name")
            with c2: data["Last"] = st.text_input("Last Name")
            data["DOB"] = st.date_input("DOB", value=None)
            data["Phone"] = st.text_input("Phone")
            data["Address"] = st.text_input("Address")

        elif entity_type == "Organisation":
            data["Name"] = st.text_input("Company Name")
            data["ABN"] = st.text_input("ABN/ACN")
            data["Address"] = st.text_input("Address")

        elif entity_type == "Vehicle":
            data["Rego"] = st.text_input("Registration")
            c1,c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")

        elif entity_type == "Phone":
            data["Number"] = st.text_input("Number")
            data["IMEI"] = st.text_input("IMEI")

        elif entity_type == "Bank Account":
            data["Bank"] = st.text_input("Bank")
            c1,c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account"] = st.text_input("Account No.")

        elif entity_type == "Location":
            data["Name"] = st.text_input("Location Name")
            data["Address"] = st.text_input("Address")

        if st.form_submit_button("Save to Library", type="primary"):
            label = {
                "Person": f"{data.get('First','')} {data.get('Last','')}".strip() or "Person",
                "Organisation": data.get("Name","Org"),
                "Vehicle": data.get("Rego","Vehicle"),
                "Phone": data.get("Number","Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account','')}",
                "Location": data.get("Name") or data.get("Address","Location")
            }[entity_type]

            entity = {
                "id": str(uuid.uuid4())[:8],
                "type": entity_type,
                "label": label,
                "data": data,
                "color": ENTITY_CONFIG[entity_type]["color"],
                "icon": ENTITY_CONFIG[entity_type]["icon"],
                "x": 0, "y": 0, "fixed": False
            }
            st.session_state.library.append(entity)
            st.success(f"Saved: {label}")
            st.session_state.form_counter += 1
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # LIBRARY → CLICK TO ADD TO CANVAS
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 2. Click to Place on Canvas")
    for e in st.session_state.library:
        if st.button(f"{e['type']} {e['label']}", key=f"place_{e['id']}"):
            # Add to canvas with random position
            import random
            e_copy = e.copy()
            e_copy.update({"x": random.randint(-400,400), "y": random.randint(-400,400), "fixed": True})
            if e_copy not in st.session_state.canvas:
                st.session_state.canvas.append(e_copy)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# MAIN CANVAS — FULLY INTERACTIVE
c1, c2 = st.columns([4,1])

with c1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas — Drag & Link Freely")

    net = Network(height="900px", bgcolor="#ffffff", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"enabled": true, "stabilization": {"iterations": 100}},
      "interaction": {"dragNodes": true, "dragView": true, "zoomView": true},
      "nodes": {"shape": "image", "size": 60, "font": {"multi": "html", "size": 18}},
      "edges": {"smooth": true, "arrows": "to"}
    }
    """)

    # Add nodes with color + data under icon
    for ent in st.session_state.canvas:
        lines = [f"<b style='font-size:20px'>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone"): lines.append(ent["data"]["Phone"])
        if ent["type"] == "Vehicle" and ent["data"].get("Rego"): lines.append(ent["data"]["Rego"])
        if ent["type"] == "Bank Account": lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account','')}")
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
            x=ent["x"], y=ent["y"],
            fixed=ent["fixed"]
        )

    # Add existing links
    for link in st.session_state.links:
        net.add_edge(link["from"], link["to"],
                     label=link.get("label",""),
                     color=link.get("color","#3b82f6"),
                     width=link.get("width",4),
                     dashes=link.get("dashes",False),
                     arrows=link.get("arrows","to"))

    components.html(net.generate_html(), height=900, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ADVANCED LINK TOOL
    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Create Advanced Link")

        nodes = {e["id"]: e["label"] for e in st.session_state.canvas}
        col1, col2 = st.columns(2)
        with col1:
            src = st.selectbox("From", options=list(nodes.keys()), format_func=lambda x: nodes[x])
        with col2:
            tgt = st.selectbox("To", options=list(nodes.keys()), format_func=lambda x: nodes[x])

        c1, c2, c3, c4 = st.columns(4)
        with c1: link_color = st.color_picker("Color", "#3b82f6")
        with c2: link_width = st.slider("Thickness", 1, 10, 4)
        with c3: link_style = st.selectbox("Style", ["Solid", "Dashed"])
        with c4: link_label = st.text_input("Label (optional)", "Owns")

        if st.button("Create Link", type="primary"):
            st.session_state.links.append({
                "from": src, "to": tgt,
                "label": link_label,
                "color": link_color,
                "width": link_width,
                "dashes": link_style == "Dashed",
                "arrows": "to"
            })
            st.success("Link created!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"rem_{ent['id']}"):
            st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != ent["id"]]
            st.session_state.links = [l for l in st.session_state.links if l["from"] != ent["id"] and l["to"] != ent["id"]]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# EXPORT
with st.expander("Export Project"):
    if st.session_state.canvas:
        df = pd.DataFrame([{"Label": e["label"], "Type": e["type"], **e["data"]} for e in st.session_state.canvas])
        st.download_button("Download Entities", df.to_csv(index=False), "entities.csv")
    if st.session_state.links:
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        links_df = pd.DataFrame([{
            "From": labels.get(l["from"]), "To": labels.get(l["to"]),
            "Type": l.get("label",""), "Color": l.get("color","#3b82f6")
        } for l in st.session_state.links])
        st.download_button("Download Links", links_df.to_csv(index=False), "links.csv")
