"""Campaign status board and deadline tracker with at-risk flags."""
from .common import d, client_name
ORDER = ["not_started", "in_progress", "waiting_client", "done"]

def flag(item, as_of):
    if item["status"] == "done": return "done"
    days = (d(item["due"]) - d(as_of)).days
    if days < 0: return "OVERDUE"
    if item["status"] == "waiting_client" and days <= 3: return "AT RISK (client dependency)"
    if item["status"] == "not_started" and days <= 7: return "AT RISK (not started)"
    if days <= 2: return "DUE SOON"
    return "on track"

def tracker(data):
    rows = []
    for i in data["deadlines"]:
        rows.append({**i, "days_left": (d(i["due"]) - d(data["as_of"])).days, "flag": flag(i, data["as_of"])})
    return sorted(rows, key=lambda r: r["due"])

def board(data):
    cols = {s: [] for s in ORDER}
    for r in tracker(data): cols[r["status"]].append(r)
    return cols

def to_markdown(data):
    L = [f"# Campaign status board ({data['as_of']})", ""]
    for s, items in board(data).items():
        L.append(f"## {s.replace('_', ' ').title()} ({len(items)})")
        L += [f"- [{r['flag']}] {client_name(data, r['client'])} / {r['campaign']}: {r['name']} (due {r['due']}, {r['owner']})" for r in items] or ["- none"]
        L.append("")
    risky = [r for r in tracker(data) if r["flag"].startswith(("OVERDUE", "AT RISK", "DUE"))]
    L += ["## Needs attention"] + [f"- {r['flag']}: {r['campaign']} - {r['name']} ({r['days_left']} days)" for r in risky]
    return "\n".join(L) + "\n"
