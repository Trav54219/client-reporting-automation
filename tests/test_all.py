import pytest
from cra import reports, scope, status, onboarding, qbr, notes, sample_data
from cra.common import load

@pytest.fixture(scope="module")
def data(): return load()

def test_sample_data_is_deterministic():
    a, _ = sample_data.build(); b, _ = sample_data.build()
    assert a == b

def test_report_totals_and_formats(data):
    r = reports.build_report(data, "northwind", "weekly")
    assert r["current"]["spend"] > 0 and set(r["channels"]) == {"search", "social", "email"}
    md, html = reports.to_markdown(r), reports.to_html(r)
    assert "## Wins" in md and "<h2>Risks</h2>" in html and "Synthetic" in md

def test_monthly_uses_four_weeks(data):
    rows = [x for x in data["metrics"] if x["client"] == "harborline"]
    cur, prev = reports.split_periods(rows, "monthly", data["as_of"])
    assert len({x["week_start"] for x in cur}) == 4 and len({x["week_start"] for x in prev}) == 4

def test_insight_rules():
    prev = {"spend": 1000, "conversions": 100, "cpa": 10, "roas": 2.0}
    good = {"spend": 1000, "conversions": 120, "cpa": 8, "roas": 2.5}
    bad = {"spend": 1300, "conversions": 70, "cpa": 18, "roas": .9}
    w, r, s = reports.insights(good, prev); assert w and not r
    w, r, s = reports.insights(bad, prev); assert len(r) >= 3 and any("test" in x for x in s)

def test_first_period_no_comparison():
    z = {"spend": 0, "conversions": 0, "cpa": 0, "roas": 0}
    w, r, s = reports.insights({"spend": 5, "conversions": 1, "cpa": 5, "roas": 1}, z)
    assert "First reporting period" in w[0]

def test_scope_alerts(data):
    b = {x["client"]: x for x in scope.burn(data)}
    assert b["northwind"]["alert"] in ("OVER SCOPE", "OVERSERVICING RISK")
    assert b["brightleaf"]["burn"] < b["northwind"]["burn"]

def test_scope_over_budget_rule(data):
    d = dict(data); d["time"] = data["time"] + [{"client": "harborline", "person": "Analyst 1", "date": "2025-03-13", "hours": 100, "task": "x"}]
    assert {x["client"]: x for x in scope.burn(d)}["harborline"]["alert"] == "OVER SCOPE"

def test_utilization(data):
    u = scope.utilization(data); assert all(v["utilization"] >= 0 for v in u.values()) and "Designer 1" in u

def test_deadline_flags():
    asof = "2025-03-14"
    assert status.flag({"due": "2025-03-12", "status": "in_progress"}, asof) == "OVERDUE"
    assert status.flag({"due": "2025-03-12", "status": "done"}, asof) == "done"
    assert status.flag({"due": "2025-03-16", "status": "waiting_client"}, asof).startswith("AT RISK")
    assert status.flag({"due": "2025-03-18", "status": "not_started"}, asof).startswith("AT RISK")
    assert status.flag({"due": "2025-04-20", "status": "not_started"}, asof) == "on track"

def test_board_and_markdown(data):
    cols = status.board(data); assert sum(len(v) for v in cols.values()) == len(data["deadlines"])
    assert "Needs attention" in status.to_markdown(data)

def test_onboarding_dates_and_channels():
    items = onboarding.checklist("X", "2025-04-10", ["email"])
    assert any("Email platform" in i["task"] for i in items)
    assert min(i["due"] for i in items) == "2025-04-07"
    doc = onboarding.kickoff_doc("X", "2025-04-10", ["email"], ["Goal A"], 20)
    assert "Goal A" in doc and "Monthly hours budget: 20" in doc

def test_qbr_has_all_sections(data):
    t = qbr.outline(data, "brightleaf")
    for s in ("Wins", "Risks", "Scope and hours", "Recommendations"): assert s in t

def test_notes_extraction():
    res = notes.extract(open("data/meeting_notes.txt").read())
    owners = {i["owner"] for i in res["action_items"]}
    assert "Designer 1" in owners and len(res["action_items"]) >= 3
    assert res["decisions"] and res["risks"]
    assert any(i["due"] == "2025-03-13" for i in res["action_items"])

def test_notes_unassigned():
    res = notes.extract("- TODO: update the deck")
    assert res["action_items"][0]["owner"] == "UNASSIGNED"

def test_cli_end_to_end(tmp_path):
    from cra.cli import main
    for cmd in (["report", "--period", "monthly"], ["scope"], ["status"], ["qbr"], ["notes"], ["onboard"]):
        main(["--out", str(tmp_path)] + cmd)
    assert (tmp_path / "northwind_monthly.html").exists() and (tmp_path / "action_items.md").exists()
