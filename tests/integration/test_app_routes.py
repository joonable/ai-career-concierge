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


async def test_profile_preflight_allows_web_origin(client):
    response = await client.options(
        "/api/v1/users/me/profile",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "PUT" in response.headers["access-control-allow-methods"]
