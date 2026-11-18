"""Deterministic SYNTHETIC data generator. Every client, person and number is invented."""
import json, random, datetime as dt, pathlib

AS_OF = "2025-03-14"
CLIENTS = [
    {"id": "northwind", "name": "Northwind Outfitters (fictional)", "am": "Account Manager A", "monthly_hours": 60, "channels": ["search", "social", "email"]},
    {"id": "brightleaf", "name": "Brightleaf Dental (fictional)", "am": "Account Manager B", "monthly_hours": 40, "channels": ["search", "social"]},
    {"id": "harborline", "name": "Harborline Logistics (fictional)", "am": "Account Manager A", "monthly_hours": 30, "channels": ["search", "email"]},
]
PEOPLE = {"Strategist 1": 120, "Designer 1": 100, "Analyst 1": 110, "Coordinator 1": 120}  # monthly billable capacity (hrs)

def build():
    rnd = random.Random(42)
    start = dt.date(2025, 1, 20)
    metrics = []
    for c in CLIENTS:
        for ch in c["channels"]:
            base = {"search": 2500, "social": 1800, "email": 400}[ch]
            for w in range(8):
                drift = {"northwind": 1.0 + .04 * w, "brightleaf": 1.0 - .05 * w, "harborline": 1.0}[c["id"]]
                spend = round(base * rnd.uniform(.9, 1.1), 2)
                clicks = int(spend / rnd.uniform(1.2, 2.2))
                conv = int(clicks * rnd.uniform(.03, .06) * drift)
                metrics.append({"client": c["id"], "week_start": str(start + dt.timedelta(weeks=w)), "channel": ch,
                                "spend": spend, "impressions": clicks * rnd.randint(22, 40), "clicks": clicks,
                                "conversions": conv, "revenue": round(conv * rnd.uniform(70, 110), 2)})
    people = list(PEOPLE)
    time = []
    for c in CLIENTS:
        mult = {"northwind": 1.25, "brightleaf": .7, "harborline": 1.0}[c["id"]]
        total = c["monthly_hours"] * mult * .85  # through mid-month of March
        n = 14
        for i in range(n):
            time.append({"client": c["id"], "person": rnd.choice(people), "date": f"2025-03-{rnd.randint(3,13):02d}",
                         "hours": round(total / n, 2), "task": rnd.choice(["reporting", "creative", "campaign setup", "client call", "optimization"])})
    d = lambda s: s
    deadlines = [
        {"client": "northwind", "campaign": "Spring Launch", "name": "Creative approval", "due": "2025-03-12", "status": "waiting_client", "owner": "Designer 1"},
        {"client": "northwind", "campaign": "Spring Launch", "name": "Landing page QA", "due": "2025-03-17", "status": "in_progress", "owner": "Coordinator 1"},
        {"client": "northwind", "campaign": "Spring Launch", "name": "Go live", "due": "2025-03-20", "status": "not_started", "owner": "Strategist 1"},
        {"client": "brightleaf", "campaign": "New Patient Search", "name": "Keyword refresh", "due": "2025-03-14", "status": "in_progress", "owner": "Analyst 1"},
        {"client": "brightleaf", "campaign": "New Patient Search", "name": "Monthly report", "due": "2025-03-31", "status": "not_started", "owner": "Analyst 1"},
        {"client": "harborline", "campaign": "Q1 Nurture", "name": "Email sequence draft", "due": "2025-03-10", "status": "in_progress", "owner": "Strategist 1"},
        {"client": "harborline", "campaign": "Q1 Nurture", "name": "Send schedule locked", "due": "2025-03-28", "status": "not_started", "owner": "Coordinator 1"},
        {"client": "harborline", "campaign": "Q1 Nurture", "name": "Prior phase wrap", "due": "2025-03-05", "status": "done", "owner": "Coordinator 1"},
    ]
    notes = """Weekly sync - Northwind - 2025-03-11
Attendees: Account Manager A, Strategist 1, Client Marketing Lead
- We reviewed spring creative. Decision: go with option B for the hero banner.
- Action: Designer 1 to send final banner sizes by Friday.
- Client Marketing Lead will confirm the promo code by 2025-03-13.
- Risk: legal sign-off on the offer wording is still pending.
- TODO: Coordinator 1 to update the launch checklist.
- Next steps: Strategist 1 to share the budget split with the client next week.
"""
    return {"clients": CLIENTS, "people": PEOPLE, "metrics": metrics, "time": time, "deadlines": deadlines, "as_of": AS_OF}, notes

if __name__ == "__main__":
    data, notes = build()
    out = pathlib.Path(__file__).resolve().parent.parent / "data"
    (out / "synthetic.json").write_text(json.dumps(data, indent=1))
    (out / "meeting_notes.txt").write_text(notes)
    print("wrote", out)
