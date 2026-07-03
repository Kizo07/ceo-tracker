"""Contract tests for company endpoints.

Guards CONTRACT-001: GET /api/companies must return a bare JSON array, not a
wrapper object like { "items": [...] }. The frontend companies.ts is typed to
the wrapper today; the agreed target is the bare array (see specs/issues.yaml).
"""
from app.models import Company


def test_companies_returns_bare_array(client, db_session):
    # Empty DB -> bare empty array (not {"items": []})
    resp = client.get("/api/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list), "GET /api/companies must return a bare array (CONTRACT-001)"
    assert data == []


def test_companies_list_shape(client, db_session):
    db_session.add(Company(name="Acme", ticker="ACME", is_tracked=True))
    db_session.add(Company(name="Globex", ticker="GLBX", is_tracked=False))
    db_session.commit()

    resp = client.get("/api/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    names = {c["name"] for c in data}
    assert names == {"Acme", "Globex"}
    # Each item carries the documented fields (CompanyResponse).
    first = data[0]
    for field in ("id", "name", "ticker", "is_tracked"):
        assert field in first


def test_companies_filter_tracked(client, db_session):
    db_session.add(Company(name="Acme", ticker="ACME", is_tracked=True))
    db_session.add(Company(name="Globex", ticker="GLBX", is_tracked=False))
    db_session.commit()

    resp = client.get("/api/companies", params={"is_tracked": "true"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Acme"


def test_company_by_missing_id_404(client):
    resp = client.get("/api/companies/9999")
    assert resp.status_code == 404
