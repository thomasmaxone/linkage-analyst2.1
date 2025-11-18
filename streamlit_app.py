import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

# FORCE NO CACHING — THIS IS THE FIX
st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Police Car Light")
if "force_rerun" not in st.session_state:
    st.session_state.force_rerun = 0
st.session_state.force_rerun += 1

# ULTRA MODERN GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, .main {background: #0f172a !important;}
    .glass {background: rgba(255,255,255,0.08); backdrop-filter: blur(16px); border-radius: 16px; 
            border: 1px solid rgba(255,255,255,0.12); padding: 1.8rem; box-shadow: 0 8px 32px rgba(0,0,0,0.5);}
    .stButton > button {background: linear-gradient(45deg,#3b82f6,#8b5cf6); color:white; border:none; 
                        border-radius:14px; padding:1rem 2rem; font-weight:600; box-shadow:0 6px 25px rgba(59,130,246,0.5);}
    .stButton > button:hover {transform:translateY(-4px); box-shadow:0 12px 35px rgba(59,130,246,0.7);}
    h1 {background: linear-gradient(90deg,#60a5fa,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; 
        font-size:3.2rem; font-weight:800;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.caption("Australian Law Enforcement Standard • 2025")

ICONS = {
    "Person": "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",
    "Vehicle": "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg",
    "Phone": "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",
    "Location": "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"
}

# INIT — CLEAR EVERYTHING
for key in list(st.session_state.keys()):
    if key not in ["library", "canvas", "links"]:
        del st.session_state[key]

for k in ["library", "canvas", "links"]:
    if k not in st.session_state:
        st.session_state[k] = []

# SIDEBAR — DYNAMIC FORM (GUARANTEED TO UPDATE)
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")

    # THIS KEY FORCES FULL REBUILD
    entity_type = st.selectbox("Entity Type", list(ICONS.keys()), key=f"type_{st.session_state.force_rerun}")

    with st.form(key=f"form_{st.session_state.force_rerun}", clear_on_submit=True):
        data = {}

        if entity_type == "Person":
            st.markdown("**Person Details**")
            c1,c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name", key="p1")
            with c2: data["Last Name"] = st.text_input("Last Name", key="p2")
            data["Date of Birth"] = st.date_input("DOB", value=None, key="p3")
            data["Address"] = st.text_input("Address", key="p4")
            data["Phone Number"] = st.text_input("Phone", key="p5")

        elif entity_type == "Organisation":
            st.markdown("**Organisation Details**")
            data["Company Name"] = st.text_input("Company Name", key="o1")
            data["ABN/ACN"] = st.text_input("ABN or ACN", key="o2")
            data["Address"] = st.text_input("Registered Address", key="o3")

        elif entity_type == "Vehicle":
            st.markdown("**Vehicle Details**")
            data["Registration"] = st.text_input("Registration Plate", key="v1")
            c1,c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make", key="v2")
            with c2: data["Model"] = st.text_input("Model", key="v3")
            data["Colour"] = st.text_input("Colour", key="v4")

        elif entity_type == "Phone":
            st.markdown("**Phone Details**")
            data["Phone Number"] = st.text_input("Phone Number", key="ph1")
            data["IMEI"] = st.text_input("IMEI", key="ph2")

        elif entity_type == "Bank Account":
            st.markdown("**Bank Account**")
            data["Bank"] = st.text_input("Bank Name", key="b1")
            c1,c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB", key="b2")
            with c2: data["Account Number"] = st.text_input("Account Number", key="b3")
            data["Holder Name"] = st.text_input("Account Holder", key="b4")

        elif entity_type == "Location":
            st.markdown("**Location Details**")
            data["Name"] = st.text_input("Location Name (e.g. Safe House)", key="l1")
            data["Address"] = st.text_input("Full Address", key="l2plom")

        saved = st.form_submit_button("Save Entity to Project", type="primary")
        if saved:
            label = {
                "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip() or "Person",
                "Organisation": data.get("Company Name", "Org"),
                "Vehicle": data.get("Registration", "Vehicle"),
                "Phone": data.get("Phone Number", "Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account Number','')}",
                "Location": data.get("Name") or data.get("Address", "Location")
            }[entity_type]

            entity = {"id": str(uuid.uuid4())[:8], "type": entity_type, "label": label, "data": data, "icon": ICONS[entity_type]}
            st.session_state.library.append(entity)
            st.success(f"Saved: {label}")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # LIBRARY
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    for e in st.session_state.library:
        if st.button(f"{e['type']} {e['label']}", key=f"add_{e['id']}"):
            if e not in st.session_state.canvas:
                st.session_state.canvas.append(e)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# CANVAS
c1, _ = st.columns([4,1])
with c1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="900px", bgcolor="#ffffff", font_color="#000000", directed=True, notebook=True)
    net.force_atlas_2based()

    for ent in st.session_state.canvas:
        net.add_node(ent["id"], label=f"<b>{ent['label']}</b>", shape="image", image=ent["icon"], size=60, title=str(ent["data"]))

    for i, link in enumerate(st.session_state.links):
        net.add_edge(link["from"], link["to"], label=link["type"], color="#3b82f6", width=4)

    components.html(net.generate_html(), height=900, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

# LINK CREATOR
if len(st.session_state.canvas) >= 2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        f = st.selectbox("From", st.session_state.canvas, format_func=lambda x: x["label"])
    with col2:
        t = st.selectbox("To", st.session_state.canvas, format_func=lambda x: x["label"])
    typ = st.text_input("Link Type", "Owns / Calls / Lives At")
    if st.button("Add Link", type="primary"):
        st.session_state.links.append({"from": f["id"], "to": t["id"], "type": typ})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
