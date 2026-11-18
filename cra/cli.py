import argparse, pathlib, sys
from . import reports, scope, status, onboarding, qbr, notes
from .common import load, ROOT

def main(argv=None):
    p = argparse.ArgumentParser(prog="cra", description="Client reporting automation (synthetic data)")
    p.add_argument("--data"); p.add_argument("--out", default=str(ROOT / "out"))
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report"); r.add_argument("--period", choices=["weekly", "monthly"], default="weekly")
    sub.add_parser("scope"); sub.add_parser("status")
    o = sub.add_parser("onboard"); o.add_argument("--client", default="Example Client (fictional)"); o.add_argument("--date", default="2025-04-01")
    o.add_argument("--channels", default="search,social"); o.add_argument("--goals", default="Grow qualified leads;Improve reporting clarity"); o.add_argument("--hours", type=int, default=40)
    sub.add_parser("qbr")
    n = sub.add_parser("notes"); n.add_argument("file", nargs="?", default=str(ROOT / "data" / "meeting_notes.txt"))
    a = p.parse_args(argv); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    data = load(a.data) if a.cmd not in ("onboard", "notes") else None
    def w(name, text): (out / name).write_text(text); print("wrote", out / name)
    if a.cmd == "report":
        for c in data["clients"]:
            rep = reports.build_report(data, c["id"], a.period)
            w(f"{c['id']}_{a.period}.md", reports.to_markdown(rep)); w(f"{c['id']}_{a.period}.html", reports.to_html(rep))
    elif a.cmd == "scope": w("scope.md", scope.to_markdown(data))
    elif a.cmd == "status": w("status.md", status.to_markdown(data))
    elif a.cmd == "onboard": w("kickoff.md", onboarding.kickoff_doc(a.client, a.date, a.channels.split(","), a.goals.split(";"), a.hours))
    elif a.cmd == "qbr":
        for c in data["clients"]: w(f"{c['id']}_qbr.md", qbr.outline(data, c["id"]))
    elif a.cmd == "notes": w("action_items.md", notes.to_markdown(notes.extract(pathlib.Path(a.file).read_text())))

if __name__ == "__main__": main()
