import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# ——— CLEAN, MODERN GLASS THEME ———
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
st.caption("Australian Law Enforcement Link Analysis • 2025 Standard")

# ——— ICONS ———
ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"
}

# ——— INITIALISE ———
for key in ["library", "canvas", "links"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ——— SIDEBAR: DYNAMIC ENTITY FORM ———
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")

    # Use a simple counter to force form refresh
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0

    entity_type = st.selectbox(
        "Entity Type",
        options=list(ICONS.keys()),
        key=f"etype_{st.session_state.form_counter}"
    )

    with st.form(key=f"entity_form_{st.session_state.form_counter}", clear_on_submit=True):
        data = {}

        if entity_type == "Person":
            st.subheader("Person Details")
            c1, c2 = st.columns(2)
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
            c1, c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")
            data["Colour"] = st.text_input("Colour (optional)")

        elif entity_type == "Phone":
            st.subheader("Phone Details")
            data["Phone Number"] = st.text_input("Phone Number")
            data["IMEI"] = st.text_input("IMEI (optional)")

        elif entity_type == "Bank Account":
            st.subheader("Bank Account Details")
            data["Bank"] = st.text_input("Bank Name")
            c1, c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account Number"] = st.text_input("Account Number")
            data["Holder Name"] = st.text_input("Account Holder")

        elif entity_type == "Location":
            st.subheader("Location Details")
            data["Location Name"] = st.text_input("Name (e.g. Safe House)")
            data["Address"] = st.text_input("Full Address")

        if st.form_submit_button("Save Entity to Project", type="primary"):
            # Generate label
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
            st.session_state.form_counter += 1  # This forces full form refresh
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ——— ENTITY LIBRARY ———
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    for entity in st.session_state.library:
        if st.button(f"{entity['type']} {entity['label']}", key=f"lib_{entity['id']}"):
            if entity not in st.session_state.canvas:
                st.session_state.canvas.append(entity)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ——— MAIN CANVAS (WHITE) ———
c1, c2 = st.columns([4, 1])

with c1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="880px", bgcolor="#ffffff", font_color="#111827", directed=True, notebook=True)
    net.force_atlas_2based()

    # Add nodes
    for ent in st.session_state.canvas:
        label_html = f"<b>{ent['label']}</b>"
        if ent["type"] == "Person" and ent["data"].get("Phone Number"):
            label_html += f"<br>{ent['data']['Phone Number']}"
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"):
            label_html += f"<br>{ent['data']['Registration']}"

        tooltip = "<br>".join([f"<b>{ent['label']}</b>"] + 
                            [f"{k}: {v}" for k, v in ent["data"].items() if v])

        net.add_node(
            ent["id"],
            label=label_html,
            shape="image",
            image=ent["icon"],
            title=tooltip,
            size=60,
            font={"multi": "html", "size": 18}
        )

    # Add links
    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"], color="#3b82f6", width=4, arrows="to")

    components.html(net.generate_html(), height=880, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ——— LINK CREATOR ———
    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Create Link")
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        f_id = st.selectbox("From", options=list(labels.keys()), format_func=lambda x: labels[x])
        t_id = st.selectbox("To", options=list(labels.keys()), format_func=lambda x: labels[x])
        link_type = st.text_input("Link Type", "Owns • Calls • Lives At • Works At")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": f_id, "to": t_id, "type": link_type})
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

# ——— EXPORT ———
with st.expander("Export Project"):
    if st.session_state.canvas:
        export_df = pd.DataFrame([{"Label": e["label"], "Type": e["type"], **e["data"]} for e in st.session_state.canvas])
        st.download_button("Download Entities CSV", export_df.to_csv(index=False), "entities.csv")
    if st.session_state.links:
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        links_df = pd.DataFrame([{"From": labels.get(l["from"]), "To": labels.get(l["to"]), "Type": l["type"]} for l in st.session_state.links])
        st.download_button("Download Links CSV", links_df.to_csv(index=False), "links.csv")
