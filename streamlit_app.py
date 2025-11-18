import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date, datetime
import os

# ------------------------------------------------------
# PAGE CONFIG (IBM i2 Classic Style)
# ------------------------------------------------------
st.set_page_config(
    page_title="AnalystForge Pro (i2 Mode)",
    layout="wide",
    page_icon="🔍"
)

# ------------------------------------------------------
# LOAD CSS THEME (Classic IBM i2 Look)
# ------------------------------------------------------
with open("assets/css/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ------------------------------------------------------
# ICON PATHS (LOCAL ASSETS)
# ------------------------------------------------------
ICONS = {
    "Person": "assets/icons/person.svg",
    "Organisation": "assets/icons/building.svg",
    "Vehicle": "assets/icons/car-front.svg",
    "Phone": "assets/icons/phone.svg",
    "Bank Account": "assets/icons/piggy-bank.svg",
    "Location": "assets/icons/house.svg",
}

# ------------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------------
for key in ["library", "canvas", "links"]:
    st.session_state.setdefault(key, [])

# ------------------------------------------------------
# SIDEBAR — ENTITY PALETTE (i2 Style)
# ------------------------------------------------------
st.sidebar.markdown("## 📂 Entity Palette (i2 Classic)")

with st.sidebar.expander("➕ Add Entity", expanded=True):

    entity_type = st.selectbox("Entity Type", list(ICONS.keys()))

    with st.form("entity_form"):
        data = {}

        # PERSON
        if entity_type == "Person":
            c1, c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name")
            with c2: data["Last Name"] = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", value=None)
            data["DOB"] = dob if dob != date(1, 1, 1) else None
            data["Phone"] = st.text_input("Phone Number")
            data["Email"] = st.text_input("Email (optional)")

        # ORGANISATION
        elif entity_type == "Organisation":
            data["Name"] = st.text_input("Organisation Name")
            data["ABN"] = st.text_input("ABN / ACN")

        # VEHICLE
        elif entity_type == "Vehicle":
            data["Registration"] = st.text_input("Registration Plate")
            c1, c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")
            data["Colour"] = st.text_input("Colour (optional)")

        # PHONE
        elif entity_type == "Phone":
            data["Number"] = st.text_input("Phone Number")
            data["IMEI"] = st.text_input("IMEI (optional)")
            data["Provider"] = st.text_input("Provider (optional)")

        # BANK ACCOUNT
        elif entity_type == "Bank Account":
            data["Bank"] = st.text_input("Bank Name")
            c1, c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account Number"] = st.text_input("Account Number")
            data["Account Name"] = st.text_input("Account Holder Name")

        # LOCATION
        elif entity_type == "Location":
            data["Street Address"] = st.text_input("Street Address")
            c1, c2 = st.columns(2)
            with c1: data["Suburb"] = st.text_input("Suburb")
            with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])
            data["Postcode"] = st.text_input("Postcode", max_chars=4)

        submit = st.form_submit_button("Add to Entity Library")

        if submit:
            label = {
                "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip(),
                "Organisation": data.get("Name", "Unknown Org"),
                "Vehicle": data.get("Registration", "Unknown Vehicle"),
                "Phone": data.get("Number", "Unknown Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account Number','')}",
                "Location": data.get("Street Address", "Unknown Location")
            }[entity_type]

            ent = {
                "id": str(uuid.uuid4())[:8],
                "type": entity_type,
                "label": label,
                "icon": ICONS[entity_type],
                "data": data
            }

            st.session_state.library.append(ent)
            st.success(f"Saved: {label}")
            st.rerun()

# ------------------------------------------------------
# SEARCH & ADD TO CANVAS
# ------------------------------------------------------
st.sidebar.divider()
st.sidebar.markdown("### 🔍 Search Library")

query = st.sidebar.text_input("Search")
filtered = [
    e for e in st.session_state.library
    if not query or query.lower() in e["label"].lower() or query.lower() in str(e["data"]).lower()
]

for ent in filtered:
    if st.sidebar.button(f"➕ {ent['label']}", key=f"lib_{ent['id']}"):
        if ent not in st.session_state.canvas:
            st.session_state.canvas.append(ent)
            st.rerun()

# ------------------------------------------------------
# MAIN LAYOUT (i2 Classic: Palette → Canvas → Details)
# ------------------------------------------------------
left, right = st.columns([4, 1])

# ------------------------------------------------------
# CANVAS
# ------------------------------------------------------
with left:
    st.markdown("## 🧩 Link Analysis Canvas (i2 Classic White)")

    net = Network(
        height="800px",
        bgcolor="#ffffff",
        font_color="#000000",
        directed=True
    )

    net.set_options("""
    var options = {
        "nodes": {
            "shape": "image",
            "brokenImage": "assets/icons/person.svg",
            "font": {"size": 14}
        },
        "edges": {
            "color": "#444444",
            "arrows": "to",
            "smooth": false
        },
        "physics": {"enabled": true}
    }
    """)

    # Add nodes
    for ent in st.session_state.canvas:
        tooltip = "<br>".join([f"<b>{ent['label']}</b>"] + [
            f"{k}: {v}" for k,v in ent["data"].items() if v
        ])

        net.add_node(
            ent["id"],
            label=ent["label"],
            title=tooltip,
            image=ent["icon"],
            size=50
        )

    # Add links
    for link in st.session_state.links:
        net.add_edge(link["from"], link["to"], label=link["type"])

    html = net.generate_html()
    components.html(html, height=800)

    # Link Creation
    st.markdown("### ➕ Create Link")

    if len(st.session_state.canvas) >= 2:
        ids = {e["id"]: e["label"] for e in st.session_state.canvas}
        from_id = st.selectbox("From", ids.keys(), format_func=lambda x: ids[x])
        to_id = st.selectbox("To", ids.keys(), format_func=lambda x: ids[x])
        link_type = st.text_input("Relationship (e.g., Calls, Owns, Lives At)")

        if st.button("Add Link"):
            st.session_state.links.append({"from": from_id, "to": to_id, "type": link_type})
            st.rerun()

# ------------------------------------------------------
# RIGHT PANEL — REMOVE ENTITIES
# ------------------------------------------------------
with right:
    st.markdown("## 🗑️ Canvas Entities")

    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"remove_{ent['id']}"):
            st.session_state.canvas = [
                e for e in st.session_state.canvas if e["id"] != ent["id"]
            ]
            st.session_state.links = [
                l for l in st.session_state.links
                if l["from"] != ent["id"] and l["to"] != ent["id"]
            ]
            st.rerun()

# ------------------------------------------------------
# EXPORT
# ------------------------------------------------------
st.divider()
st.markdown("## 📤 Export Project")

if st.session_state.canvas:
    df = pd.DataFrame([
        {"Label": e["label"], "Type": e["type"], **e["data"]}
        for e in st.session_state.canvas
    ])
    st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")

if st.session_state.links:
    df_links = pd.DataFrame(st.session_state.links)
    st.download_button("Download Links CSV", df_links.to_csv(index=False), "links.csv")
