# virgo_db_sql
A lightweight Python client for querying Virgo databases: EAGLE, Millennium, and milli-Millennium.

## Installation

- From PyPI (placeholder): `pip install virgo_db_sql`
- From GitHub: `pip install git+https://github.com/jyingjie/virgo-db-sql.git`
- From source:
  - `git clone <your-repo-url>`
  - `pip install -e .`

## Usage

```python
# Option 1: Functional API (backward-compatible)
from virgo_db_sql import connect, execute_query
from virgo_db_sql import EAGLE_DB_URL, MILLENNIUM_DB_URL, MILLIMIL_DB_URL

con = connect(user="username", password="password", db_url=EAGLE_DB_URL)
rows = execute_query(con, "SELECT TOP 5 * FROM Some.Schema.Table")

# Option 2: OOP Clients
from virgo_db_sql import EagleClient, MillenniumClient, MilliMilClient

eagle = EagleClient("username", "password")
rows = eagle.execute_query("SELECT TOP 5 * FROM Some.Schema.Table")

mill = MillenniumClient("username", "password")
docs = mill.fetch_docs("Some.Schema.Table")
```

## Environment Variables & Security

- You can configure credentials via env vars (priority: explicit args > env vars > prompt):
  - `VIRGO_DB_USER`: username
  - `VIRGO_DB_PASSWORD`: password
  - `VIRGO_DB_URL`: optional, override default endpoint
- Security tips:
  - Use HTTPS only; avoid printing env vars in logs/errors.
  - Enable secret masking in CI/CD; prefer Secrets (K8s/Docker) over plain envs.
  - The client attempts to remove `VIRGO_DB_PASSWORD` from the process env after reading it.

An example template is provided at `examples/env.example`:
```
VIRGO_DB_USER=your_username
VIRGO_DB_PASSWORD=your_password
# VIRGO_DB_URL=https://virgodb.cosma.dur.ac.uk:8443/Eagle
```