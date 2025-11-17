import streamlit as st
import pandas as pd
import base64
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Magnifying Glass")

# ======================== FIXED LOGIN (no more syntax errors) ========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.sidebar:
        st.header("Login to AnalystForge Pro")
        username = st.text_input("Username", value="investigator")
        password = st.text_input("Password", type="password")  # Fixed order!
        if st.button("Login", type="primary"):
            if username == "investigator" and password == "analyst2025":
                st.session_state.authenticated = True
                st.session_state.user = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
    st.stop()
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ======================== MAIN APP ========================
st.title("AnalystForge Pro – Full i2 Analyst’s Notebook Replacement")
st.caption("Entity Library • Drag & Drop • Australian Law Enforcement Standard 2025")

# Initialize data
if "entity_library" not in st.session_state:
    st.session_state.entity_library = pd.DataFrame(columns=[
        "ID", "Type", "Label", "FirstName", "LastName", "DOB", "Phone", "Email",
        "OrgName", "ABN", "VehicleRego", "Make", "Model", "IMEI", "BankName",
        "BSB", "AccountNumber", "Address", "Suburb", "State", "Postcode", "Notes", "PhotoURL"
    ])

if "graph_entities" not in st.session_state:
    st.session_state.graph_entities = []
if "graph_links" not in st.session_state:
    st.session_state.graph_links = []
if "selected_for_canvas" not in st.session_state:
    st.session_state.selected_for_canvas = []

# ======================== SIDEBAR: Entity Library ========================
with st.sidebar.expander("Entity Library", expanded=True):
    st.subheader("Add New Entity")
    entity_type = st.selectbox("Type", [
        "Person", "Organisation", "Vehicle", "Phone", "Bank Account", "Location"
    ])

    data = {"Type": entity_type, "ID": str(uuid.uuid4())[:8]}

    if entity_type == "Person":
        c1, c2 = st.columns(2)
        with c1: data["FirstName"] = st.text_input("First Name", key="fn")
        with c2: data["LastName"] = st.text_input("Last Name", key="ln")
        data["DOB"] = st.date_input("Date of Birth", value=None, key="dob")
        data["Phone"] = st.text_input("Phone", key="pph")
        data["Email"] = st.text_input("Email", key="pem")

    elif entity_type == "Organisation":
        data["OrgName"] = st.text_input("Organisation Name", key="orgn")
        data["ABN"] = st.text_input("ABN", key="abn")

    elif entity_type == "Vehicle":
        data["VehicleRego"] = st.text_input("Registration", key="rego")
        data["Make"] = st.text_input("Make", key="make")
        data["Model"] = st.text_input("Model", key="model")

    elif entity_type == "Phone":
        data["Phone"] = st.text_input("Phone Number", key="phnum")
        data["IMEI"] = st.text_input("IMEI (optional)", key="imei")

    elif entity_type == "Bank Account":
        data["BankName"] = st.text_input("Bank", key="bank")
        data["BSB"] = st.text_input("BSB", key="bsb")
        data["AccountNumber"] = st.text_input("Account Number", key="acc")

    elif entity_type == "Location":
        data["Address"] = st.text_input("Street Address", key="addr")
        c1, c2 = st.columns(2)
        with c1: data["Suburb"] = st.text_input("Suburb", key="sub")
        with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"], key="state")
        data["Postcode"] = st.text_input("Postcode", max_chars=4, key="pc")

    data["Notes"] = st.text_area("Notes", height=80, key="notes")
    data["PhotoURL"] = st.text_input("Photo URL (optional)", key="photo")

    if st.button("Add to Library", type="primary"):
        label_map = {
            "Person": f"{data.get('FirstName','')} {data.get('LastName','')}".strip() or "Unnamed Person",
            "Organisation": data.get("OrgName", "Unnamed Org"),
            "Vehicle": data.get("VehicleRego", "Unknown Rego"),
            "Phone": data.get("Phone", "Unknown Phone"),
            "Bank Account": f"{data.get('BSB','???')}-{data.get('AccountNumber','???')}",
            "Location": f"{data.get('Suburb','')} {data.get('State','')}"
        }
        data["Label"] = label_map[entity_type]
        st.session_state.entity_library = pd.concat([st.session_state.entity_library, pd.DataFrame([data])], ignore_index=True)
        st.success(f"Added: {data['Label']}")
        st.rerun()

    # Search library
    search = st.text_input("Search Library", placeholder="Name, phone, rego...", key="search")
    display_lib = st.session_state.entity_library
    if search:
        display_lib = display_lib[display_lib.apply(lambda row: search.lower() in str(row.values).lower(), axis=1)]

    st.write(f"**{len(display_lib)} entities found**")
    for _, row in display_lib.iterrows():
        icon = {"Person":"Person","Organisation":"Building","Vehicle":"Car","Phone":"Phone","Bank Account":"Credit Card","Location":"Location"}.get(row["Type"], "Circle")
        if st.button(f"{icon} {row['Label']}", key=f"lib_{row['ID']}"):
            st.session_state.selected_for_canvas.append(row.to_dict())
            st.success(f"Selected: {row['Label']} → Click 'Drop to Canvas'")

# ======================== MAIN CANVAS ========================
col1, col2 = st.columns([4, 1])

with col1:
    st.subheader("Link Chart Canvas")

    if st.session_state.selected_for_canvas:
        st.info(f"Ready to drop ({len(st.session_state.selected_for_canvas)}): {', '.join([x['Label'] for x in st.session_state.selected_for_canvas[:5]])}")
        if st.button("Drop Selected to Canvas", type="primary"):
            for ent in st.session_state.selected_for_canvas:
                if ent not in st.session_state.graph_entities:
                    st.session_state.graph_entities.append(ent)
            st.session_state.selected_for_canvas = []
            st.rerun()

    # Build network
    net = Network(height="800px", bgcolor="#0e1117", font_color="#fff", directed=True)
    net.force_atlas_2based()

    colors = {"Person":"#ff4444", "Phone":"#00C851", "Vehicle":"#33b5e5", "Location":"#ffbb33", "Bank Account":"#9c27b0", "Organisation":"#aa66cc"}

    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        photo = ent.get("PhotoURL", "")
        if photo and photo.strip():
            net.add_node(label, shape="circularImage", image=photo, title=label)
        else:
            net.add_node(label, color=colors.get(ent["Type"], "#888888"), title=f"{label}\n{ent['Type']}")

    for link in st.session_state.graph_links:
        net.add_edge(link["Source"], link["Target"], label=link.get("Type", ""), color="#cccccc", arrows="to")

    net.show("canvas.html")
    components.html(open("canvas.html", "r", encoding="utf-8").read(), height=800, scrolling=True)

    # Quick link creator
    if len(st.session_state.graph_entities) >= 2:
        st.markdown("### Quick Create Link")
        e1 = st.selectbox("From", [e["Label"] for e in st.session_state.graph_entities])
        e2 = st.selectbox("To", [e["Label"] for e in st.session_state.graph_entities])
        link_type = st.text_input("Link Type (e.g. Calls, Owns, Transfers)", "Calls")
        if st.button("Add Link"):
            st.session_state.graph_links.append({"Source": e1, "Target": e2, "Type": link_type})
            st.success(f"Link added: {e1} → {e2}")
            st.rerun()

with col2:
    st.subheader("On Canvas")
    for ent in st.session_state.graph_entities:
        if st.button(f"Remove {ent['Label']}", key=f"rem_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["ID"] != ent["ID"]]
            st.rerun()

# ======================== EXPORT ========================
with st.expander("Export Canvas Data"):
    if st.session_state.graph_entities:
        ent_df = pd.DataFrame(st.session_state.graph_entities)
        st.download_button("Download Entities CSV", ent_df.to_csv(index=False), "entities.csv", "text/csv")
    if st.session_state.graph_links:
        link_df = pd.DataFrame(st.session_state.graph_links)
        st.download_button("Download Links CSV", link_df.to_csv(index=False), "links.csv", "text/csv")
