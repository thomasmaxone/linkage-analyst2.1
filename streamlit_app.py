import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# ULTRA-MODERN 2025 GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    .main {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    .css-1d391kg {background: transparent !important;}
    .glass-card {
        background: rgba(255, 255, 255, 0.09);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white; border: none; border-radius: 12px;
        padding: 0.8rem 2rem; font-weight: 600;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5);
        transition: all 0.3s;
    }
    .stButton > button:hover {transform: translateY(-3px); box-shadow: 0 10px 30px rgba(59, 130, 246, 0.7);}
    h1 {background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 700;}
    .stSelectbox > div > div {background: rgba(255,255,255,0.1); border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.caption("Next-Gen Link Analysis • Australian Law Enforcement Standard 2025–2026")

ICONS = {
    "Person":       "https://raw.githubusercontent.com/twbs/icons/main/icons/person-fill.svg",
    "Organisation": "https://raw.githubusercontent.com/twbs/icons/main/icons/building-fill.svg",
    "Vehicle":      "https://raw.githubusercontent.com/twbs/icons/main/icons/truck.svg",
    "Phone":        "https://raw.githubusercontent.com/twbs/icons/main/icons/phone-fill.svg",
    "Bank Account": "https://raw.githubusercontent.com/twbs/icons/main/icons/piggy-bank-fill.svg",
    "Location":     "https://raw.githubusercontent.com/twbs/icons/main/icons/house-fill.svg"
}

for key in ["library", "canvas", "links"]:
    if key not in st.session_state:
        st.session_state[key] = []

# SIDEBAR — DYNAMIC FORM (only shows relevant fields)
with st.sidebar:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")

    with st.form("entity_form", clear_on_submit=True):
        entity_type = st.selectbox("Entity Type", list(ICONS.keys()), key="type_select")

        data = {}

        # DYNAMIC FIELDS — only what’s needed
        if entity_type == "Person":
            st.markdown("**Personal Details**")
            c1, c2 = st.columns(2)
            with c1: data["First Name"] = st.text_input("First Name", placeholder="John")
            with c2: data["Last Name"] = st.text_input("Last Name", placeholder="Smith")
            data["DOB"] = st.date_input("Date of Birth", value=None)
            data["Phone"] = st.text_input("Mobile/Phone")
            data["Email"] = st.text_input("Email (optional)")

        elif entity_type == "Organisation":
            st.markdown("**Organisation Details**")
            data["Name"] = st.text_input("Full Name", placeholder="ACME Pty Ltd")
            data["ABN"] = st.text_input("ABN / ACN", placeholder="12 345 678 901")

        elif entity_type == "Vehicle":
            st.markdown("**Vehicle Details**")
            data["Registration"] = st.text_input("Registration Plate*", placeholder="ABC-123")
            c1, c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make", placeholder="Toyota")
            with c2: data["Model"] = st.text_input("Model", placeholder="Camry")
            data["Year"] = st.text_input("Year (optional)", max_chars=4)

        elif entity_type == "Phone":
            st.markdown("**Phone Details**")
            data["Number"] = st.text_input("Phone Number*", placeholder="0412 345 678")
            data["IMEI"] = st.text_input("IMEI (optional)")
            data["Provider"] = st.text_input("Provider (optional)")

        elif entity_type == "Bank Account":
            st.markdown("**Bank Account Details**")
            data["Bank"] = st.text_input("Bank Name", placeholder="Commonwealth Bank")
            c1, c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB*", placeholder="062-000")
            with c2: data["Account Number"] = st.text_input("Account Number*", placeholder="12345678")
            data["Account Name"] = st.text_input("Account Holder")

        elif entity_type == "Location":
            st.markdown("**Location Details**")
            data["Name/Description"] = st.text_input("Name (e.g. Home, Safe House)", placeholder="Primary Residence")
            data["Street Address"] = st.text_input("Street Address")
            c1, c2 = st.columns(2)
            with c1: data["Suburb"] = st.text_input("Suburb")
            with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])
            data["Postcode"] = st.text_input("Postcode", max_chars=4)

        # SAVE BUTTON
        saved = st.form_submit_button("Save Entity to Project", type="primary")

        if saved:
            # Generate smart label
            label_map = {
                "Person": f"{data.get('First Name','')} {data.get('Last Name','')}".strip() or "Person",
                "Organisation": data.get("Name", "Organisation"),
                "Vehicle": data.get("Registration", "Vehicle"),
                "Phone": data.get("Number", "Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account Number','')}",
                "Location": data.get("Name/Description", "Location") or data.get("Street Address", "Location")
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

    # Library list
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    search = st.text_input("Search entities...", key="libsearch")
    filtered = [e for e in st.session_state.library 
                if not search or search.lower() in e["label"].lower() or search.lower() in str(e["data"]).lower()]

    for e in filtered:
        if st.button(f"{e['type']} {e['label']}", key=f"add_{e['id']}"):
            if e not in st.session_state.canvas:
                st.session_state.canvas.append(e)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# MAIN CANVAS (clean white)
c1, c2 = st.columns([4, 1])

with c1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="880px", bgcolor="#ffffff", font_color="#1f2937", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"forceAtlas2Based": {"gravitationalConstant": -80}},
      "nodes": {"font": {"size": 18}},
      "edges": {"color": "#3b82f6", "width": 4, "arrows": "to", "smooth": true}
    }
    """)

    for ent in st.session_state.canvas:
        lines = [f"<b style='font-size:20px'>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone"): lines.append(ent["data"]["Phone"])
        if ent["type"] == "Vehicle" and ent["data"].get("Registration"): lines.append(ent["data"]["Registration"])
        if ent["type"] == "Bank Account": lines.append(f"{ent['data'].get('BSB','')}-{ent['data'].get('Account Number','')}")
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b> ({ent['type']})"] +
                             [f"{k}: {v if not isinstance(v,date) else v.strftime('%d/%m/%Y')}"
                              for k,v in ent["data"].items() if v and v != date(1,1,1)])

        net.add_node(ent["id"], label=label_html, shape="image", image=ent["icon"],
                     title=tooltip, size=60, font={"multi": "html"})

    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"], font={"size": 16})

    components.html(net.generate_html(), height=880, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Create Link")
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        f = st.selectbox("From", options=list(labels.keys()), format_func=lambda x: labels[x], key="from_link")
        t = st.selectbox("To", options=list(labels.keys()), format_func=lambda x: labels[x], key="to_link")
        typ = st.text_input("Link Type", "Owns • Calls • Controls • Lives At", key="link_type")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": f, "to": t, "type": typ})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"rem_{ent['id']}"):
            st.session_state.canvas = [e for e in st.session_state.canvas if e["id"] != ent["id"]]
            st.session_state.links = [l for l in st.session_state.links if l["from"] != ent["id"] and l["to"] != ent["id"]]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Export
with st.expander("Export Project"):
    if st.session_state.canvas:
        df = pd.DataFrame([{"Label": e["label"], "Type": e["type"], **e["data"]} for e in st.session_state.canvas])
        st.download_button("Download Entities CSV", df.to_csv(index=False), "entities.csv")
    if st.session_state.links:
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        links_df = pd.DataFrame([{"From": labels.get(l["from"]), "To": labels.get(l["to"]), "Type": l["type"]} for l in st.session_state.links])
        st.download_button("Download Links CSV", links_df.to_csv(index=False), "links.csv")
