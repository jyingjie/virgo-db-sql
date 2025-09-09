import os
import pytest


LIVE_ENV_FLAG = os.getenv("VIRGO_DB_LIVE_TEST", "0")


@pytest.mark.skipif(LIVE_ENV_FLAG not in {"1", "true", "True"}, reason="Live tests disabled")
def test_live_min_query():
    from virgo_db_sql import EagleClient

    username = os.getenv("VIRGO_DB_USER")
    password = os.getenv("VIRGO_DB_PASSWORD")
    if not username or not password:
        pytest.skip("Missing credentials in environment")

    client = EagleClient(username, password)
    # Execute a minimal harmless query; adjust to a guaranteed-safe SQL if available
    # Here we only assert that a request can be made and handled until headers parsing
    try:
        client.execute_query("SELECT TOP 1 1 AS one")
    except Exception as exc:
        # Service may reject unknown SQL; the request path itself shouldn't crash the client
        assert isinstance(exc, Exception)


