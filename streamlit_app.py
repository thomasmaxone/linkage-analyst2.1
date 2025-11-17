import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# Header
st.sidebar.success("AnalystForge Pro – Australian Law Enforcement Standard")
st.sidebar.caption("Real icons • Full linking • Nov 2025")

st.title("AnalystForge Pro – i2 Analyst’s Notebook Replacement")
st.caption("With proper entity symbols • Drag & drop • Full node linking")

# Entity type → icon + color (exact i2 style)
ENTITY_STYLES = {
    "Person":       {"icon": "Person", "color": "#e74c3c"},
    "Organisation": {"icon": "Office Building", "color": "#9b59b6"},
    "Vehicle":      {"icon": "Car", "color": "#3498db"},
    "Phone":        {"icon": "Phone", "color": "#2ecc71"},
    "Bank Account": {"icon": "Bank", "color": "#f1c40f"},
    "Location":     {"icon": "Location Pin", "color": "#e67e22"}
}

# Initialise data
if "entity_library" not in st.session_state:
    st.session_state.entity_library = pd.DataFrame(columns=["ID","Type","Label","Data","PhotoURL"])
if "graph_entities" not in st.session_state:
    st.session_state.graph_entities = []
if "graph_links" not in st.session_state:
    st.session_state.graph_links = []
if "selected" not in st.session_state:
    st.session_state.selected = []

# ======================== SIDEBAR: Entity Library ========================
with st.sidebar.expander("Entity Library", expanded=True):
    st.subheader("Add New Entity")
    entity_type = st.selectbox("Type", list(ENTITY_STYLES.keys()))

    data = {"Type": entity_type, "ID": str(uuid.uuid4())[:8], "Data": {}, "PhotoURL": ""}

    # Form fields per type
    if entity_type == "Person":
        c1,c2 = st.columns(2)
        with c1: data["Data"]["First"] = st.text_input("First Name")
        with c2: data["Data"]["Last"] = st.text_input("Last Name")
        data["Data"]["DOB"] = st.date_input("DOB", value=None)
        data["Data"]["Phone"] = st.text_input("Phone")
        data["PhotoURL"] = st.text_input("Photo URL (optional)")

    elif entity_type == "Organisation":
        data["Data"]["Name"] = st.text_input("Organisation Name")
        data["Data"]["ABN"] = st.text_input("ABN")

    elif entity_type == "Vehicle":
        data["Data"]["Rego"] = st.text_input("Registration")
        c1,c2 = st.columns(2)
        with c1: data["Data"]["Make"] = st.text_input("Make")
        with c2: data["Data"]["Model"] = st.text_input("Model")

    elif entity_type == "Phone":
        data["Data"]["Number"] = st.text_input("Phone Number")
        data["Data"]["IMEI"] = st.text_input("IMEI (optional)")

    elif entity_type == "Bank Account":
        data["Data"]["Bank"] = st.text_input("Bank")
        c1,c2 = st.columns(2)
        with c1: data["Data"]["BSB"] = st.text_input("BSB")
        with c2: data["Data"]["Account"] = st.text_input("Account No.")

    elif entity_type == "Location":
        data["Data"]["Address"] = st.text_input("Address")
        c1,c2 = st.columns(2)
        with c1: data["Data"]["Suburb"] = st.text_input("Suburb")
        with c2: data["Data"]["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])

    # Generate label
    if st.button("Add to Library", type="primary"):
        labels = {
            "Person": f"{data['Data'].get('First','')} {data['Data'].get('Last','')}".strip() or "Unknown Person",
            "Organisation": data["Data"].get("Name", "Unknown Org"),
            "Vehicle": data["Data"].get("Rego", "Unknown Vehicle"),
            "Phone": data["Data"].get("Number", "Unknown Phone"),
            "Bank Account": f"{data['Data'].get('BSB','')}-{data['Data'].get('Account','')}",
            "Location": f"{data['Data'].get('Suburb','')} {data['Data'].get('State','')}"
        }
        data["Label"] = labels[entity_type]
        st.session_state.entity_library = pd.concat([st.session_state.entity_library, pd.DataFrame([data])], ignore_index=True)
        st.success(f"Added {ENTITY_STYLES[entity_type]['icon']} {data['Label']}")
        st.rerun()

    # Search & display library with icons
    search = st.text_input("Search Library")
    lib = st.session_state.entity_library
    if search:
        lib = lib[lib.apply(lambda row: search.lower() in str(row.to_dict()).lower(), axis=1)]

    st.write(f"**{len(lib)} entities**")
    for _, row in lib.iterrows():
        icon = ENTITY_STYLES[row["Type"]]["icon"]
        if st.button(f"{icon} {row['Label']}", key=f"lib_{row['ID']}"):
            st.session_state.selected.append(row.to_dict())
            st.success(f"Selected {icon} {row['Label']} → Drop to canvas")

# ======================== MAIN CANVAS ========================
col1, col2 = st.columns([4,1])

with col1:
    st.subheader("Link Analysis Canvas")

    # Drop selected entities
    if st.session_state.selected:
        st.info(f"Ready to drop: {', '.join([f'{ENTITY_STYLES[s['Type']]['icon']} {s['Label']}' for s in st.session_state.selected[:5]])}")
        if st.button("Drop All Selected to Canvas", type="primary"):
            for ent in st.session_state.selected:
                if ent not in st.session_state.graph_entities:
                    st.session_state.graph_entities.append(ent)
            st.session_state.selected = []
            st.rerun()

    # Build network
    net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True, notebook=True)
    net.force_atlas_2based()

    # Add nodes with proper icons
    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        style = ENTITY_STYLES[ent["Type"]]
        photo = ent.get("PhotoURL", "").strip()
        title = f"<b>{label}</b><br>{ent['Type']}<br>" + "<br>".join([f"{k}: {v}" for k,v in ent["Data"].items() if v])

        if photo:
            net.add_node(label, shape="circularImage", image=photo, title=title)
        else:
            net.add_node(label, title=title, color=style["color"], size=30)

    # Add links
    for link in st.session_state.graph_links:
        net.add_edge(link["source"], link["target"], label=link.get("type", "Link"), color="#95a5a6", arrows="to")

    # Generate HTML safely
    html = net.generate_html()
    components.html(html, height=800, scrolling=True)

    # Link creator
    if len(st.session_state.graph_entities) >= 2:
        st.markdown("### Create Link Between Entities")
        nodes = [e["Label"] for e in st.session_state.graph_entities]
        src = st.selectbox("From", nodes, key="link_from")
        tgt = st.selectbox("To", nodes, key="link_to")
        link_type = st.text_input("Link Type", "Calls / Owns / Transfers / Meets")
        if st.button("Create Link", type="primary"):
            st.session_state.graph_links.append({"source": src, "target": tgt, "type": link_type})
            st.success(f"Linked {src} → {tgt}")
            st.rerun()

with col2:
    st.subheader("On Canvas")
    st.write(f"**{len(st.session_state.graph_entities)} entities**")
    for ent in st.session_state.graph_entities:
        icon = ENTITY_STYLES[ent["Type"]]["icon"]
        if st.button(f"{icon} {ent['Label']}", key=f"rem_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["ID"] != ent["ID"]]
            st.rerun()

# Export
with st.expander("Export Canvas"):
    if st.session_state.graph_entities:
        df_e = pd.DataFrame([{"Label": e["Label"], "Type": e["Type"], **e["Data"]} for e in st.session_state.graph_entities])
        st.download_button("Download Entities CSV", df_e.to_csv(index=False), "entities.csv")
    if st.session_state.graph_links:
        df_l = pd.DataFrame(st.session_state.graph_links)
        st.download_button("Download Links CSV", df_l.to_csv(index=False), "links.csv")
