import os
import pytest


LIVE_ENV_FLAG = os.getenv("VIRGO_DB_LIVE_TEST", "0")


@pytest.mark.skipif(LIVE_ENV_FLAG not in {"1", "true", "True"}, reason="Live tests disabled")
def test_live_millennium_massive_galaxies_slice():
    from virgo_db_sql import MillenniumClient

    username = os.getenv("VIRGO_DB_USER")
    password = os.getenv("VIRGO_DB_PASSWORD")
    if not username or not password:
        pytest.skip("Missing credentials in environment")

    client = MillenniumClient(username, password)

    sql = """
-- Select positions and K band magnitude for massive galaxies in an 8Mpc/h slice
select 
  stellarmass, mag_K, x, y, z
from 
  Gonzalez2014a..mr7
where 
   x between 0 and 8
   and SnapNum=61
   and stellarmass > 0.01
"""

    rows = client.execute_query(sql)
    assert rows is not None
    assert getattr(rows, "dtype", None) is not None
    assert getattr(rows.dtype, "names", None) is not None


