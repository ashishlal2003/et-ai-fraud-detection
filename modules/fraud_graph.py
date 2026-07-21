"""
Module 3 — Fraud Network Visualizer
====================================
Renders an interactive graph of fraud compounds → scammers → mule accounts → victims
using NetworkX + Pyvis. All data is synthetic; no real PII is used.

Tab entry point: render_streamlit_tab(openai_client=None)
"""

from __future__ import annotations

import json
import os
import random
import string
from pathlib import Path
from typing import Optional

import networkx as nx
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Colour palette keyed by node type — matches Streamlit's dark theme (#0e1117)
NODE_COLORS = {
    "compound": "#FF4B4B",   # vivid red
    "scammer":  "#FF8C00",   # dark orange
    "mule":     "#FFD700",   # gold-yellow
    "victim":   "#38BDF8",   # sky blue
}

NODE_SIZES = {
    "compound": 35,
    "scammer":  25,
    "mule":     18,
    "victim":   14,
}

# Path relative to this file's location
_DATA_FILE = Path(__file__).parent.parent / "data" / "fraud_network.json"

# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

_COMPOUND_NAMES = ["Jamtara", "Mewat", "Nuh"]

_SCAMMER_NAMES = [
    "Rahul Sharma", "Vikas Yadav", "Ajay Singh", "Deepak Kumar",
    "Ravi Meena", "Sonu Malik", "Pintu Gupta", "Bablu Chauhan",
    "Aakash Tiwari", "Rohit Nagar",
]

_MULE_NAMES = [
    "Rakesh Verma", "Suresh Prasad", "Dinesh Patel", "Mahesh Joshi",
    "Ganesh Rao", "Naresh Sinha", "Umesh Dubey", "Ramesh Pandey",
    "Sunil Yadav", "Anil Sharma", "Nitin Kumar", "Vipin Mishra",
    "Sanjay Chauhan", "Pankaj Singh", "Manish Tiwari",
    "Ashok Verma", "Santosh Gupta", "Deepak Misra", "Rajesh Nair",
    "Harish Pillai",
]

_VICTIM_NAMES = [
    "Priya Mehta", "Anjali Reddy", "Sunita Devi", "Kavita Sharma",
    "Meena Kumari", "Anita Singh", "Pooja Gupta", "Rekha Patel",
    "Sushma Joshi", "Geeta Rao", "Lata Prasad", "Usha Verma",
    "Manju Chauhan", "Sarla Yadav", "Kamla Devi", "Shanti Singh",
    "Pushpa Dubey", "Asha Pandey", "Bimla Sinha", "Nirmala Tiwari",
    "Ramesh Gupta", "Suresh Kumar", "Mahesh Verma", "Dinesh Sharma",
    "Rajesh Yadav", "Mukesh Singh", "Naresh Patel", "Umesh Joshi",
    "Ganesh Rao", "Harish Mishra", "Vikash Chauhan", "Ashish Pandey",
    "Pradeep Verma", "Vinod Kumar", "Sunil Gupta", "Anil Dubey",
    "Nitin Sharma", "Vipin Singh", "Sanjay Patel", "Pankaj Joshi",
    "Arjun Nair", "Krishnan Pillai", "Venkat Reddy", "Murali Rao",
    "Rajan Kumar", "Balan Nair", "Gopalan Menon", "Shyam Bihari",
    "Ramnath Tripathi", "Kedar Joshi",
]

_STATES = [
    "Uttar Pradesh", "Bihar", "Rajasthan", "Jharkhand", "West Bengal",
    "Maharashtra", "Madhya Pradesh", "Haryana", "Delhi", "Gujarat",
    "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Kerala", "Odisha",
]

_FRAUD_TYPES = [
    "Digital Arrest Scam", "KYC Update Fraud", "Investment Scam",
    "OTP Theft", "UPI Phishing", "Fake Loan App", "SIM Swap",
    "Lottery Fraud", "Job Offer Scam", "Fake Bank Call",
]


def _rand_phone(prefix: str = "+91") -> str:
    """Generate a random Indian mobile number."""
    digits = "".join(random.choices(string.digits, k=10))
    # Start with 6-9 for valid Indian mobile
    digits = random.choice("6789") + digits[1:]
    return f"{prefix}-{digits[:5]}-{digits[5:]}"


def _rand_upi(name: str) -> str:
    slug = name.lower().replace(" ", "")[:8]
    banks = ["okaxis", "oksbi", "okhdfcbank", "okicici", "paytm", "ybl"]
    return f"{slug}@{random.choice(banks)}"


def _rand_amount() -> int:
    """Random loss amount (INR), weighted toward 10k–2L range."""
    return random.choice([
        random.randint(2_000, 10_000),
        random.randint(10_000, 50_000),
        random.randint(50_000, 2_00_000),
        random.randint(2_00_000, 10_00_000),
    ])


def generate_synthetic_data() -> dict:
    """
    Generate synthetic fraud network data inline.

    Returns dict with 'nodes' and 'edges' lists suitable for
    build_networkx_graph().
    """
    random.seed(42)
    nodes: list[dict] = []
    edges: list[dict] = []

    # ---- Fraud compounds ----
    compound_ids = []
    for i, name in enumerate(_COMPOUND_NAMES):
        nid = f"compound_{i}"
        compound_ids.append(nid)
        nodes.append({
            "id": nid,
            "label": name,
            "type": "compound",
            "state": "Jharkhand" if name == "Jamtara" else "Haryana",
            "active_since": f"201{i + 5}",
            "known_frauds": random.randint(200, 800),
        })

    # ---- Scammers (10) ----
    scammer_ids = []
    for i, name in enumerate(_SCAMMER_NAMES):
        nid = f"scammer_{i}"
        scammer_ids.append(nid)
        # scammer_1 has a fixed demo phone matching synthetic_fraud_network.py
        phone = "+91-98765-43210" if i == 1 else _rand_phone()
        compound = compound_ids[i % len(compound_ids)]
        nodes.append({
            "id": nid,
            "label": name,
            "type": "scammer",
            "phone": phone,
            "upi": _rand_upi(name),
            "state": random.choice(_STATES[:5]),
            "fraud_type": random.choice(_FRAUD_TYPES),
            "arrests": random.randint(0, 3),
        })
        edges.append({
            "source": compound,
            "target": nid,
            "relation": "operates_from",
            "weight": random.randint(1, 5),
        })

    # ---- Mule accounts (20) ----
    mule_ids = []
    for i, name in enumerate(_MULE_NAMES):
        nid = f"mule_{i}"
        mule_ids.append(nid)
        phone = _rand_phone()
        scammer = scammer_ids[i % len(scammer_ids)]
        nodes.append({
            "id": nid,
            "label": name,
            "type": "mule",
            "phone": phone,
            "upi": _rand_upi(name),
            "bank": random.choice(["SBI", "PNB", "BOI", "Canara", "UCO"]),
            "state": random.choice(_STATES),
            "transactions": random.randint(5, 60),
        })
        edges.append({
            "source": scammer,
            "target": nid,
            "relation": "routes_through",
            "weight": random.randint(1, 3),
        })
        # Some mules connect to 2 scammers
        if i % 4 == 0 and len(scammer_ids) > 1:
            extra = scammer_ids[(i + 2) % len(scammer_ids)]
            if extra != scammer:
                edges.append({
                    "source": extra,
                    "target": nid,
                    "relation": "routes_through",
                    "weight": 1,
                })

    # ---- Victims (50) ----
    for i, name in enumerate(_VICTIM_NAMES[:50]):
        nid = f"victim_{i}"
        phone = _rand_phone()
        mule = mule_ids[i % len(mule_ids)]
        amount = _rand_amount()
        nodes.append({
            "id": nid,
            "label": name,
            "type": "victim",
            "phone": phone,
            "state": random.choice(_STATES),
            "amount_lost": amount,
            "fraud_type": random.choice(_FRAUD_TYPES),
            "reported": random.choice([True, False]),
        })
        edges.append({
            "source": mule,
            "target": nid,
            "relation": "defrauded",
            "amount": amount,
            "weight": 1,
        })

    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_graph_data() -> dict:
    """
    Load fraud network data.

    Tries data/fraud_network.json first; falls back to inline synthetic data.
    """
    if _DATA_FILE.exists():
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return generate_synthetic_data()


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_networkx_graph(data: dict) -> nx.DiGraph:
    """
    Build a directed NetworkX graph from the data dict.

    Nodes carry all metadata as attributes. Edges carry relation + weight.
    """
    G = nx.DiGraph()

    for node in data.get("nodes", []):
        nid = node["id"]
        node_type = node.get("type", "victim")
        G.add_node(
            nid,
            **node,
            color=NODE_COLORS.get(node_type, "#AAAAAA"),
            size=NODE_SIZES.get(node_type, 14),
        )

    for edge in data.get("edges", []):
        G.add_edge(
            edge["source"],
            edge["target"],
            relation=edge.get("relation", ""),
            weight=edge.get("weight", 1),
            amount=edge.get("amount", 0),
        )

    return G


# ---------------------------------------------------------------------------
# Sub-graph extraction
# ---------------------------------------------------------------------------

def get_subgraph(
    graph: nx.DiGraph,
    data: dict,
    phone_number: str,
) -> tuple[nx.DiGraph, dict]:
    """
    Find the node matching phone_number and return its 2-hop ego-graph
    together with aggregate stats.

    Returns:
        (subgraph, stats_dict) where stats_dict has keys:
          total_victims, total_amount_lost, states_affected, connected_scammers
    """
    phone_clean = phone_number.strip().replace(" ", "").replace("-", "")

    # Find matching node
    match_id = None
    for nid, attrs in graph.nodes(data=True):
        stored = str(attrs.get("phone", "")).replace("-", "").replace(" ", "")
        if phone_clean in stored or stored.endswith(phone_clean[-10:]):
            match_id = nid
            break

    if match_id is None:
        return nx.DiGraph(), {
            "total_victims": 0,
            "total_amount_lost": 0,
            "states_affected": 0,
            "connected_scammers": 0,
            "found": False,
            "match_id": None,
        }

    # Build undirected view for neighbor traversal
    undirected = graph.to_undirected()

    # 2-hop neighbourhood
    neighbors_1 = set(undirected.neighbors(match_id))
    neighbors_2: set[str] = set()
    for n in neighbors_1:
        neighbors_2.update(undirected.neighbors(n))

    subgraph_nodes = {match_id} | neighbors_1 | neighbors_2
    sub = graph.subgraph(subgraph_nodes).copy()

    # Compute stats over the subgraph
    victims = [
        attrs for _, attrs in sub.nodes(data=True)
        if attrs.get("type") == "victim"
    ]
    scammers = [
        attrs for _, attrs in sub.nodes(data=True)
        if attrs.get("type") == "scammer"
    ]
    states = {
        attrs.get("state")
        for _, attrs in sub.nodes(data=True)
        if attrs.get("state")
    }

    stats = {
        "found": True,
        "match_id": match_id,
        "match_label": graph.nodes[match_id].get("label", match_id),
        "match_type": graph.nodes[match_id].get("type", "unknown"),
        "total_victims": len(victims),
        "total_amount_lost": sum(v.get("amount_lost", 0) for v in victims),
        "states_affected": len(states),
        "connected_scammers": len(scammers),
    }
    return sub, stats


# ---------------------------------------------------------------------------
# Pyvis rendering
# ---------------------------------------------------------------------------

def render_pyvis_html(
    graph: nx.DiGraph,
    highlight_nodes: Optional[list] = None,
) -> str:
    """
    Render a NetworkX graph as an interactive Pyvis HTML string.

    Node size is proportional to degree. Highlighted nodes get larger
    and a gold border. Returns the full HTML document as a string.

    Raises ImportError if pyvis is not installed.
    """
    from pyvis.network import Network  # type: ignore — deferred import

    highlight_set = set(highlight_nodes or [])

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0e1117",
        font_color="white",
        directed=True,
        notebook=False,
    )
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=120,
        spring_strength=0.04,
        damping=0.09,
    )

    max_degree = max(dict(graph.degree()).values(), default=1)

    for nid, attrs in graph.nodes(data=True):
        degree = graph.degree(nid)
        base_size = attrs.get("size", 14)
        scaled = base_size + int((degree / max(max_degree, 1)) * 20)

        is_highlight = nid in highlight_set
        border_color = "#FFD700" if is_highlight else attrs.get("color", "#AAAAAA")
        border_width = 4 if is_highlight else 1
        node_size = scaled + 10 if is_highlight else scaled

        tooltip_lines = [f"<b>{attrs.get('label', nid)}</b>",
                         f"Type: {attrs.get('type', '—')}"]
        for key in ("phone", "state", "fraud_type", "bank", "amount_lost",
                    "upi", "transactions", "arrests"):
            val = attrs.get(key)
            if val is not None:
                label = key.replace("_", " ").title()
                if key == "amount_lost":
                    tooltip_lines.append(f"{label}: ₹{val:,}")
                else:
                    tooltip_lines.append(f"{label}: {val}")

        net.add_node(
            nid,
            label=attrs.get("label", nid),
            color={
                "background": attrs.get("color", "#AAAAAA"),
                "border": border_color,
                "highlight": {"background": "#FFD700", "border": "#FFF"},
            },
            size=node_size,
            borderWidth=border_width,
            title="<br>".join(tooltip_lines),
            font={"color": "white", "size": 11},
        )

    for src, tgt, edata in graph.edges(data=True):
        relation = edata.get("relation", "")
        edge_colors = {
            "operates_from": "#FF4B4B",
            "routes_through": "#FF8C00",
            "defrauded": "#38BDF8",
        }
        color = edge_colors.get(relation, "#555555")
        amount = edata.get("amount", 0)
        tip = f"{relation.replace('_', ' ').title()}"
        if amount:
            tip += f"<br>₹{amount:,}"

        net.add_edge(
            src, tgt,
            color={"color": color, "opacity": 0.7},
            title=tip,
            width=max(1, edata.get("weight", 1)),
            arrows="to",
        )

    # Inject custom options for cleaner layout
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 120,
          "damping": 0.09
        },
        "stabilization": {"iterations": 200}
      },
      "interaction": {
        "tooltipDelay": 100,
        "hover": true,
        "navigationButtons": false,
        "keyboard": {"enabled": true}
      },
      "edges": {
        "smooth": {"type": "dynamic"}
      }
    }
    """)

    html_str = net.generate_html()
    return html_str


# ---------------------------------------------------------------------------
# Streamlit tab renderer
# ---------------------------------------------------------------------------

def render_streamlit_tab(openai_client=None) -> None:
    """
    Full Streamlit UI for the Fraud Network Visualizer tab.

    Layout:
    - Header with icon and description
    - Top KPI row: 4 metrics
    - Phone number lookup → subgraph + stats
    - Full network view (expander)
    - Top-10 victim table
    """
    # ---- Custom CSS injected once ----
    st.markdown(
        """
        <style>
        /* Node-type legend pills */
        .legend-pill {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 6px;
            color: #0e1117;
        }
        /* Stat box used for lookup results */
        .stat-box {
            background: #1c2333;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }
        .stat-box .stat-label {
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .stat-box .stat-value {
            color: #f1f5f9;
            font-size: 22px;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }
        .stat-box .stat-sub {
            color: #64748b;
            font-size: 11px;
        }
        /* Alert banners */
        .alert-danger {
            background: rgba(239,68,68,0.15);
            border-left: 4px solid #EF4444;
            border-radius: 4px;
            padding: 12px 16px;
            color: #fca5a5;
            margin: 8px 0;
        }
        .alert-success {
            background: rgba(34,197,94,0.12);
            border-left: 4px solid #22C55E;
            border-radius: 4px;
            padding: 12px 16px;
            color: #86efac;
            margin: 8px 0;
        }
        /* Section divider */
        .section-divider {
            border: none;
            border-top: 1px solid #1e293b;
            margin: 24px 0 16px 0;
        }
        /* Graph iframe frame */
        iframe {
            border-radius: 8px;
            border: 1px solid #1e293b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    st.markdown(
        """
        <div style="margin-bottom: 4px;">
            <span style="font-size: 28px; font-weight: 800; color: #f1f5f9;
                         letter-spacing: -0.5px;">
                🕸️ Fraud Network Visualizer
            </span>
        </div>
        <p style="color: #64748b; font-size: 14px; margin-top: 2px; margin-bottom: 16px;">
            Trace how scam operations flow from <b style="color:#FF4B4B">fraud compounds</b>
            through <b style="color:#FF8C00">scammers</b> and
            <b style="color:#FFD700">mule accounts</b> to
            <b style="color:#38BDF8">victims</b>.
            Enter a phone number to map its connections.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ---- Node-type legend ----
    legend_html = " ".join(
        f'<span class="legend-pill" style="background:{color};">'
        f'{"▲" if t == "compound" else "●"} {t.title()}</span>'
        for t, color in NODE_COLORS.items()
    )
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- Load data ----
    @st.cache_data(show_spinner=False)
    def _cached_data() -> dict:
        return load_graph_data()

    @st.cache_data(show_spinner=False)
    def _cached_graph(_data: dict) -> nx.DiGraph:
        return build_networkx_graph(_data)

    with st.spinner("Loading fraud network…"):
        data = _cached_data()
        G = _cached_graph(data)

    # ---- Global KPIs ----
    all_nodes = list(G.nodes(data=True))
    all_victims = [a for _, a in all_nodes if a.get("type") == "victim"]
    all_scammers = [a for _, a in all_nodes if a.get("type") == "scammer"]
    total_lost = sum(v.get("amount_lost", 0) for v in all_victims)
    all_states = {a.get("state") for _, a in all_nodes if a.get("state")}

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Network Nodes", f"{G.number_of_nodes():,}")
    k2.metric("Identified Victims", f"{len(all_victims):,}")
    k3.metric(
        "Total Amount Lost",
        f"₹{total_lost / 1_00_000:.1f}L"
        if total_lost >= 1_00_000
        else f"₹{total_lost:,}",
    )
    k4.metric("States Affected", str(len(all_states)))

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- Phone-number lookup ----
    st.markdown(
        "<p style='font-size:16px; font-weight:700; color:#f1f5f9;'>"
        "🔍 Phone Number Lookup</p>",
        unsafe_allow_html=True,
    )

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        phone_input = st.text_input(
            "Enter phone number",
            placeholder="e.g. +91-98765-43210",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("Trace", type="primary", use_container_width=True)

    # Try pyvis import once to give early feedback
    pyvis_available = True
    try:
        import pyvis  # noqa: F401
    except ImportError:
        pyvis_available = False

    if not pyvis_available:
        st.error(
            "**Pyvis not installed.** Run `pip install pyvis` and restart the app "
            "to enable interactive graph rendering."
        )

    if search_clicked and phone_input.strip():
        sub, stats = get_subgraph(G, data, phone_input.strip())

        if not stats["found"]:
            st.markdown(
                f"<div class='alert-danger'>"
                f"No node found matching <b>{phone_input}</b>. "
                f"Check the number format (+91-XXXXX-XXXXX) and try again."
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            node_type = stats["match_type"]
            color = NODE_COLORS.get(node_type, "#AAAAAA")

            st.markdown(
                f"<div class='alert-danger'>"
                f"<b>⚠ Match found:</b> "
                f"<span style='color:{color}; font-weight:700;'>"
                f"{stats['match_label']}</span> "
                f"({node_type.title()}) is linked to this fraud network."
                f"</div>",
                unsafe_allow_html=True,
            )

            # Sub-stats row
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Nodes in Cluster", sub.number_of_nodes())
            s2.metric("Victims in Cluster", stats["total_victims"])
            s3.metric(
                "Amount Lost (Cluster)",
                f"₹{stats['total_amount_lost'] / 1_00_000:.1f}L"
                if stats["total_amount_lost"] >= 1_00_000
                else f"₹{stats['total_amount_lost']:,}",
            )
            s4.metric("States Affected", stats["states_affected"])

            # Render subgraph
            if pyvis_available and sub.number_of_nodes() > 0:
                st.markdown(
                    "<p style='color:#94a3b8; font-size:13px; margin-top:12px;'>"
                    "Hover over nodes for details. Scroll to zoom. Drag to pan.</p>",
                    unsafe_allow_html=True,
                )
                try:
                    html_sub = render_pyvis_html(
                        sub,
                        highlight_nodes=[stats["match_id"]],
                    )
                    st.components.v1.html(html_sub, height=620, scrolling=False)
                except Exception as exc:
                    st.error(f"Graph rendering error: {exc}")

            # Victim table for this cluster
            cluster_victims = [
                {
                    "Name": attrs.get("label", nid),
                    "Phone": attrs.get("phone", "—"),
                    "State": attrs.get("state", "—"),
                    "Amount Lost (₹)": attrs.get("amount_lost", 0),
                    "Fraud Type": attrs.get("fraud_type", "—"),
                    "Reported": "Yes" if attrs.get("reported") else "No",
                }
                for nid, attrs in sub.nodes(data=True)
                if attrs.get("type") == "victim"
            ]
            if cluster_victims:
                cluster_victims.sort(key=lambda r: r["Amount Lost (₹)"], reverse=True)
                st.markdown(
                    "<p style='font-size:14px; font-weight:600; color:#94a3b8;"
                    " margin-top:18px;'>Victims in this cluster</p>",
                    unsafe_allow_html=True,
                )
                import pandas as pd  # noqa: PLC0415 — deferred
                df_cluster = pd.DataFrame(cluster_victims[:20])
                df_cluster["Amount Lost (₹)"] = df_cluster["Amount Lost (₹)"].apply(
                    lambda x: f"₹{x:,}"
                )
                st.dataframe(df_cluster, use_container_width=True, hide_index=True)

    elif search_clicked:
        st.warning("Please enter a phone number to search.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- Full network view ----
    with st.expander("🌐 View Full Fraud Network", expanded=False):
        st.markdown(
            "<p style='color:#64748b; font-size:13px;'>"
            f"Rendering all <b>{G.number_of_nodes()}</b> nodes and "
            f"<b>{G.number_of_edges()}</b> edges. This may take a few seconds.</p>",
            unsafe_allow_html=True,
        )
        if pyvis_available:
            if st.button("Generate Full Network Graph", key="full_graph_btn"):
                with st.spinner("Rendering network…"):
                    try:
                        html_full = render_pyvis_html(G)
                        st.components.v1.html(html_full, height=680, scrolling=False)
                    except Exception as exc:
                        st.error(f"Graph rendering error: {exc}")
        else:
            st.info("Install pyvis to enable the full network graph.")

    # ---- Top-10 victims by amount lost ----
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:16px; font-weight:700; color:#f1f5f9;'>"
        "💸 Top 10 Victims by Amount Lost</p>",
        unsafe_allow_html=True,
    )

    top_victims = sorted(
        [
            {
                "Name": attrs.get("label", nid),
                "Phone": attrs.get("phone", "—"),
                "State": attrs.get("state", "—"),
                "Amount Lost": attrs.get("amount_lost", 0),
                "Fraud Type": attrs.get("fraud_type", "—"),
                "Reported to Cybercrime": "✅" if attrs.get("reported") else "❌",
            }
            for nid, attrs in G.nodes(data=True)
            if attrs.get("type") == "victim"
        ],
        key=lambda r: r["Amount Lost"],
        reverse=True,
    )[:10]

    import pandas as pd  # noqa: PLC0415 — deferred

    df_top = pd.DataFrame(top_victims)
    df_top["Amount Lost"] = df_top["Amount Lost"].apply(lambda x: f"₹{x:,}")
    st.dataframe(df_top, use_container_width=True, hide_index=True)

    # ---- Footer note ----
    st.markdown(
        "<p style='color:#334155; font-size:11px; margin-top:24px; text-align:center;'>"
        "All data shown is fully synthetic and generated for demonstration purposes. "
        "No real individuals are represented. "
        "Report fraud at <b>cybercrime.gov.in</b> or call helpline <b>1930</b>."
        "</p>",
        unsafe_allow_html=True,
    )
