import streamlit as st
import pandas as pd
import base64
from pyvis.network import Network
import streamlit.components.v1 as components
import plotly.express as px
from datetime import datetime
import uuid

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Magnifying Glass")

# === Simple login (same as before) ===
if "auth" not in st.session_state:
    with st.sidebar.form("login"):
        st.write("### AnalystForge Pro")
        user = st.text_input("Username", "investigator")
        pw = st.text_input("Password", type="password", "analyst2025")
        if st.form_submit_button("Login"):
            if user == "investigator" and pw == "analyst2025":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong credentials")
    st.stop()
else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        del st.session_state.auth
        st.rerun()

st.title("AnalystForge Pro – Full i2 Analyst’s Notebook Replacement")
st.caption("Now with Entity Library + Drag & Drop (AU law enforcement standard 2025)")

# === Initialise Entity Library (saved forever in session) ===
if "entity_library" not in st.session_state:
    st.session_state.entity_library = pd.DataFrame(columns=[
        "ID", "Type", "Label", "FirstName", "LastName", "DOB", "Phone", "Email",
        "OrgName", "ABN", "VehicleRego", "Make", "Model", "IMEI", "BankName",
        "BSB", "AccountNumber", "Address", "Suburb", "State", "Postcode", "Notes", "PhotoURL"
    ])

# === Sidebar: Entity Library + Add New ===
with st.sidebar.expander("Entity Library", expanded=True):
    st.subheader("Add New Entity")
    entity_type = st.selectbox("Type", [
        "Person", "Organisation", "Vehicle", "Phone", "Bank Account", "Location"
    ], key="new_type")

    form_data = {"Type": entity_type, "ID": str(uuid.uuid4())[:8]}

    if entity_type == "Person":
        col1, col2 = st.columns(2)
        with col1: form_data["FirstName"] = st.text_input("First Name")
        with col2: form_data["LastName"] = st.text_input("Last Name")
        form_data["DOB"] = st.date_input("DOB", value=None)
        form_data["Phone"] = st.text_input("Phone")
        form_data["Email"] = st.text_input("Email")

    elif entity_type == "Organisation":
        form_data["OrgName"] = st.text_input("Organisation Name", placeholder="ACME Pty Ltd")
        form_data["ABN"] = st.text_input("ABN")

    elif entity_type == "Vehicle":
        form_data["VehicleRego"] = st.text_input("Registration", placeholder="ABC-123")
        form_data["Make"] = st.text_input("Make", "Toyota")
        form_data["Model"] = st.text_input("Model", "Camry")

    elif entity_type == "Phone":
        form_data["Phone"] = st.text_input("Phone Number", placeholder="0412 345 678")
        form_data["IMEI"] = st.text_input("IMEI (optional)")

    elif entity_type == "Bank Account":
        form_data["BankName"] = st.text_input("Bank", "Commonwealth")
        form_data["BSB"] = st.text_input("BSB", "062-000")
        form_data["AccountNumber"] = st.text_input("Account Number")

    elif entity_type == "Location":
        form_data["Address"] = st.text_input("Street Address")
        col1, col2 = st.columns(2)
        with col1: form_data["Suburb"] = st.text_input("Suburb")
        with col2: form_data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])
        form_data["Postcode"] = st.text_input("Postcode", max_chars=4)

    form_data["Notes"] = st.text_area("Notes", height=80)
    form_data["PhotoURL"] = st.text_input("Photo URL (optional)", placeholder="https://example.com/photo.jpg")

    if st.button("Add to Library", type="primary"):
        label_fields = {
            "Person": f"{form_data.get('FirstName','')} {form_data.get('LastName','')}".strip() or "Unnamed Person",
            "Organisation": form_data.get("OrgName", "Unnamed Org"),
            "Vehicle": form_data.get("VehicleRego", "Unknown Rego"),
            "Phone": form_data.get("Phone", "Unknown Phone"),
            "Bank Account": f"{form_data.get('BSB','???')}-{form_data.get('AccountNumber','???')}",
            "Location": f"{form_data.get('Suburb','')} {form_data.get('State','')}"
        }
        form_data["Label"] = label_fields[entity_type]
        new_row = pd.DataFrame([form_data])
        st.session_state.entity_library = pd.concat([st.session_state.entity_library, new_row], ignore_index=True)
        st.success(f"Added: {form_data['Label']}")

    # Search & Library List
    search = st.text_input("Search Library", placeholder="Type to filter...")
    if search:
        lib = st.session_state.entity_library[st.session_state.entity_library.apply(
            lambda row: search.lower() in str(row.values).lower(), axis=1)]
    else:
        lib = st.session_state.entity_library

    st.write(f"**{len(lib)} entities**")
    for _, row in lib.iterrows():
        label = row["Label"]
        typ = row["Type"]
        color = {"Person":"🔴","Organisation":"🟦","Vehicle":"🚗","Phone":"📱","Bank Account":"🏦","Location":"📍"}.get(typ,"⚪")
        if st.button(f"{color} {label}", key=row["ID"]):
            if "selected_for_canvas" not in st.session_state:
                st.session_state.selected_for_canvas = []
            st.session_state.selected_for_canvas.append(row.to_dict())
            st.success(f"Ready to drop: {label}")

# === Main Canvas Area ===
if "graph_entities" not in st.session_state:
    st.session_state.graph_entities = []
if "graph_links" not in st.session_state:
    st.session_state.graph_links = []

col_main, col_right = st.columns([4,1])

with col_main:
    st.subheader("Link Chart Canvas")

    # Drag-and-drop zone
    if "selected_for_canvas" in st.session_state and st.session_state.selected_for_canvas:
        st.info(f"Drag these onto the canvas: {', '.join([x['Label'] for x in st.session_state.selected_for_canvas])}")

    # Build PyVis network
    net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True)
    net.force_atlas_2based()

    # Add entities already on canvas
    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        typ = ent["Type"]
        photo = ent.get("PhotoURL","")
        if photo:
            net.add_node(label, shape="circularImage", image=photo, title=str(ent))
        else:
            color = {"Person":"#ff4444","Phone":"#00C851","Vehicle":"#33b5e5","Location":"#ffbb33","Bank Account":"#9c27b0","Organisation":"#aa66cc"}.get(typ,"#888")
            net.add_node(label, title=str(ent), color=color)

    # Add links
    for link in st.session_state.graph_links:
        net.add_edge(link["Source"], link["Target"], label=link.get("Type","Link"), color="#aaaaaa", arrows="to")

    net.show("canvas.html")
    components.html(open("canvas.html","r",encoding="utf-8").read(), height=800, scrolling=True)

    # Add selected entities to canvas
    if st.button("Drop Selected Entities onto Canvas"):
        for ent in st.session_state.selected_for_canvas:
            if ent not in st.session_state.graph_entities:
                st.session_state.graph_entities.append(ent)
        st.session_state.selected_for_canvas = []
        st.rerun()

    # Quick link creator
    if len(st.session_state.graph_entities) >= 2:
        st.write("### Quick Link")
        e1 = st.selectbox("From", options=[e["Label"] for e in st.session_state.graph_entities], key="l1")
        e2 = st.selectbox("To", options=[e["Label"] for e in st.session_state.graph_entities], key="l2")
        link_type = st.text_input("Link Type", "Meets/Calls/Transfers")
        if st.button("Create Link"):
            st.session_state.graph_links.append({"Source":e1, "Target":e2, "Type":link_type})
            st.success(f"Linked {e1} → {e2}")

with col_right:
    st.subheader("On Canvas")
    st.write(f"{len(st.session_state.graph_entities)} entities")
    for ent in st.session_state.graph_entities:
        if st.button(f"Remove {ent['Label']}", key=f"rem_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["Label"] != ent["Label"]]
            st.rerun()

# Export tab
with st.expander("Export Canvas"):
    if st.session_state.graph_entities:
        df_ent = pd.DataFrame(st.session_state.graph_entities)
        csv1 = df_ent.to_csv(index=False)
        b64 = base64.b64encode(csv1.encode()).decode()
        st.download_button("Download Entities CSV", csv1, "canvas_entities.csv")
    if st.session_state.graph_links:
        df_link = pd.DataFrame(st.session_state.graph_links)
        csv2 = df_link.to_csv(index=False)
        st.download_button("Download Links CSV", csv2, "canvas_links.csv")
