"""T-P1-01: GET /catalogue returns valid DCAT v3 JSON-LD.
T-P1-04: SQL injection in ct_node param → no data leak.
T-P1-05: GET /v1/taxonomy/nodes returns correct count.
T-P2-01: /llms.txt returns correct allow/disallow.
T-P2-02: Error response does not contain file paths.
T-P2-03: GET /health returns correct shape."""

from __future__ import annotations


def test_catalogue_dcat_v3(client):
    """T-P1-01."""
    r = client.get("/catalogue")
    assert r.status_code == 200
    body = r.json()
    assert "@context" in body
    assert body["@type"] == "dcat:Catalog"
    datasets = body["dcat:dataset"]
    assert len(datasets) == 2
    startups_ds = datasets[0]
    assert "odrl:hasPolicy" in startups_ds


def test_sql_injection_no_leak(client):
    """T-P1-04."""
    r = client.get("/v1/startups", params={"ct_node": "' OR 1=1 --"})
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0


def test_taxonomy_node_count(client):
    """T-P1-05 (seed data has 3 nodes)."""
    r = client.get("/v1/taxonomy/nodes")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 3


def test_llms_txt(client):
    """T-P2-01."""
    r = client.get("/llms.txt")
    assert r.status_code == 200
    text = r.text
    assert "Disallow: /v1/api-keys" in text
    assert "Allow: /v1/startups" in text


def test_error_no_file_paths(client):
    """T-P2-02."""
    r = client.get("/v1/startups/nonexistent-id-12345")
    assert "/opt/" not in r.text
    assert "Traceback" not in r.text


def test_health_endpoint(client):
    """T-P2-03."""
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert "version" in body


def test_startups_pagination(client):
    r = client.get("/v1/startups?limit=2&offset=0")
    assert r.status_code == 200
    body = r.json()
    assert len(body["data"]) <= 2
    assert body["meta"]["limit"] == 2
    assert body["meta"]["offset"] == 0


def test_startups_filter_by_country(client):
    r = client.get("/v1/startups?country=CO")
    assert r.status_code == 200
    for s in r.json()["data"]:
        assert s["country"] == "CO"


def test_startups_export_csv(client):
    r = client.get("/v1/startups/export")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers.get("content-disposition", "")
    lines = r.text.strip().split("\n")
    assert len(lines) >= 2  # header + at least 1 data row


def test_taxonomy_node_with_linked_startups(client):
    r = client.get("/v1/taxonomy/nodes/CT-EN-001")
    assert r.status_code == 200
    body = r.json()["data"]
    assert body["id"] == "CT-EN-001"
    assert "linked_startups" in body


def test_response_headers(client):
    r = client.get("/v1/startups?limit=1")
    assert "X-CTH-Dataset-Version" in r.headers
    assert "X-CTH-Licence" in r.headers
    assert "X-Request-ID" in r.headers
