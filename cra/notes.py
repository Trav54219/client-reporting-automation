"""Rule-based meeting notes to action items extractor."""
import re

MARKERS = re.compile(r"^\s*[-*]?\s*(action|todo|to-do|next steps?|follow[- ]?up)\s*:\s*(.+)$", re.I)
WILL = re.compile(r"^\s*[-*]?\s*(.+?)\s+(?:will|to)\s+(.+)$", re.I)
DATE = re.compile(r"\b(?:by\s+)?(\d{4}-\d{2}-\d{2}|monday|tuesday|wednesday|thursday|friday|next week|tomorrow|today|end of day|eod)\b", re.I)
OWNER = re.compile(r"^((?:[A-Z][\w]*)(?:\s+[A-Z0-9][\w]*){0,3})\s+(?:to|will)\s+", re.I)
SIGNAL = re.compile(r"\b(will confirm|will send|will share|to send|to share|to update|to confirm|to review)\b", re.I)

def extract(text):
    items, decisions, risks = [], [], []
    for line in text.splitlines():
        raw = line.strip().lstrip("-* ").strip()
        if not raw: continue
        low = raw.lower()
        if low.startswith("decision:"): decisions.append(raw.split(":", 1)[1].strip()); continue
        m = re.search(r"decision:\s*(.+)", raw, re.I)
        if m: decisions.append(m.group(1).strip())
        if low.startswith("risk:"): risks.append(raw.split(":", 1)[1].strip()); continue
        mk = MARKERS.match(line)
        body = mk.group(2) if mk else (raw if SIGNAL.search(raw) else None)
        if not body: continue
        om = OWNER.match(body)
        due = DATE.search(body)
        items.append({"task": body.rstrip("."), "owner": om.group(1) if om else "UNASSIGNED",
                      "due": due.group(1) if due else "no date"})
    return {"action_items": items, "decisions": decisions, "risks": risks}

def to_markdown(res):
    L = ["# Action items", "", "| Owner | Task | Due |", "|---|---|---|"]
    L += [f"| {i['owner']} | {i['task']} | {i['due']} |" for i in res["action_items"]]
    L += ["", "## Decisions"] + [f"- {x}" for x in res["decisions"]] + ["", "## Risks"] + [f"- {x}" for x in res["risks"]]
    return "\n".join(L) + "\n"
