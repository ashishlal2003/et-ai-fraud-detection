"""
Generate a realistic synthetic Indian fraud network graph and save to data/fraud_network.json.

Network structure:
  - 5  compound nodes  (fraud hotspot locations)
  - 20 scammer nodes   (linked to compounds)
  - 40 mule accounts   (used to launder money)
  - 200 victim nodes   (pan-India distribution)

Edges:
  compound  -> scammer  (operates)
  scammer   -> victim   (called)
  scammer   -> mule     (transferred)
  mule      -> mule     (layered)
"""

import json
import random
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

random.seed(42)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

FRAUD_HOTSPOTS = [
    {"location": "Jamtara", "state": "Jharkhand", "lat": 24.0, "lon": 86.5},
    {"location": "Mewat",   "state": "Haryana",   "lat": 28.0, "lon": 77.0},
    {"location": "Bharatpur","state": "Rajasthan", "lat": 27.2, "lon": 77.5},
    {"location": "Mathura",  "state": "Uttar Pradesh","lat": 27.5, "lon": 77.7},
    {"location": "Nuh",      "state": "Haryana",   "lat": 28.1, "lon": 77.0},
]

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Jammu and Kashmir",
]

# Weighted distribution – more victims from populous states
STATE_WEIGHTS = {
    "Uttar Pradesh": 12, "Maharashtra": 10, "Bihar": 8, "West Bengal": 7,
    "Madhya Pradesh": 6, "Rajasthan": 6, "Gujarat": 5, "Karnataka": 5,
    "Andhra Pradesh": 4, "Tamil Nadu": 4, "Telangana": 4, "Odisha": 3,
    "Haryana": 3, "Punjab": 3, "Assam": 3, "Jharkhand": 3, "Delhi": 5,
    "Kerala": 2, "Chhattisgarh": 2, "Uttarakhand": 1,
}
# Remaining states
for s in INDIAN_STATES:
    if s not in STATE_WEIGHTS:
        STATE_WEIGHTS[s] = 1

STATES_LIST = list(STATE_WEIGHTS.keys())
STATES_PROBS = [STATE_WEIGHTS[s] for s in STATES_LIST]
STATES_TOTAL = sum(STATES_PROBS)
STATES_PROBS = [p / STATES_TOTAL for p in STATES_PROBS]

FIRST_NAMES = [
    "Ravi", "Suresh", "Ramesh", "Mahesh", "Rajesh", "Dinesh", "Naresh",
    "Lokesh", "Ganesh", "Umesh", "Priya", "Sunita", "Geeta", "Kavita",
    "Anita", "Mamta", "Shobha", "Rekha", "Usha", "Lata", "Vikram",
    "Ajay", "Sanjay", "Vijay", "Rohit", "Mohit", "Sumit", "Amit",
    "Tarun", "Varun", "Kiran", "Arjun", "Rahul", "Kunal", "Vishal",
    "Deepak", "Prakash", "Aakash", "Vivek", "Rakesh", "Sachin", "Manish",
    "Yogesh", "Nitesh", "Hitesh", "Paresh", "Haresh", "Jitesh", "Shailesh",
    "Lalita", "Saroj", "Pushpa", "Kamla", "Poonam", "Renu", "Manju",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Yadav", "Mishra",
    "Tiwari", "Dubey", "Pandey", "Shukla", "Srivastava", "Agarwal",
    "Jain", "Bansal", "Garg", "Maheshwari", "Mittal", "Khanna", "Malhotra",
    "Patel", "Shah", "Mehta", "Joshi", "Desai", "Nair", "Pillai",
    "Reddy", "Naidu", "Rao", "Iyer", "Iyengar", "Menon", "Krishnan",
    "Bose", "Das", "Ghosh", "Chatterjee", "Mukherjee", "Ganguly",
    "Mondal", "Roy", "Sen", "Paul", "Dey", "Saha", "Biswas",
    "Mandal", "Mandi", "Hussain", "Ansari", "Khan", "Sheikh",
]

BANK_NAMES = [
    "SBI", "HDFC", "ICICI", "Axis", "PNB", "Kotak", "Yes Bank",
    "Canara Bank", "Union Bank", "Bank of Baroda", "IDFC First",
    "IndusInd", "RBL Bank", "Federal Bank", "Paytm Payments Bank",
    "Airtel Payments Bank",
]

UPI_SUFFIXES = ["@oksbi", "@okhdfcbank", "@okaxis", "@paytm", "@ybl", "@upi", "@ibl", "@axisbank"]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_phone():
    prefixes = ["70", "73", "74", "75", "76", "77", "78", "79",
                "80", "81", "82", "83", "84", "85", "86", "87",
                "88", "89", "90", "91", "92", "93", "94", "95",
                "96", "97", "98", "99"]
    prefix = random.choice(prefixes)
    rest = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"+91{prefix}{rest}"


def random_upi(name: str) -> str:
    handle = name.lower().replace(" ", "")[:8] + str(random.randint(10, 99))
    return handle + random.choice(UPI_SUFFIXES)


def random_date(start_year=2022, end_year=2024) -> str:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def random_state() -> str:
    return random.choices(STATES_LIST, weights=STATES_PROBS, k=1)[0]


def random_amount_victim() -> int:
    # Skewed: most victims lose smaller amounts
    tiers = [
        (500, 5000, 0.30),
        (5001, 25000, 0.35),
        (25001, 100000, 0.25),
        (100001, 300000, 0.08),
        (300001, 500000, 0.02),
    ]
    r = random.random()
    cumulative = 0.0
    for lo, hi, prob in tiers:
        cumulative += prob
        if r <= cumulative:
            return random.randint(lo, hi)
    return random.randint(500, 500000)


# ---------------------------------------------------------------------------
# Build nodes
# ---------------------------------------------------------------------------

def build_compounds():
    nodes = []
    for i, hs in enumerate(FRAUD_HOTSPOTS):
        node_id = f"compound_{i+1}"
        nodes.append({
            "id": node_id,
            "type": "compound",
            "label": f"Fraud Compound - {hs['location']}",
            "location": hs["location"],
            "state": hs["state"],
            "lat": hs["lat"],
            "lon": hs["lon"],
            "active_since": random_date(2019, 2021),
            "estimated_members": random.randint(20, 80),
        })
    return nodes


def build_scammers(compound_nodes):
    nodes = []
    compound_ids = [c["id"] for c in compound_nodes]
    for i in range(1, 21):
        name = random_name()
        node_id = f"scammer_{i}"
        # scammer_1 has a fixed demo phone so the UI placeholder is always usable
        phone = "+91-98765-43210" if i == 1 else random_phone()
        compound = random.choice(compound_ids)
        # Pick state matching compound
        compound_state = next(c["state"] for c in compound_nodes if c["id"] == compound)
        nodes.append({
            "id": node_id,
            "type": "scammer",
            "label": name,
            "phone": phone,
            "alias": f"Agent_{random.randint(100,999)}",
            "compound_id": compound,
            "state": compound_state,
            "upi": random_upi(name),
            "bank": random.choice(BANK_NAMES),
            "account_no": "XXXX" + "".join([str(random.randint(0, 9)) for _ in range(8)]),
            "date_joined": random_date(2020, 2023),
            "specialisation": random.choice(["digital_arrest", "kyc_scam", "investment_fraud"]),
            "calls_made": random.randint(200, 2000),
        })
    return nodes


def build_mules(n=40):
    nodes = []
    for i in range(1, n + 1):
        name = random_name()
        node_id = f"mule_{i}"
        nodes.append({
            "id": node_id,
            "type": "mule",
            "label": name,
            "phone": random_phone(),
            "upi": random_upi(name),
            "bank": random.choice(BANK_NAMES),
            "account_no": "XXXX" + "".join([str(random.randint(0, 9)) for _ in range(8)]),
            "state": random_state(),
            "amount": random.randint(50000, 2000000),
            "date_opened": random_date(2021, 2023),
            "kyc_type": random.choice(["aadhaar", "voter_id", "fake_id"]),
            "active": random.choice([True, True, False]),
        })
    return nodes


def build_victims(n=200):
    nodes = []
    for i in range(1, n + 1):
        name = random_name()
        node_id = f"victim_{i}"
        amount = random_amount_victim()
        state = random_state()
        nodes.append({
            "id": node_id,
            "type": "victim",
            "label": name,
            "phone": random_phone(),
            "state": state,
            "amount_lost": amount,
            "date_of_incident": random_date(2022, 2024),
            "fraud_type": random.choice(["digital_arrest", "kyc_scam", "investment_fraud"]),
            "reported_to_police": random.choice([True, False, False]),  # most don't report
            "upi": random_upi(name) if random.random() < 0.6 else None,
            "bank": random.choice(BANK_NAMES),
        })
    return nodes


# ---------------------------------------------------------------------------
# Build edges
# ---------------------------------------------------------------------------

def build_edges(compounds, scammers, mules, victims):
    edges = []

    scammer_ids = [s["id"] for s in scammers]
    mule_ids = [m["id"] for m in mules]
    victim_ids = [v["id"] for v in victims]
    victim_map = {v["id"]: v for v in victims}
    scammer_map = {s["id"]: s for s in scammers}

    # compound -> scammer (operates)
    for scammer in scammers:
        edges.append({
            "source": scammer["compound_id"],
            "target": scammer["id"],
            "relation": "operates",
            "weight": 1.0,
        })

    # scammer -> victim (called)
    # Each scammer victimises 3-15 victims
    victim_pool = list(victim_ids)
    random.shuffle(victim_pool)
    idx = 0
    for scammer in scammers:
        n_victims = random.randint(3, 15)
        assigned = []
        while len(assigned) < n_victims and idx < len(victim_pool):
            assigned.append(victim_pool[idx])
            idx += 1
        if idx >= len(victim_pool):
            victim_pool = list(victim_ids)
            random.shuffle(victim_pool)
            idx = 0
        for vid in assigned:
            v = victim_map[vid]
            edges.append({
                "source": scammer["id"],
                "target": vid,
                "relation": "called",
                "amount_extracted": v["amount_lost"],
                "date": v["date_of_incident"],
            })

    # scammer -> mule (transferred)
    # Each scammer uses 1-4 mules
    for scammer in scammers:
        chosen_mules = random.sample(mule_ids, k=random.randint(1, 4))
        for mid in chosen_mules:
            edges.append({
                "source": scammer["id"],
                "target": mid,
                "relation": "transferred",
                "amount": random.randint(10000, 500000),
                "date": random_date(2022, 2024),
            })

    # mule -> mule (layered transfers - create a chain)
    # Connect ~25% of mule pairs
    mule_shuffled = list(mule_ids)
    random.shuffle(mule_shuffled)
    n_mule_edges = len(mule_ids) // 2
    seen_pairs = set()
    added = 0
    for _ in range(n_mule_edges * 3):  # try more than needed to fill quota
        src, tgt = random.sample(mule_ids, 2)
        pair = (src, tgt)
        if pair not in seen_pairs and src != tgt:
            seen_pairs.add(pair)
            edges.append({
                "source": src,
                "target": tgt,
                "relation": "layered",
                "amount": random.randint(5000, 300000),
                "date": random_date(2022, 2024),
            })
            added += 1
            if added >= n_mule_edges:
                break

    return edges


# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------

def print_summary(nodes, edges):
    victims = [n for n in nodes if n["type"] == "victim"]
    total_amount = sum(v["amount_lost"] for v in victims)
    states_affected = len(set(v["state"] for v in victims))
    avg_amount = total_amount / len(victims) if victims else 0

    fraud_type_counts = defaultdict(int)
    for v in victims:
        fraud_type_counts[v["fraud_type"]] += 1

    print("\n=== Fraud Network Summary ===")
    print(f"Total nodes           : {len(nodes)}")
    print(f"  Compounds           : {sum(1 for n in nodes if n['type'] == 'compound')}")
    print(f"  Scammers            : {sum(1 for n in nodes if n['type'] == 'scammer')}")
    print(f"  Mule accounts       : {sum(1 for n in nodes if n['type'] == 'mule')}")
    print(f"  Victims             : {len(victims)}")
    print(f"Total edges           : {len(edges)}")
    print(f"Total amount lost     : Rs {total_amount:,.0f}")
    print(f"Average per victim    : Rs {avg_amount:,.0f}")
    print(f"States affected       : {states_affected}")
    print(f"Reported to police    : {sum(1 for v in victims if v.get('reported_to_police'))}")
    print(f"\nFraud type breakdown:")
    for ft, count in sorted(fraud_type_counts.items()):
        print(f"  {ft:<25} {count}")

    top_states = defaultdict(int)
    for v in victims:
        top_states[v["state"]] += v["amount_lost"]
    top5 = sorted(top_states.items(), key=lambda x: -x[1])[:5]
    print(f"\nTop 5 states by amount lost:")
    for state, amt in top5:
        print(f"  {state:<25} Rs {amt:,.0f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base = Path(__file__).parent   # data/
    out_path = base / "fraud_network.json"

    print("Generating synthetic fraud network ...")

    compounds = build_compounds()
    scammers = build_scammers(compounds)
    mules = build_mules(40)
    victims = build_victims(200)
    all_nodes = compounds + scammers + mules + victims

    edges = build_edges(compounds, scammers, mules, victims)

    network = {
        "metadata": {
            "description": "Synthetic Indian fraud network for research/demo purposes",
            "generated_date": "2024-01-01",
            "node_count": len(all_nodes),
            "edge_count": len(edges),
            "node_types": ["compound", "scammer", "mule", "victim"],
            "edge_types": ["operates", "called", "transferred", "layered"],
        },
        "nodes": all_nodes,
        "edges": edges,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(network, f, ensure_ascii=False, indent=2, default=str)

    print(f"Saved fraud network to {out_path}")
    print_summary(all_nodes, edges)


if __name__ == "__main__":
    main()
