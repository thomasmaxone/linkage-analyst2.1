import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

st.sidebar.success("AnalystForge Pro – AU Police Standard")
st.sidebar.caption("Real icons on canvas • Nov 2025")

st.title("AnalystForge Pro – Full i2 Analyst’s Notebook Replacement")
st.caption("Real entity symbols on canvas • Drag & drop • Full linking")

# Proper icons for each entity type (exactly like i2)
ICON_URLS = {
    "Person":       "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/person.png",
    "Organisation": "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/building.png",
    "Vehicle":      "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/car.png",
    "Phone":        "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/phone.png",
    "Bank Account": "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/bank.png",
    "Location":     "https://raw.githubusercontent.com/coleam00/analystforge/main/icons/pin.png"
}

# Initialise
if "entity_library" not in st.session_state:
    st.session_state.entity_library = pd.DataFrame(columns=["ID","Type","Label","Data","PhotoURL"])
if "graph_entities" not in st.session_state:
    st.session_state.graph_entities = []
if "graph_links" not in st.session_state:
    st.session_state.graph_links = []
if "selected" not in st.session_state:
    st.session_state.selected = []

# ======================== LIBRARY ========================
with st.sidebar.expander("Entity Library", expanded=True):
    st.subheader("Add New Entity")
    entity_type = st.selectbox("Type", list(ICON_URLS.keys()))

    data_dict = {}
    photo_url = ""

    if entity_type == "Person":
        c1,c2 = st.columns(2)
        with c1: data_dict["First"] = st.text_input("First Name", key="p1")
        with c2: data_dict["Last"] = st.text_input("Last Name", key="p2")
        data_dict["DOB"] = st.date_input("DOB", value=None, key="p3")
        data_dict["Phone"] = st.text_input("Phone", key="p4")
        photo_url = st.text_input("Photo URL (optional)", key="p5")

    elif entity_type == "Organisation":
        data_dict["Name"] = st.text_input("Organisation Name", key="o1")
        data_dict["ABN"] = st.text_input("ABN", key="o2")

    elif entity_type == "Vehicle":
        data_dict["Rego"] = st.text_input("Registration", key="v1")
        c1,c2 = st.columns(2)
        with c1: data_dict["Make"] = st.text_input("Make", key="v2")
        with c2: data_dict["Model"] = st.text_input("Model", key="v3")

    elif entity_type == "Phone":
        data_dict["Number"] = st.text_input("Phone Number", key="ph1")
        data_dict["IMEI"] = st.text_input("IMEI", key="ph2")

    elif entity_type == "Bank Account":
        data_dict["Bank"] = st.text_input("Bank", key="b1")
        c1,c2 = st.columns(2)
        with c1: data_dict["BSB"] = st.text_input("BSB", key="b2")
        with c2: data_dict["Account"] = st.text_input("Account No.", key="b3")

    elif entity_type == "Location":
        data_dict["Address"] = st.text_input("Address", key="l1")
        c1,c2 = st.columns(2)
        with c1: data_dict["Suburb"] = st.text_input("Suburb", key="l2")
        with c2: data_dict["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"], key="l3")

    if st.button("Add to Library", type="primary"):
        labels = {
            "Person": f"{data_dict.get('First','')} {data_dict.get('Last','')}".strip() or "Unknown Person",
            "Organisation": data_dict.get("Name", "Unknown Org"),
            "Vehicle": data_dict.get("Rego", "Unknown Vehicle"),
            "Phone": data_dict.get("Number", "Unknown Phone"),
            "Bank Account": f"{data_dict.get('BSB','')}-{data_dict.get('Account','')}",
            "Location": f"{data_dict.get('Suburb','')} {data_dict.get('State','')}"
        }
        new_entity = {
            "ID": str(uuid.uuid4())[:8],
            "Type": entity_type,
            "Label": labels[entity_type],
            "Data": data_dict,
            "PhotoURL": photo_url or ICON_URLS[entity_type]  # fallback to icon
        }
        st.session_state.entity_library = pd.concat([st.session_state.entity_library, pd.DataFrame([new_entity])], ignore_index=True)
        st.success(f"Added {new_entity['Label']}")
        st.rerun()

    # Search & display
    search = st.text_input("Search Library", key="search")
    lib = st.session_state.entity_library
    if search:
        lib = lib[lib.apply(lambda row: search.lower() in str(row.to_dict()).lower(), axis=1)]

    st.write(f"**{len(lib)} entities**")
    for _, row in lib.iterrows():
        if st.button(f"{row['Type']} {row['Label']}", key=f"lib_{row['ID']}"):
            st.session_state.selected.append(row.to_dict())
            st.success(f"Selected {row['Label']}")

# ======================== CANVAS ========================
c1, c2 = st.columns([4,1])

with c1:
    st.subheader("Link Analysis Canvas")

    if st.session_state.selected:
        preview = ", ".join([e["Label"] for e in st.session_state.selected[:6]])
        st.info(f"Ready to drop: {preview}")
        if st.button("Drop All → Canvas", type="primary"):
            for ent in st.session_state.selected:
                if ent not in st.session_state.graph_entities:
                    st.session_state.graph_entities.append(ent)
            st.session_state.selected = []
            st.rerun()

    # Build network with REAL ICONS on canvas
    net = Network(height="800px", bgcolor="#0e1117", font_color="#ffffff", directed=True, notebook=True)
    net.force_atlas_2based()

    for ent in st.session_state.graph_entities:
        label = ent["Label"]
        icon_url = ICON_URLS[ent["Type"]]

        # Tooltip
        details = []
        for k, v in ent["Data"].items():
            if v in [None, "", date(1,1,1)]: continue
            if isinstance(v, date): v = v.strftime("%Y-%m-%d")
            details.append(f"{k}: {v}")
        tooltip = f"<b>{label}</b><br>{ent['Type']}<br>" + "<br>".join(details)

        # Use icon as node image
        net.add_node(
            label,
            shape="image",
            image=icon_url,
            title=tooltip,
            size=40,
            labelHighlightBold=True
        )

    # Links
    for link in st.session_state.graph_links:
        net.add_edge(link["source"], link["target"], label=link.get("type", ""), color="#bdc3c7", arrows="to", width=3)

    # Render
    components.html(net.generate_html(), height=800, scrolling=True)

    # Link creator
    if len(st.session_state.graph_entities) >= 2:
        st.markdown("### Create Link")
        nodes = [e["Label"] for e in st.session_state.graph_entities]
        src = st.selectbox("From", nodes, key="from")
        tgt = st.selectbox("To", nodes, key="to")
        link_type = st.text_input("Link Type", "Calls / Owns / Lives At", key="lt")
        if st.button("Create Link", type="primary"):
            st.session_state.graph_links.append({"source": src, "target": tgt, "type": link_type})
            st.success("Link created")
            st.rerun()

with c2:
    st.subheader("On Canvas")
    for ent in st.session_state.graph_entities:
        if st.button(f"Remove {ent['Label']}", key=f"rem_{ent['ID']}"):
            st.session_state.graph_entities = [e for e in st.session_state.graph_entities if e["ID"] != ent["ID"]]
            st.rerun()

# Export
with st.expander("Export"):
    if st.session_state.graph_entities:
        export = [{"Label": e["Label"], "Type": e["Type"], **e["Data"]} for e in st.session_state.graph_entities]
        df = pd.DataFrame(export)
        st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")
    if st.session_state.graph_links:
        df_l = pd.DataFrame(st.session_state.graph_links)
        st.download_button("Download Links CSV", df_l.to_csv(index=False), "links.csv")
