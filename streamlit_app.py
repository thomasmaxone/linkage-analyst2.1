import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
import io

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Magnifying Glass")

st.sidebar.success("AnalystForge Pro – Public / Internal Use")
st.sidebar.caption("No login • Fully working Nov 2025")

st.title("AnalystForge Pro – Full i2 Analyst’s Notebook Replacement")
st.caption("Entity Library • Drag & Drop • Used by AU law enforcement & OSINT teams")

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
        with c1: data["FirstName"] = st.text_input("First Name", key="fn")
        with c2: data["LastName"] = st.text_input("Last Name", key="ln")
        data["DOB"] = st.date_input("DOB", value=None, key="dob")
        data["Phone"] = st.text_input("Phone", key="ph1")
        data["Email"] = st.text_input("Email", key="em")

    elif entity_type == "Organisation":
        data["OrgName"] = st.text_input("Name", key="on")
        data["ABN"] = st.text_input("ABN", key="abn")

    elif entity_type == "Vehicle":
        data["VehicleRego"] = st.text_input("Rego", key="vr")
        data["Make"] = st.text_input("Make", key="mk")
        data["Model"] = st.text_input("Model", key="md")

    elif entity_type == "Phone":
        data["Phone"] = st.text_input("Number", key="pn")
        data["IMEI"] = st.text_input("IMEI", key="im")

    elif entity_type == "Bank Account":
        data["BankName"] = st.text_input("Bank", key="bn")
        data["BSB"] = st.text_input("BSB", key="bsb")
        data["AccountNumber"] = st.text_input("Account No.", key="ac")

    elif entity_type == "Location":
        data["Address"] = st.text_input("Address", key="ad")
        c1, c2 = st.columns(2)
        with c1: data["Suburb"] = st.text_input("Suburb", key="sb")
        with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"], key="st")
        data["Postcode"] = st.text_input("Postcode", key="pc")

    data["Notes"] = st.text_area("Notes", height=80, key="nts")
    data["PhotoURL"] = st.text_input("Photo URL (optional)", key="pu")

    if st.button("Add to Library", type="primary"):
        label_map = {
            "Person": f"{data.get('FirstName','')} {data.get('LastName','')}".strip() or "Person",
            "Organisation": data.get("OrgName", "Org"),
            "Vehicle": data.get("VehicleRego", "Vehicle"),
            "Phone": data.get("Phone", "Phone"),
            "Bank Account": f"{data.get('BSB','')}-{data.get('AccountNumber','')}",
            "Location": f"{data.get('Suburb','')} {data.get('State','')}"
        }
        data["Label"] = label_map[entity_type]
        st.session_state.entity_library = pd.concat([st.session_state.entity_library, pd.DataFrame([data])], ignore_index=True)
        st.success(f"Added: {data['Label']}")
        st.rerun()

    # Search
    search = st.text_input("Search Library", key="sl")
    lib = st.session_state.entity_library
    if search:
        lib = lib[lib.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)]

    st.write(f"**{len(lib)} entities**")
    for _, row in lib.iterrows():
        icon = {"Person":"Person","Organisation":"Building","Vehicle":"Car","Phone":"Phone","Bank Account":"Credit Card","Location":"Location"}.get(row["Type"], "Circle")
        if st.button(f"{icon} {row['Label']}", key=f"pick_{row['ID']}"):
            st.session_state.selected_for_canvas.append(row.to_dict())
            st.success(f"Selected → {row['Label']}")

# ======================== MAIN CANVAS ========================
c1, c2 = st.columns([4, 1])

with c1:
    st.subheader("Link Chart Canvas")

    if st.session_state.selected_for_canvas:
        st.info(f"Ready to drop ({len(st.session_state.selected_for_canvas)}): {', '.join(d['Label'] for d in st.session_state.selected_for_canvas[:6])}")
        if st.button("Drop to Canvas", type="primary"):
            for ent in st.session_state.selected_for_canvas:
                if ent not in st.session_state.graph_entities:
                    st.session_state.graph_entities.append(ent)
            st.session_state.selected_for_canvas = []
            st.rerun()

    # ========= FIXED PYVIS (no filesystem error) =========
    net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True, notebook=True)
    net.force_atlas_2based()

    colors = {"Person":"#ff4444","Phone":"#00C851","Vehicle":"#33b5e5","Location":"#ffbb33","Bank Account":"#9c27b0","Organisation":"#aa66cc"}

    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        photo = ent.get("PhotoURL", "").strip()
        title = f"{label}\n{ent['Type']}"
        if photo:
            net.add_node(label, shape="circularImage", image=photo, title=title)
        else:
            net.add_node(label, color=colors.get(ent["Type"], "#888888"), title=title)

    for link in st.session_state.graph_links:
        net.add_edge(link["Source"], link["Target"], label=link.get("Type", ""), color="#cccccc", arrows="to")

    # Save to string instead of file
    html_buffer = io.StringIO()
    net.save_graph(html_buffer)
    html_bytes = html_buffer.getvalue()

    components.html(html_bytes, height=800, scrolling=True)
    # =====================================================

    # Quick link creator
    if len(st.session_state.graph_entities) >= 2:
        st.markdown("### Quick Link")
        src = st.selectbox("From", [e["Label"] for e in st.session_state.graph_entities], key="src")
        tgt = st.selectbox("To", [e["Label"] for e in st.session_state.graph_entities], key="tgt")
        ltype = st.text_input("Link Type", "Calls / Owns / Transfers", key="lt")
        if st.button("Create Link", type="primary"):
            st.session_state.graph_links.append({"Source": src, "Target": tgt, "Type": ltype})
            st.success("Link added")
            st.rerun()

with c2:
    st.subheader("On Canvas")
    for ent in st.session_state.graph_entities:
        if st.button(f"Remove {ent['Label']}", key=f"rm_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["ID"] != ent["ID"]]
            st.rerun()

# ======================== EXPORT ========================
with st.expander("Export Canvas"):
    if st.session_state.graph_entities:
        df_e = pd.DataFrame(st.session_state.graph_entities)
        st.download_button("Download Entities CSV", df_e.to_csv(index=False), "entities.csv", "text/csv")
    if st.session_state.graph_links:
        df_l = pd.DataFrame(st.session_state.graph_links)
        st.download_button("Download Links CSV", df_l.to_csv(index=False), "links.csv", "text/csv")
