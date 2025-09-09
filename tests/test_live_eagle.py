import os
import pytest


LIVE_ENV_FLAG = os.getenv("VIRGO_DB_LIVE_TEST", "0")


@pytest.mark.skipif(LIVE_ENV_FLAG not in {"1", "true", "True"}, reason="Live tests disabled")
def test_live_eagle_colour_magnitude():
    from virgo_db_sql import EagleClient

    username = os.getenv("VIRGO_DB_USER")
    password = os.getenv("VIRGO_DB_PASSWORD")
    if not username or not password:
        pytest.skip("Missing credentials in environment")

    client = EagleClient(username, password)

    sql = """
SELECT        
    (mag.g_nodust - mag.r_nodust) as g_minus_r,
    mag.r_nodust as r
FROM 
    RefL0100N1504_SubHalo as gal,
    RefL0100N1504_Magnitudes as mag,
    RefL0100N1504_Aperture as ape
WHERE  
    gal.SnapNum = 27 and      
    gal.SubGroupNumber = 0 and 
    ape.Mass_Star > 1.0e9 and  
    ape.ApertureSize = 30 and 

    gal.GalaxyID = mag.GalaxyID and
    gal.GalaxyID = ape.GalaxyID
"""

    rows = client.execute_query(sql)
    assert rows is not None
    assert getattr(rows, "dtype", None) is not None
    assert getattr(rows.dtype, "names", None) is not None


