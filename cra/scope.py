"""Scope-and-hours tracker: budget burn, overservicing alerts, team utilization."""
from .common import d, pct, client_name
import datetime as dt, calendar

def month_progress(as_of):
    t = d(as_of); return t.day / calendar.monthrange(t.year, t.month)[1]

def burn(data):
    prog = month_progress(data["as_of"]); out = []
    for c in data["clients"]:
        used = sum(t["hours"] for t in data["time"] if t["client"] == c["id"] and t["date"][:7] == data["as_of"][:7])
        ratio = pct(used, c["monthly_hours"]); pace = pct(ratio, prog)
        if ratio > 1: alert = "OVER SCOPE"
        elif pace > 1.25: alert = "OVERSERVICING RISK"
        elif pace < .5: alert = "UNDERUSED"
        else: alert = "OK"
        projected = used / prog if prog else used
        out.append({"client": c["id"], "name": c["name"], "budget": c["monthly_hours"], "used": round(used, 1),
                    "burn": ratio, "month_elapsed": prog, "projected": round(projected, 1), "alert": alert})
    return out

def utilization(data):
    res = {}
    for p, cap in data["people"].items():
        h = sum(t["hours"] for t in data["time"] if t["person"] == p and t["date"][:7] == data["as_of"][:7])
        res[p] = {"hours": round(h, 1), "capacity_to_date": round(cap * month_progress(data["as_of"]), 1),
                  "utilization": pct(h, cap * month_progress(data["as_of"]))}
    return res

def to_markdown(data):
    L = [f"# Scope and hours ({data['as_of']})", "", "| Client | Used / Budget | Burn | Month elapsed | Projected | Alert |", "|---|---:|---:|---:|---:|---|"]
    for b in burn(data):
        L.append(f"| {b['name']} | {b['used']} / {b['budget']} | {b['burn']:.0%} | {b['month_elapsed']:.0%} | {b['projected']} | {b['alert']} |")
    L += ["", "## Utilization (billable hours vs capacity to date)", "| Person | Hours | Utilization |", "|---|---:|---:|"]
    L += [f"| {p} | {u['hours']} | {u['utilization']:.0%} |" for p, u in utilization(data).items()]
    return "\n".join(L) + "\n"
