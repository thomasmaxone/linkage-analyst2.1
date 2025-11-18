import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# ULTRA-MODERN GLASS THEME
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
st.caption("Australian Law Enforcement Standard • 2025")

ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"
}

# Initialise
for key in ["library", "canvas", "links", "form_counter"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "form_counter" else 0

# SIDEBAR — DYNAMIC FORM
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")

    entity_type = st.selectbox(
        "Entity Type",
        options=list(ICONS.keys()),
        key=f"etype_{st.session_state.form_counter}"
    )

    with st.form(key=f"form_{st.session_state.form_counter}", clear_on_submit=True):
        data = {}

        if entity_type == "Person":
            st.subheader("Person Details")
            c1,c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name")
            with c2: data["Last Name"] = st.text_input("Last Name")
            data["Date of Birth"] = st.date_input("DOB", value=None)
            data["Address"] = st.text_input("Residential Address")
            data["Phone Number"] = st.text_input("Phone Number")

        elif entity_type == "Organisation":
            st.subheader("Organisation Details")
            data["Company Name"] = st.text_input("Company Name")
            data["ABN/ACN"] = st.text_input("ABN or ACN")
            data["Address"] = st.text_input("Registered Address")

        elif entity_type == "Vehicle":
            st.subheader("Vehicle Details")
            data["Registration"] = st.text_input("Registration Plate")
            c1,c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")
            data["Colour"] = st.text_input("Colour")

        elif entity_type == "Phone":
            st.subheader("Phone Details")
            data["Phone Number"] = st.text_input("Phone Number")
            data["IMEI"] = st.text_input("IMEI")

        elif entity_type == "Bank Account":
            st.subheader("Bank Account")
            data["Bank"] = st.text_input("Bank Name")
            c1,c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account Number"] = st.text_input("Account Number")
            data["Holder Name"] = st.text_input("Account Holder")

        elif entity_type == "Location":
            st.subheader("Location Details")
            data["Location Name"] = st.text_input("Name/Description")
            data["Address"] = st.text_input("Full Address")

        if st.form_submit_button("Save Entity to Project", type="primary"):
            label = {
                "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip() or "Person",
                "Organisation": data.get("Company Name", "Organisation"),
                "Vehicle": data.get("Registration", "Vehicle"),
                "Phone": data.get("Phone Number", "Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account Number','')}",
                "Location": data.get("Location Name") or data.get("Address", "Location")
            }[entity_type]

            entity = {
                "id": str(uuid.uuid4())[:8],
                "type": entity_type,
                "label": label,
                "data": data,
                "icon": ICONS[entity_type]
            }
            st.session_state.library.append(entity)
            st.success(f"Saved: {label}")
            st.session_state.form_counter += 1
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
c1, c2 = st.columns([4,1])

with c1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="880px", bgcolor="#ffffff", font_color="#111827", directed=True, notebook=True)
    net.force_atlas_2based()

    for ent in st.session_state.canvas:
        lines = [f"<b>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone Number"):
            lines.append(ent["data"]["Phone Number"])
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"):
            lines.append(ent["data"]["Registration"])
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b>"] + 
                             [f"{k}: {v if not isinstance(v,date) else v.strftime('%d/%m/%Y')}" 
                              for k,v in ent["data"].items() if v and v != date(1,1,1)])

        net.add_node(ent["id"], label=label_html, shape="image", image=ent["icon"],
                     title=tooltip, size=60, font={"multi": "html", "size": 18})

    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"], color="#3b82f6", width=4, arrows="to")

    components.html(net.generate_html(), height=880, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # LINK CREATOR
    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Create Link")
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        f = st.selectbox("From", options=list(labels.keys()), format_func=lambda x: labels[x])
        t = st.selectbox("To", options=list(labels.keys()), format_func=lambda x: labels[x])
        typ = st.text_input("Link Type", "Owns • Calls • Lives At")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": f, "to": t, "type": typ})
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

# EXPORT — FIXED pandas import
with st.expander("Export Project"):
    if st.session_state.canvas:
        export_data = []
        for e in st.session_state.canvas:
            row = {"Label": e["label"], "Type": e["type"]}
            row.update({k: v for k, v in e["data"].items() if v})
            export_data.append(row)
        df = pd.DataFrame(export_data)
        st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")

    if st.session_state.links:
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        links_data = [{"From": labels.get(l["from"], "?"), "To": labels.get(l["to"], "?"), "Type": l["type"]} 
                     for l in st.session_state.links]
        links_df = pd.DataFrame(links_data)
        st.download_button("Download Links CSV", links_df.to_csv(index=False), "links.csv")
