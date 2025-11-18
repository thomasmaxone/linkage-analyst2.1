import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Police Car Light")

# BEAUTIFUL 2025 GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    .main {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    .glass-card {
        background: rgba(255, 255, 255, 0.09);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 1.8rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 1.2rem;
    }
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white; border: none; border-radius: 14px;
        padding: 0.9rem 2.2rem; font-weight: 600; font-size: 1.1rem;
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5);
        transition: all 0.3s;
    }
    .stButton > button:hover {transform: translateY(-4px); box-shadow: 0 12px 35px rgba(59, 130, 246, 0.7);}
    h1 {background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.2rem; font-weight: 800;}
    .stTextInput > div > div > input, .stSelectbox > div > div {background: rgba(255,255,255,0.1); border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.caption("Australian Law Enforcement Link Analysis • 2025 Standard")

# OFFICIAL ICONS (used in real police tools)
ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"
}

# Init
for k in ["library", "canvas", "links"]:
    if k not in st.session_state:
        st.session_state[k] = []

# SIDEBAR — CLEAN, RELEVANT FIELDS ONLY
with st.sidebar:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")

    with st.form("add_entity", clear_on_submit=True):
        entity_type = st.selectbox("Select Entity Type", list(ICONS.keys()), key="etype")

        data = {}

        if entity_type == "Person":
            st.markdown("**Name & Identity**")
            c1, c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name*", placeholder="John")
            with c2: data["Last Name"] = st.text_input("Last Name*", placeholder="Smith")
            data["Date of Birth"] = st.date_input("Date of Birth*", value=None)
            st.markdown("**Contact & Address**")
            data["Phone Number"] = st.text_input("Phone Number", placeholder="0412 345 678")
            data["Address"] = st.text_input("Residential Address", placeholder="123 Example St, Sydney NSW 2000")

        elif entity_type == "Organisation":
            st.markdown("**Company Details**")
            data["Company Name"] = st.text_input("Company Name*", placeholder="ACME Holdings Pty Ltd")
            data["ABN/ACN"] = st.text_input("ABN or ACN*", placeholder="12 345 678 901")
            data["Registered Address"] = st.text_input("Registered Address", placeholder="Level 10, 123 Pitt St, Sydney")

        elif entity_type == "Vehicle":
            st.markdown("**Vehicle Registration**")
            data["Registration"] = st.text_input("Registration Plate*", placeholder="ABC-123")
            c1, c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make*", placeholder="Toyota")
            with c2: data["Model"] = st.text_input("Model*", placeholder="Camry")
            data["Colour"] = st.text_input("Colour", placeholder="White")

        elif entity_type == "Phone":
            st.markdown("**Telephone Details**")
            data["Phone Number"] = st.text_input("Phone Number*", placeholder="0412 345 678")
            data["IMEI"] = st.text_input("IMEI", placeholder="356789123456789")
            data["Provider"] = st.text_input("Telco Provider", placeholder="Telstra")

        elif entity_type == "Bank Account":
            st.markdown("**Bank Account Details**")
            data["Bank Name"] = st.text_input("Bank*", placeholder="Commonwealth Bank")
            c1, c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB*", placeholder="062-000")
            with c2: data["Account Number"] = st.text_input("Account Number*", placeholder="98765432")
            data["Account Holder"] = st.text_input("Account Holder Name*", placeholder="John Smith")

        elif entity_type == "Location":
            st.markdown("**Location Details**")
            data["Location Name"] = st.text_input("Name/Description", placeholder="Safe House Alpha")
            data["Street Address"] = st.text_input("Street Address*", placeholder="45 Hidden Lane")
            c1, c2 = st.columns(2)
            with c1: data["Suburb"] = st.text_input("Suburb*", placeholder="Parramatta")
            with c2: data["State"] = st.selectbox("State*", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])
            data["Postcode"] = st.text_input("Postcode*", max_chars=4)

        saved = st.form_submit_button("Save Entity to Project", type="primary")

        if saved:
            # Required field check
            required = {
                "Person": ["First Name", "Last Name", "Date of Birth"],
                "Organisation": ["Company Name", "ABN/ACN"],
                "Vehicle": ["Registration", "Make", "Model"],
                "Phone": ["Phone Number"],
                "Bank Account": ["Bank", "BSB", "Account Number", "Account Holder"],
                "Location": ["Street Address", "Suburb", "State"]
            }[entity_type]

            missing = [f for f in required if not data.get(f)]
            if missing:
                st.error(f"Missing required: {', '.join(missing)}")
            else:
                label_map = {
                    "Person": f"{data['First Name']} {data['Last Name']}",
                    "Organisation": data["Company Name"],
                    "Vehicle": data["Registration"],
                    "Phone": data["Phone Number"],
                    "Bank Account": f"{data['BSB']}-{data['Account Number']}",
                    "Location": data.get("Location Name") or data["Street Address"][:30]
                }
                label = label_map[entity_type]

                entity = {
                    "id": str(uuid.uuid4())[:8],
                    "type": entity_type,
                    "label": label,
                    "data": data,
                    "icon": ICONS[entity_type]
                }
                st.session_state.library.append(entity)
                st.success(f"Saved: {label}")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Library
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    search = st.text_input("Search...", key="srch")
    filtered = [e for e in st.session_state.library 
                if not search or search.lower() in e["label"].lower()]

    for e in filtered:
        if st.button(f"{e['type']} {e['label']}", key=f"lib_{e['id']}"):
            if e not in st.session_state.canvas:
                st.session_state.canvas.append(e)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# MAIN CANVAS
c1, c2 = st.columns([4,1])

with c1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="880px", bgcolor="#ffffff", font_color="#111827", directed=True, notebook=True)
    net.set_options('''
    var options = {
      "physics": {"forceAtlas2Based": {"gravitationalConstant": -100}},
      "nodes": {"font": {"size": 18, "face": "Inter"}},
      "edges": {"color": "#3b82f6", "width": 4, "arrows": "to"}
    }
    ''')

    for ent in st.session_state.canvas:
        lines = [f"<b style='font-size:21px'>{ent['label']}</b>"]
        if ent["type"] == "Person":
            if ent["data"].get("Phone Number"): lines.append(ent["data"]["Phone Number"])
        elif ent["type"] == "Vehicle":
            if ent["data"].get("Make"): lines.append(f"{ent['data']['Make']} {ent['data']['Model']}")
        label_html = "<br>".join(lines)

        tooltip_lines = [f"<b>{ent['label']}</b>", ent["type"]]
        for k, v in ent["data"].items():
            if v and v != date(1,1,1):
                if isinstance(v, date): v = v.strftime("%d/%m/%Y")
                _lines.append(f"{k}: {v}")
        tooltip = "<br>".join(_lines)

        net.add_node(ent["id"], label=label_html, shape="image", image=ent["icon"],
                     title=tooltip, size=60, font={"multi": "html"})

    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"])

    components.html(net.generate_html(), height=880, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Create Link")
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        f = st.selectbox("From", options=list(labels.keys()), format_func=lambda x: labels[x], key="lf")
        t = st.selectbox("To", options=list(labels.keys()), format_func=lambda x: labels[x], key="lt")
        typ = st.text_input("Link Type", "Owns • Calls • Controls • Associated", key="ltyp")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": f, "to": t, "type": typ})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"del_{ent['id']}"):
            st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != ent["id"]]
            st.session_state.links = [l for l in st.session_state.links if l["from"] != ent["id"] and l["to"] != ent["id"]]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
