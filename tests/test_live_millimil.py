import os
import pytest


LIVE_ENV_FLAG = os.getenv("VIRGO_DB_LIVE_TEST", "0")


@pytest.mark.skipif(LIVE_ENV_FLAG not in {"1", "true", "True"}, reason="Live tests disabled")
def test_live_millimil_mpa_halo_query():
    from virgo_db_sql import MilliMilClient

    username = os.getenv("VIRGO_DB_USER")
    password = os.getenv("VIRGO_DB_PASSWORD")
    if not username or not password:
        pytest.skip("Missing credentials in environment")

    client = MilliMilClient(username, password)

    sql = """
select *
  from millimil..MPAHalo
 where snapnum=50 
   and np between 100 and 1000 
   and x between 10 and 20
   and y between 10 and 20
   and z between 10 and 20
"""

    try:
        rows = client.execute_query(sql)
        assert rows is not None
        # Structured numpy array should have named fields
        assert getattr(rows, "dtype", None) is not None
        assert getattr(rows.dtype, "names", None) is not None
    except Exception as exc:
        # If the service rejects the SQL, surface the error for debugging
        pytest.fail(f"Live millimil query failed: {exc}")


