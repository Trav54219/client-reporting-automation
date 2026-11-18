"""Client onboarding checklist and kickoff doc generator."""
import datetime as dt
from .common import d

PHASES = [
    ("Before kickoff", -3, ["Signed scope of work and billing contact on file", "Shared folder and reporting channel created", "Access requests sent (ad accounts, analytics, CMS)", "Internal handoff from sales to account lead"]),
    ("Kickoff week", 0, ["Kickoff call held; goals and success metrics agreed", "Stakeholders, approvers and escalation contact confirmed", "Brand assets and guidelines received", "Tracking audit scheduled"]),
    ("First 30 days", 14, ["Tracking verified end to end", "Baseline metrics captured", "First reporting cadence delivered", "Hours budget and scope loaded into tracker"]),
]
CHANNEL_ITEMS = {"search": "Search account access and conversion actions checked", "social": "Social ad account and pixel access confirmed", "email": "Email platform access and list consent reviewed"}

def checklist(client, kickoff_date, channels):
    k = d(kickoff_date); items = []
    for phase, offset, tasks in PHASES:
        tasks = list(tasks)
        if phase == "Before kickoff": tasks += [CHANNEL_ITEMS[c] for c in channels if c in CHANNEL_ITEMS]
        for t in tasks: items.append({"phase": phase, "task": t, "due": str(k + dt.timedelta(days=offset)), "done": False})
    return items

def kickoff_doc(client, kickoff_date, channels, goals, monthly_hours):
    L = [f"# Kickoff: {client}", f"Date: {kickoff_date}", "", "## Agenda", "1. Introductions and roles", "2. Goals and success metrics", "3. Channels and scope", "4. Reporting cadence", "5. Approvals and communication", "6. Open questions", "",
         "## Goals"] + [f"- {g}" for g in goals] + ["", "## Scope", f"- Channels: {', '.join(channels)}", f"- Monthly hours budget: {monthly_hours}",
         "- Hours are tracked and shared monthly; changes to scope go through a written change request.", "", "## Working agreement",
         "- Weekly report each Monday; monthly summary by the 5th business day", "- Client approvals within 2 business days to protect launch dates", "", "## Onboarding checklist"]
    L += [f"- [ ] ({i['phase']}, by {i['due']}) {i['task']}" for i in checklist(client, kickoff_date, channels)]
    return "\n".join(L) + "\n"
