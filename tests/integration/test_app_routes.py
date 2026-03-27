async def test_root_returns_api_welcome_payload(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "AI Career Concierge API",
        "status": "ok",
        "docs_url": "/docs",
        "healthcheck_url": "/healthz",
    }


async def test_healthz_returns_runtime_status(client):
    response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "env": "test",
    }
