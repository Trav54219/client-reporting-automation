"""Weekly/monthly client report from campaign metrics. Insights come from fixed rules."""
import html
from .common import d, pct, client_name

def totals(rows):
    t = {k: sum(r[k] for r in rows) for k in ("spend", "impressions", "clicks", "conversions", "revenue")}
    t["ctr"] = pct(t["clicks"], t["impressions"]); t["cvr"] = pct(t["conversions"], t["clicks"])
    t["cpa"] = pct(t["spend"], t["conversions"]); t["roas"] = pct(t["revenue"], t["spend"])
    return t

def split_periods(rows, period, as_of):
    """Return (current, previous) rows. weekly = last 7 days vs the 7 before; monthly = 4 weeks vs prior 4."""
    n = 1 if period == "weekly" else 4
    weeks = sorted({r["week_start"] for r in rows if d(r["week_start"]) <= d(as_of)})
    cur_w, prev_w = set(weeks[-n:]), set(weeks[-2 * n:-n])
    return [r for r in rows if r["week_start"] in cur_w], [r for r in rows if r["week_start"] in prev_w]

def change(cur, prev):
    return (cur - prev) / prev if prev else 0.0

def insights(cur, prev):
    """Plain-language wins/risks/next steps from threshold rules."""
    wins, risks, steps = [], [], []
    if not prev["spend"]:
        return ["First reporting period; no comparison yet."], [], ["Set baseline targets with the client."]
    cpa_c, conv_c, roas_c = change(cur["cpa"], prev["cpa"]), change(cur["conversions"], prev["conversions"]), change(cur["roas"], prev["roas"])
    if conv_c >= .10: wins.append(f"Conversions rose {conv_c:.0%} versus the previous period.")
    if cpa_c <= -.10: wins.append(f"Cost per conversion fell {abs(cpa_c):.0%}.")
    if roas_c >= .10: wins.append(f"Return on ad spend improved {roas_c:.0%}.")
    if conv_c <= -.10: risks.append(f"Conversions dropped {abs(conv_c):.0%}.")
    if cpa_c >= .15: risks.append(f"Cost per conversion rose {cpa_c:.0%}.")
    if cur["roas"] < 1: risks.append(f"Revenue is below spend (ROAS {cur['roas']:.2f}).")
    if change(cur["spend"], prev["spend"]) > .15: risks.append("Spend is up more than 15% without a matching rise in conversions." if conv_c < .15 else "Spend is up more than 15%; confirm budget approval.")
    if not wins: wins.append("Performance held steady; no major swings.")
    if conv_c <= -.10 or cpa_c >= .15: steps += ["Review search terms and creative fatigue; propose a test within the week.", "Walk the client through the cause before they ask."]
    if roas_c >= .10: steps.append("Discuss shifting budget toward the best-returning channel.")
    if not steps: steps.append("Continue current plan; revisit targets at next check-in.")
    return wins, risks, steps

def build_report(data, client_id, period="weekly"):
    rows = [r for r in data["metrics"] if r["client"] == client_id]
    cur_rows, prev_rows = split_periods(rows, period, data["as_of"])
    cur, prev = totals(cur_rows), totals(prev_rows)
    channels = {}
    for ch in sorted({r["channel"] for r in cur_rows}):
        channels[ch] = totals([r for r in cur_rows if r["channel"] == ch])
    wins, risks, steps = insights(cur, prev)
    return {"client": client_name(data, client_id), "period": period, "as_of": data["as_of"], "current": cur,
            "previous": prev, "channels": channels, "wins": wins, "risks": risks, "next_steps": steps}

def to_markdown(r):
    L = [f"# {r['period'].title()} Report: {r['client']}", f"_As of {r['as_of']}. Synthetic data._", "",
         "| Metric | This period | Previous | Change |", "|---|---:|---:|---:|"]
    for k, lab, f in [("spend", "Spend", "${:,.0f}"), ("conversions", "Conversions", "{:,.0f}"), ("cpa", "Cost / conversion", "${:,.2f}"), ("roas", "ROAS", "{:.2f}")]:
        c, p = r["current"][k], r["previous"][k]
        L.append(f"| {lab} | {f.format(c)} | {f.format(p)} | {change(c, p):+.0%} |")
    L += ["", "## By channel", "| Channel | Spend | Conversions | ROAS |", "|---|---:|---:|---:|"]
    L += [f"| {ch} | ${t['spend']:,.0f} | {t['conversions']} | {t['roas']:.2f} |" for ch, t in r["channels"].items()]
    for title, key in [("Wins", "wins"), ("Risks", "risks"), ("Next steps", "next_steps")]:
        L += ["", f"## {title}"] + ([f"- {x}" for x in r[key]] or ["- None this period."])
    return "\n".join(L) + "\n"

def to_html(r):
    e = html.escape
    def ul(items): return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>" if items else "<p>None this period.</p>"
    rows = "".join(f"<tr><td>{e(k)}</td><td>{e(f.format(r['current'][key]))}</td><td>{e(f.format(r['previous'][key]))}</td></tr>"
                   for k, key, f in [("Spend", "spend", "${:,.0f}"), ("Conversions", "conversions", "{:,.0f}"), ("Cost / conversion", "cpa", "${:,.2f}"), ("ROAS", "roas", "{:.2f}")])
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{e(r['client'])} report</title>"
            "<style>body{font:15px system-ui;max-width:680px;margin:2rem auto;padding:0 1rem}td,th{padding:4px 12px;text-align:right}"
            "td:first-child,th:first-child{text-align:left}</style></head><body>"
            f"<h1>{e(r['period'].title())} Report: {e(r['client'])}</h1><p><em>As of {e(r['as_of'])}. Synthetic data.</em></p>"
            f"<table><tr><th>Metric</th><th>This period</th><th>Previous</th></tr>{rows}</table>"
            f"<h2>Wins</h2>{ul(r['wins'])}<h2>Risks</h2>{ul(r['risks'])}<h2>Next steps</h2>{ul(r['next_steps'])}</body></html>")
