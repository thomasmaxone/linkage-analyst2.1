import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Magnifying Glass")

# ======================== NO LOGIN – DIRECT ACCESS ========================
st.sidebar.success("AnalystForge Pro – Public / Internal Use")
st.sidebar.caption("Login removed as requested – Nov 2025")

st.title("AnalystForge Pro – Full i2 Analyst’s Notebook Replacement")
st.caption("Entity Library • Drag & Drop • Used daily by AU law enforcement & OSINT teams")

# ======================== INITIALISE DATA ========================
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
        with c1: data["FirstName"] = st.text_input("First Name", key="p1")
        with c2: data["LastName"] = st.text_input("Last Name", key="p2")
        data["DOB"] = st.date_input("Date of Birth", value=None, key="p3")
        data["Phone"] = st.text_input("Phone", key="p4")
        data["Email"] = st.text_input("Email", key="p5")

    elif entity_type == "Organisation":
        data["OrgName"] = st.text_input("Organisation Name", key="o1")
        data["ABN"] = st.text_input("ABN", key="o2")

    elif entity_type == "Vehicle":
        data["VehicleRego"] = st.text_input("Registration", key="v1")
        data["Make"] = st.text_input("Make", key="v2")
        data["Model"] = st.text_input("Model", key="v3")

    elif entity_type == "Phone":
        data["Phone"] = st.text_input("Phone Number", key="ph1")
        data["IMEI"] = st.text_input("IMEI (optional)", key="ph2")

    elif entity_type == "Bank Account":
        data["BankName"] = st.text_input("Bank", key="b1")
        data["BSB"] = st.text_input("BSB", key="b2")
        data["AccountNumber"] = st.text_input("Account Number", key="b3")

    elif entity_type == "Location":
        data["Address"] = st.text_input("Street Address", key="l1")
        c1, c2 = st.columns(2)
        with c1: data["Suburb"] = st.text_input("Suburb", key="l2")
        with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"], key="l3")
        data["Postcode"] = st.text_input("Postcode", max_chars=4, key="l4")

    data["Notes"] = st.text_area("Notes", height=80, key="notes")
    data["PhotoURL"] = st.text_input("Photo URL (optional)", placeholder="https://...", key="photo")

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
        st.success(f"Added → {data['Label']}")
        st.rerun()

    # Search
    search = st.text_input("Search Library", key="search_lib")
    lib = st.session_state.entity_library
    if search:
        lib = lib[lib.apply(lambda row: search.lower() in str(row.values).lower(), axis=1)]

    st.write(f"**{len(lib)} entities**")
    for _, row in lib.iterrows():
        icon = {"Person":"Person","Organisation":"Building","Vehicle":"Car","Phone":"Phone","Bank Account":"Credit Card","Location":"Location"}.get(row["Type"], "Circle")
        if st.button(f"{icon} {row['Label']}", key=f"pick_{row['ID']}"):
            st.session_state.selected_for_canvas.append(row.to_dict())
            st.success(f"Selected: {row['Label']} → Drop to canvas")

# ======================== MAIN CANVAS ========================
c1, c2 = st.columns([4, 1])

with c1:
    st.subheader("Link Chart Canvas")

    if st.session_state.selected_for_canvas:
        st.info(f"Ready ({len(st.session_state.selected_for_canvas)}): {', '.join([x['Label'] for x in st.session_state.selected_for_canvas[:6]])}")
        if st.button("Drop Selected to Canvas", type="primary"):
            for ent in st.session_state.selected_for_canvas:
                if ent not in st.session_state.graph_entities:
                    st.session_state.graph_entities.append(ent)
            st.session_state.selected_for_canvas.clear()
            st.rerun()

    net = Network(height="800px", bgcolor="#0e1117", font_color="#fff", directed=True)
    net.force_atlas_2based()

    colors = {"Person":"#ff4444","Phone":"#00C851","Vehicle":"#33b5e5","Location":"#ffbb33","Bank Account":"#9c27b0","Organisation":"#aa66cc"}

    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        photo = ent.get("PhotoURL", "").strip()
        if photo:
            net.add_node(label, shape="circularImage", image=photo)
        else:
            net.add_node(label, color=colors.get(ent["Type"], "#888888"), title=f"{label}\n{ent['Type']}")

    for link in st.session_state.graph_links:
        net.add_edge(link["Source"], link["Target"], label=link.get("Type", ""), color="#cccccc", arrows="to")

    net.show("canvas.html")
    components.html(open("canvas.html", "r", encoding="utf-8").read(), height=800, scrolling=True)

    # Quick link
    if len(st.session_state.graph_entities) >= 2:
        st.markdown("### Quick Link")
        from_ent = st.selectbox("From", [e["Label"] for e in st.session_state.graph_entities])
        to_ent = st.selectbox("To", [e["Label"] for e in st.session_state.graph_entities])
        link_type = st.text_input("Link Type", "Calls / Owns / Transfers")
        if st.button("Create Link"):
            st.session_state.graph_links.append({"Source": from_ent, "Target": to_ent, "Type": link_type})
            st.success("Link created")
            st.rerun()

with c2:
    st.subheader("On Canvas")
    for ent in st.session_state.graph_entities:
        if st.button(f"Remove {ent['Label']}", key=f"del_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["ID"] != ent["ID"]]
            st.rerun()

# ======================== EXPORT ========================
with st.expander("Export Canvas"):
    if st.session_state.graph_entities:
        ent_df = pd.DataFrame(st.session_state.graph_entities)
        st.download_button("Entities CSV", ent_df.to_csv(index=False), "entities.csv", "text/csv")
    if st.session_state.graph_links:
        link_df = pd.DataFrame(st.session_state.graph_links)
        st.download_button("Links CSV", link_df.to_csv(index=False), "links.csv", "text/csv")
