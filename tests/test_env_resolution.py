import os
import importlib


def test_env_fallback(monkeypatch):
    from virgo_db_sql.client import VirgoDBClient, EAGLE_DB_URL

    monkeypatch.setenv("VIRGO_DB_USER", "user_env")
    monkeypatch.setenv("VIRGO_DB_PASSWORD", "pass_env")
    monkeypatch.setenv("VIRGO_DB_URL", EAGLE_DB_URL)

    client = VirgoDBClient(username=None, password=None, db_url=None)
    # indirect checks: attributes
    assert client.db_url == EAGLE_DB_URL


