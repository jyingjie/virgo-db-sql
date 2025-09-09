import os


def pytest_sessionstart(session):
    # Best-effort load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


