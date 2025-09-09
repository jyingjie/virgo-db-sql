import importlib


def test_public_exports():
    mod = importlib.import_module("virgo_db_sql")
    # Required symbols
    for name in [
        "__version__",
        "connect",
        "execute_query",
        "EAGLE_DB_URL",
        "MILLENNIUM_DB_URL",
        "MILLIMIL_DB_URL",
        "VirgoDBClient",
        "EagleClient",
        "MillenniumClient",
        "MilliMilClient",
    ]:
        assert hasattr(mod, name), f"Missing export: {name}"


