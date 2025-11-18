import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# Dark professional theme – white canvas only
st.markdown("""
<style>
    .reportview-container {background: #0e1117;}
    .sidebar .sidebar-content {background: #1a1f2d;}
    header {background: #0e1117 !important;}
    h1, h2, h3 {color: #ffffff;}
    .stButton>button {background: #2c5282; color: white; border: none;}
    .stButton>button:hover {background: #4299e1;}
</style>
""", unsafe_allow_html=True)

st.sidebar.success("AnalystForge Pro – AU Police 2025")
st.sidebar.caption("Save & Reset workflow • White canvas • Physical icons")

st.title("AnalystForge Pro – i2 Analyst’s Notebook Replacement")
st.caption("White canvas • Save & Reset entity entry • Used daily across Australia")

# Icons
ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/car-front.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house.svg"
}

# Initialise session state
for key in ["library", "canvas", "links"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ======================== ADD ENTITY (WITH SAVE & RESET) ========================
with st.sidebar.expander("➕ Add New Entity to Project", expanded=True):
    entity_type = st.selectbox("Entity Type", list(ICONS.keys()), key="new_type")

    # Use a form so we can reset everything with one button
    with st.form(key="entity_form"):
        data = {}

        if entity_type == "Person":
            c1, c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name")
            with c2: data["Last Name"] = st.text_input("Last Name")
            data["DOB"] = st.date_input("Date of Birth", value=None)
            data["Phone"] = st.text_input("Phone Number")
            data["Email"] = st.text_input("Email (optional)")

        elif entity_type == "Organisation":
            data["Name"] = st.text_input("Organisation Name")
            data["ABN"] = st.text_input("ABN / ACN")

        elif entity_type == "Vehicle":
            data["Registration"] = st.text_input("Registration Plate")
            c1, c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")
            data["Colour"] = st.text_input("Colour (optional)")

        elif entity_type == "Phone":
            data["Number"] = st.text_input("Phone Number")
            data["IMEI"] = st.text_input("IMEI (optional)")
            data["Provider"] = st.text_input("Provider (optional)")

        elif entity_type == "Bank Account":
            data["Bank"] = st.text_input("Bank Name")
            c1, c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account Number"] = st.text_input("Account Number")
            data["Account Name"] = st.text_input("Account Holder Name")

        elif entity_type == "Location":
            data["Street Address"] = st.text_input("Street Address")
            c1, c2 = st.columns(2)
            with c1: data["Suburb"] = st.text_input("Suburb")
            with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])
            data["Postcode"] = st.text_input("Postcode", max_chars=4)

        # THE SAVE BUTTON
        save_btn = st.form_submit_button("Save Entity to Project", type="primary")

        if save_btn:
            # Generate label
            label = {
                "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip() or "Unknown Person",
                "Organisation": data.get("Name", "Unknown Org"),
                "Vehicle": data.get("Registration", "Unknown Vehicle"),
                "Phone": data.get("Number", "Unknown Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account Number','')}",
                "Location": data.get("Street Address", "Unknown Location")
            }[entity_type]

            new_entity = {
                "id": str(uuid.uuid4())[:8],
                "type": entity_type,
                "label": label,
                "data": data,
                "icon": ICONS[entity_type]
            }

            st.session_state.library.append(new_entity)
            st.success(f"Saved: {label}")
            st.rerun()  # This resets the entire form automatically

    # Search existing entities in library
    search = st.text_input("Search Library", key="lib_search")
    filtered = [e for e in st.session_state.library 
                if not search or search.lower() in e["label"].lower() or search.lower() in str(e["data"]).lower()]

    st.write(f"**{len(filtered)} entities in project**")
    for ent in filtered:
        if st.button(f"{ent['type']} {ent['label']}", key=f"add_{ent['id']}"):
            if ent not in st.session_state.canvas:
                st.session_state.canvas.append(ent)
                st.success(f"Added to canvas: {ent['label']}")
                st.rerun()

# ======================== CANVAS (WHITE) ========================
c1, c2 = st.columns([4,1])

with c1:
    st.subheader("Link Analysis Canvas")

    net = Network(height="850px", bgcolor="#ffffff", font_color="#000000", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"enabled": true},
      "nodes": {"font": {"size": 16}},
      "edges": {"color": "#2c5282", "width": 3, "arrows": "to"}
    }
    """)

    # Add nodes
    for ent in st.session_state.canvas:
        lines = [f"<b>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone"): lines.append(ent["data"]["Phone"])
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"): lines.append(ent["data"]["Registration"])
        if ent["type"] == "Bank Account": lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account Number','')}")
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b> ({ent['type']})"] + 
                             [f"{k}: {v if not isinstance(v,date) else v.strftime('%d/%m/%Y')}" 
                              for k,v in ent["data"].items() if v and v != date(1,1,1)])

        net.add_node(ent["id"], label=label_html, shape="image", image=ent["icon"],
                     title=tooltip, size=50)

    # Add links
    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas] and link["to"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"])

    components.html(net.generate_html(), height=850, scrolling=True)

    # Link creator
    if len(st.session_state.canvas) >= 2:
        st.markdown("### Create Link")
        id_to_label = {e["id"]: e["label"] for e in st.session_state.canvas}
        from_id = st.selectbox("From", options=list(id_to_label.keys()), format_func=lambda x: id_to_label[x])
        to_id = st.selectbox("To", options=list(id_to_label.keys()), format_func=lambda x: id_to_label[x])
        link_type = st.text_input("Link Type", "Owns • Calls • Lives At • Works At")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": from_id, "to": to_id, "type": link_type})
            st.success("Link created")
            st.rerun()

with c2:
    st.subheader("On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"rem_{ent['id']}"):
            st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != ent["id"]]
            st.session_state.links = [l for l in st.session_state.links if l["from"] != ent["id"] and l["to"] != ent["id"]]
            st.rerun()

# Export
with st.expander("Export Project"):
    if st.session_state.canvas:
        export = [{"Label": e["label"], "Type": e["type"], **e["data"]} for e in st.session_state.canvas]
        df = pd.DataFrame(export)
        st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")
    if st.session_state.links:
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        links_exp = [{"From": labels.get(l["from"],"?"), "To": labels.get(l["to"],"?"), "Type": l["type"]} for l in st.session_state.links]
        st.download_button("Download Links CSV", pd.DataFrame(links_exp).to_csv(index=False), "links.csv")
