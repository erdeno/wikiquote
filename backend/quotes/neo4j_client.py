import os
from neo4j import GraphDatabase

_URI = os.getenv("NEO4J_URI")
_USER = os.getenv("NEO4J_USER")
_PASS = os.getenv("NEO4J_PASSWORD")
_DB   = os.getenv("NEO4J_DATABASE")

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(_URI, auth=(_USER, _PASS))
    return _driver

# ---- SAFE READ HELPERS (materialize inside the session) ----
def run_read(cypher: str, params: dict):
    """Return a list[dict] where each dict is a record (keys → values)."""
    def _work(tx):
        res = tx.run(cypher, **params)
        return [r.data() for r in res]   # materialize before session closes
    with get_driver().session(database=_DB) as session:
        return session.execute_read(_work)

def run_read_one(cypher: str, params: dict):
    """Return a single dict or None."""
    rows = run_read(cypher, params)
    return rows[0] if rows else None

def health_check_details() -> dict:
    try:
        row = run_read_one("RETURN 1 AS ok", {})
        ok = (row is not None) and (row["ok"] == 1)
        return {"ok": ok, "error": None}
    except Exception as e:
        return {"ok": False, "error": str(e)}