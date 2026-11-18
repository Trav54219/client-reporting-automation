import json, pathlib, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(path=None):
    return json.loads((pathlib.Path(path) if path else ROOT / "data" / "synthetic.json").read_text())

def d(s): return dt.date.fromisoformat(s)

def pct(a, b): return (a / b) if b else 0.0

def client_name(data, cid):
    return next(c["name"] for c in data["clients"] if c["id"] == cid)
