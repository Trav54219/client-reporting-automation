"""QBR deck outline from monthly report data across a quarter."""
from .reports import totals, change, insights
from .common import client_name
from .scope import burn

def outline(data, client_id):
    rows = [r for r in data["metrics"] if r["client"] == client_id]
    weeks = sorted({r["week_start"] for r in rows}); half = len(weeks) // 2
    early, late = totals([r for r in rows if r["week_start"] in weeks[:half]]), totals([r for r in rows if r["week_start"] in weeks[half:]])
    wins, risks, steps = insights(late, early)
    b = next(x for x in burn(data) if x["client"] == client_id)
    slides = [
        ("Agenda and objectives", ["What we set out to do", "What happened", "What we recommend"]),
        ("Results vs. prior half of the period", [f"Spend ${late['spend']:,.0f} ({change(late['spend'], early['spend']):+.0%})", f"Conversions {late['conversions']} ({change(late['conversions'], early['conversions']):+.0%})", f"ROAS {late['roas']:.2f} (was {early['roas']:.2f})"]),
        ("Wins", wins), ("Risks and what we are doing about them", risks or ["No material risks flagged by rules"]),
        ("Channel breakdown", [f"{ch}: ROAS {totals([r for r in rows if r['channel']==ch])['roas']:.2f}" for ch in sorted({r['channel'] for r in rows})]),
        ("Scope and hours", [f"{b['used']} of {b['budget']} hours used this month ({b['alert']})"]),
        ("Recommendations for next quarter", steps), ("Decisions needed and next steps", ["Approve test budget", "Confirm priorities", "Set next QBR date"]),
    ]
    out = [f"# QBR outline: {client_name(data, client_id)}", ""]
    for n, (t, pts) in enumerate(slides, 1):
        out += [f"## Slide {n}: {t}"] + [f"- {p}" for p in pts] + [""]
    return "\n".join(out)
