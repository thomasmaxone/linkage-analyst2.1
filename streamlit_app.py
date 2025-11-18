import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import uuid
from datetime import date

st.set_page_config(page_title="AnalystForge Pro", layout="wide", page_icon="Detective")

# ——— ULTRA-MODERN 2025 GLASS-MORPHISM THEME ———
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Inter', sans-serif;}
    
    .main {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    
    .css-1d391kg, .css-1v0mbdj {background: transparent !important;}
    
    /* Glass cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    }
    
    /* Glowing primary button */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.6);
    }
    
    /* Sidebar glow */
    .css-1lcbmhc {background: rgba(15, 23, 42, 0.95) !important; backdrop-filter: blur(10px);}
    
    h1 {background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .stSelectbox, .stTextInput > div > div > input {border-radius: 12px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>AnalystForge Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:1.1rem; margin-top:-10px;'>Next-Gen Link Analysis • Australian Law Enforcement 2025</p>", unsafe_allow_html=True)

# Icons
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

# ——— SIDEBAR: MODERN ENTITY ENTRY ———
with st.sidebar:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Add New Entity")
    
    with st.form("entity_form", clear_on_submit=True):
        entity_type = st.selectbox("Type", list(ICONS.keys()), key="type")
        data = {}

        if entity_type == "Person":
            c1,c2 = st.columns(2)
            with c1: data["First"] = st.text_input("First Name")
            with c2: data["Last"] = st.text_input("Last Name")
            data["DOB"] = st.date_input("DOB", value=None)
            data["Phone"] = st.text_input("Phone")

        elif entity_type == "Organisation":
            data["Name"] = st.text_input("Organisation Name")
            data["ABN"] = st.text_input("ABN / ACN")

        elif entity_type == "Vehicle":
            data["Rego"] = st.text_input("Registration")
            c1,c2 = st.columns(2)
            with c1: data["Make"] = st.text_input("Make")
            with c2: data["Model"] = st.text_input("Model")

        elif entity_type == "Phone":
            data["Number"] = st.text_input("Phone Number")
            data["IMEI"] = st.text_input("IMEI (optional)")

        elif entity_type == "Bank Account":
            data["Bank"] = st.text_input("Bank")
            c1,c2 = st.columns(2)
            with c1: data["BSB"] = st.text_input("BSB")
            with c2: data["Account"] = st.text_input("Account No.")

        elif entity_type == "Location":
            data["Address"] = st.text_input("Address")
            c1,c2 = st.columns(2)
            with c1: data["Suburb"] = st.text_input("Suburb")
            with c2: data["State"] = st.selectbox("State", ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"])

        saved = st.form_submit_button("Save Entity to Project", type="primary")
        
        if saved:
            label = {
                "Person": f"{data.get('First','')} {data.get('Last','')}".strip() or "Person",
                "Organisation": data.get("Name","Org"),
                "Vehicle": data.get("Rego","Vehicle"),
                "Phone": data.get("Number","Phone"),
                "Bank Account": f"{data.get('BSB','')}-{data.get('Account','')}",
                "Location": data.get("Address","Location")
            }[entity_type]

            entity = {
                "id": str(uuid.uuid4())[:8],
                "type": entity_type,
                "label": label,
                "data": data,
                "icon": ICONS[entity_type]
            }
            st.session_state.library.append(entity)
            st.success(f"Saved {label}")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Library list
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Entity Library")
    search = st.text_input("Search", key="search")
    filtered = [e for e in st.session_state.library if not search or search.lower() in e["label"].lower()]
    
    for e in filtered:
        if st.button(f"{e['type']} {e['label']}", key=f"add_{e['id']}"):
            if e not in st.session_state.canvas:
                st.session_state.canvas.append(e)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ——— MAIN CANVAS (WHITE + MODERN) ———
col1, col2 = st.columns([4,1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Link Analysis Canvas")

    net = Network(height="860px", bgcolor="#ffffff", font_color="#1f2937", directed=True, notebook=True)
    net.set_options("""
    var options = {
      "physics": {"forceAtlas2Based": {"gravitationalConstant": -50}},
      "nodes": {"font": {"size": 16, "face": "Inter"}},
      "edges": {"color": "#3b82f6", "width": 4, "arrows": "to", "smooth": true}
    }
    """)

    for ent in st.session_state.canvas:
        lines = [f"<b style='font-size:18px'>{ent['label']}</b>"]
        if ent["type"] == "Person" and ent["data"].get("Phone"): lines.append(ent["data"]["Phone"])
        if ent["type"] == "Vehicle" and ent["data"].get("Rego"): lines.append(ent["data"]["Rego"])
        label_html = "<br>".join(lines)

        tooltip = "<br>".join([f"<b>{ent['label']}</b>", ent["type"]] + 
                             [f"{k}: {v}" for k,v in ent["data"].items() if v and v != date(1,1,1)])

        net.add_node(ent["id"], label=label_html, shape="image", image=ent["icon"],
                     title=tooltip, size=55, font={"multi": "html"})

    for link in st.session_state.links:
        if link["from"] in [e["id"] for e in st.session_state.canvas]:
            net.add_edge(link["from"], link["to"], label=link["type"], font={"size": 14})

    components.html(net.generate_html(), height=860, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Link creator
    if len(st.session_state.canvas) >= 2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Create Link")
        labels = {e["id"]: e["label"] for e in st.session_state.canvas}
        f = st.selectbox("From", options=list(labels.keys()), format_func=lambda x: labels[x])
        t = st.selectbox("To", options=list(labels.keys()), format_func=lambda x: labels[x])
        typ = st.text_input("Link Type", "Owns • Calls • Controls")
        if st.button("Add Link", type="primary"):
            st.session_state.links.append({"from": f, "to": t, "type": typ})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### On Canvas")
    for ent in st.session_state.canvas:
        if st.button(f"Remove {ent['label']}", key=f"rm_{ent['id']}"):
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
