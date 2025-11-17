import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="🔍")

st.sidebar.success("AnalystForge Pro – AU Police Standard 2025")
st.sidebar.caption("Fixed IDs • Physical icons • Label + data under icon")

st.title("AnalystForge Pro – Full i2 Analyst's Notebook Replacement")
st.caption("Real physical symbols • Drag & drop • Bulletproof linking")

# Physical icons (high-quality PNGs – fast & reliable)
ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/car-front.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/building.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house.svg"
}

# Initialise
if "library" not in st.session_state:
    st.session_state.library = []
if "canvas" not in st.session_state:
    st.session_state.canvas = []
if "links" not in st.session_state:
    st.session_state.links = []
if "selected" not in st.session_state:
    st.session_state.selected = []

# ======================== ADD ENTITY ========================
with st.sidebar.expander("Add Entity to Library", expanded=True):
    type_ = st.selectbox("Entity Type", list(ICONS.keys()))
    data = {}

    if type_ == "Person":
        c1,c2 = st.columns(2)
        with c1: data["First Name"] = st.text_input("First Name", key="f1")
        with c2: data["Last Name"] = st.text_input("Last Name", key="l1")
        data["DOB"] = st.date_input("DOB", value=None, key="dob1")
        data["Phone"] = st.text_input("Phone", key="ph1")

    elif type_ == "Organisation":
        data["Name"] = st.text_input("Organisation Name", key="org1")
        data["ABN"] = st.text_input("ABN", key="abn1")

    elif type_ == "Vehicle":
        data["Rego"] = st.text_input("Registration", key="rego1")
        c1,c2 = st.columns(2)
        with c1: data["Make"] = st.text_input("Make", key="mk1")
        with c2: data["Model"] = st.text_input("Model", key="md1")

    elif type_ == "Phone":
        data["Number"] = st.text_input("Phone Number", key="num1")
        data["IMEI"] = st.text_input("IMEI", key="imei1")

    elif type_ == "Bank Account":
        data["Bank"] = st.text_input("Bank Name", key="bnk1")
        c1,c2 = st.columns(2)
        with c1: data["BSB"] = st.text_input("BSB", key="bsb1")
        with c2: data["Account"] = st.text_input("Account No.", key="acc1")

    elif type_ == "Location":
        data["Address"] = st.text_input("Street Address", key="addr1")
        c1,c2 = st.columns(2)
        with c1: data["Suburb"] = st.text_input("Suburb", key="sub1")
        with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"], key="st1")

    if st.button("Add to Library", type="primary"):
        label = {
            "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip() or "Unknown Person",
            "Organisation": data.get("Name", "Unknown Org"),
            "Vehicle": data.get("Rego", "Unknown Vehicle"),
            "Phone": data.get("Number", "Unknown Phone"),
            "Bank Account": f"{data.get('BSB','')}-{data.get('Account','')}",
            "Location": data.get("Address", "Unknown Location")
        }[type_]

        entity = {
            "id": str(uuid.uuid4())[:8],
            "type": type_,
            "label": label,
            "data": data,
            "icon": ICONS[type_]
        }
        st.session_state.library.append(entity)
        st.success(f"Added {label}")
        st.rerun()

    # Search & select
    search = st.text_input("Search Library")
    filtered = [e for e in st.session_state.library if search.lower() in str(e).lower()] if search else st.session_state.library

    for ent in filtered:
        if st.button(f"{ent['type']} {ent['label']}", key=f"lib_{ent['id']}"):
            st.session_state.selected.append(ent)
            st.success(f"Selected → {ent['label']}")

# ======================== CANVAS ========================
c1, c2 = st.columns([4,1])

with c1:
    st.subheader("Link Analysis Canvas")

    if st.session_state.selected:
        preview = ", ".join([e["label"][:20] for e in st.session_state.selected[:5]])
        st.info(f"Ready to drop: {preview}")
        if st.button("Drop All to Canvas", type="primary"):
            for e in st.session_state.selected:
                if e not in st.session_state.canvas:
                    st.session_state.canvas.append(e)
            st.session_state.selected = []
            st.rerun()

    # Build network with PHYSICAL ICONS + LABEL BELOW (FIXED IDs)
    net = Network(height="850px", bgcolor="#1a1a1a", font_color="#ffffff", directed=True, notebook=True)
    net.force_atlas_2based()

    # Add nodes first (using UUID IDs)
    for ent in st.session_state.canvas:
        # Main info under icon
        lines = [ent["label"]]
        if ent["type"] == "Person" and ent["data"].get("Phone"):
            lines.append(ent["data"]["Phone"])
        elif ent["type"] == "Vehicle" and ent["data"].get("Rego"):
            lines.append(ent["data"]["Rego"])
        elif ent["type"] == "Bank Account":
            lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account','')}")
        label_below = "<br>".join(lines)

        # Tooltip with all data
        tooltip_lines = [f"<b>{ent['label']}</b>", ent["type"]]
        for k, v in ent["data"].items():
            if v and v != date(1,1,1):
                if isinstance(v, date): v = v.strftime("%d/%m/%Y")
                tooltip_lines.append(f"{k}: {v}")
        tooltip = "<br>".join(tooltip_lines)

        net.add_node(
            ent["id"],  # Use UUID ID
            label=label_below,
            shape="image",
            image=ent["icon"],
            title=tooltip,
            size=50,
            font={"size": 14, "color": "#ffffff", "face": "arial"},
            scaling={"label": True}
        )

    # Add links (FIXED: Use UUID IDs for source/target)
    for link in st.session_state.links:
        # Ensure nodes exist (safety check)
        if link["from"] in [e["id"] for e in st.session_state.canvas] and link["to"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"], color="#3498db", width=3, arrows="to")

    components.html(net.generate_html(), height=850, scrolling=True)

    # Link creator (FIXED: Use UUID IDs)
    if len(st.session_state.canvas) >= 2:
        st.markdown("### Create Link")
        canvas_labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        from_id = st.selectbox("From", list(canvas_labels.keys()), format_func=lambda x: canvas_labels[x], key="f")
        to_id = st.selectbox("To", list(canvas_labels.keys()), format_func=lambda x: canvas_labels[x], key="t")
        link_type = st.text_input("Link Type", "Owns / Calls / Lives At / Works At", key="lt")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": from_id, "to": to_id, "type": link_type})
            st.success("Link created")
            st.rerun()

with c2:
    st.subheader("On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"rem_{ent['id']}"):
            st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != ent["id"]]
            # Clean up links
            st.session_state.links = [l for l in st.session_state.links if l["from"] != ent["id"] and l["to"] != ent["id"]]
            st.rerun()

# Export
with st.expander("Export Canvas"):
    if st.session_state.canvas:
        export = []
        for e in st.session_state.canvas:
            row = {"Label": e["label"], "Type": e["type"]}
            row.update(e["data"])
            export.append(row)
        df = pd.DataFrame(export)
        st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")
    if st.session_state.links:
        links_export = [{"From": canvas_labels.get(l["from"], l["from"]), "To": canvas_labels.get(l["to"], l["to"]), "Type": l["type"]} for l in st.session_state.links]
        df_l = pd.DataFrame(links_export)
        st.download_button("Download Links CSV", df_l.to_csv(index=False), "links.csv")
