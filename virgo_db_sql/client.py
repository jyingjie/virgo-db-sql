#!/bin/env python

# Client to access the Virgo databases (EAGLE, Millennium, milli-Millennium)
# Based on the original module for the Virgo Consortium

import numpy as np
from urllib.parse import urlencode
from urllib.request import urlopen, HTTPPasswordMgrWithDefaultRealm, \
    OpenerDirector, install_opener, build_opener, HTTPBasicAuthHandler, \
    HTTPCookieProcessor
from http.cookiejar import LWPCookieJar

import re
import os
from getpass import getpass

# Predefined database base URLs (no trailing slash)
EAGLE_DB_URL = "https://virgodb.cosma.dur.ac.uk:8443/Eagle"
MILLENNIUM_DB_URL = "https://virgodb.cosma.dur.ac.uk:8443/MyMillennium"
MILLIMIL_DB_URL = "https://virgodb.cosma.dur.ac.uk:8443/Millennium"

# Mapping between SQL and numpy types
numpy_dtype = {
    b"real"     : np.float32,
    b"float"    : np.float64,
    b"int"      : np.int32,
    b"bigint"   : np.int64,
    b"char"     : np.dtype("|S256"),
    b"nvarchar" : np.dtype("|S256")
}

# Cookie storage - want to avoid creating a new session for every query
cookie_file = "sql_cookies.txt"
cookie_jar = LWPCookieJar(cookie_file)
try:
    cookie_jar.load(ignore_discard=True)
except IOError:
    pass


class VirgoDBClient:
    def __init__(self, username, password=None, db_url=None):
        """Base client to connect and interact with Virgo web databases."""
        # Resolve credentials and endpoint: explicit args > env vars > prompt/default
        if username is None:
            username = os.getenv("VIRGO_DB_USER")
        if password is None:
            password = os.getenv("VIRGO_DB_PASSWORD")
        resolved_db_url = db_url or os.getenv("VIRGO_DB_URL") or EAGLE_DB_URL
        if password is None:
            password = getpass()
        self.db_url = resolved_db_url
        # For docs path construction (e.g., Eagle, MyMillennium, Millennium)
        self._docs_db_name = self.db_url.rstrip('/').split('/')[-1]
        # Set up authentication and cookies
        self.password_mgr = HTTPPasswordMgrWithDefaultRealm()
        self.password_mgr.add_password(None, self.db_url, username, password)
        self.opener = OpenerDirector()
        self.auth_handler   = HTTPBasicAuthHandler(self.password_mgr)
        self.cookie_handler = HTTPCookieProcessor(cookie_jar)
        # Optional: reduce accidental leakage by clearing password env var
        try:
            os.environ.pop("VIRGO_DB_PASSWORD", None)
        except Exception:
            pass

    def execute_query(self, sql):
        """Run an SQL query and return the result as a record array"""
        url = self.db_url.rstrip('/') + "/?" + urlencode({'action': 'doQuery', 'SQL': sql})
        install_opener(build_opener(self.auth_handler, self.cookie_handler))
        response = urlopen(url)
        cookie_jar.save(ignore_discard=True)

        # Check for OK response
        line = response.readline()
        if bytes(line) != b"#OK\n":
            raise Exception(response.readlines())

        # Skip rows until we reach QUERYTIMEOUT
        while True:
            line = bytes(response.readline())
            if line == b"":
                raise Exception("Unexpected end of file while reading result"
                                "header")
            elif line.startswith(b"#QUERYTIMEOUT"):
                break

        # Skip QUERYTIME
        if not(bytes(response.readline()).startswith(b"#QUERYTIME")):
            raise Exception("Don't understand result header!")

        # Read column info
        # (also discards line with full list of column names)
        columns = []
        while True:
            line = bytes(response.readline())
            if not line.startswith(b"#"):
                break
            else:
                m = re.match(br"^#COLUMN ([0-9]+) name=([\w]+) "
                             br"JDBC_TYPE=(-?[0-9]+) JDBC_TYPENAME=([\w]+)\n$",
                             line)
                if m is not None:
                    columns.append(m.groups())
                else:
                    raise Exception("Don't understand column info: "+line)

        # Construct record type for the output
        types = [numpy_dtype[col[3]] for col in columns]
        try:
            names = [col[1] for col in columns]
            dtype = np.dtype([(n, t) for n, t in zip(names, types)])
        except TypeError:
            names = [col[1].decode() for col in columns]
            dtype = np.dtype([(n, t) for n, t in zip(names, types)])

        # Return the data as a record array
        return np.genfromtxt(response, dtype=dtype, delimiter=",")

    def fetch_docs(self, table):
        """Return the documentation page bytes for the specified table."""
        url = self.db_url.rstrip('/') + "/Help?" + urlencode(
            {'page': "databases/" + self._docs_db_name + "/" + table}
        )
        install_opener(build_opener(self.auth_handler, self.cookie_handler))
        response = urlopen(url)
        cookie_jar.save(ignore_discard=True)
        return response.readlines()


class EagleClient(VirgoDBClient):
    def __init__(self, username, password=None, db_url=EAGLE_DB_URL):
        super().__init__(username=username, password=password, db_url=db_url)


class MillenniumClient(VirgoDBClient):
    def __init__(self, username, password=None, db_url=MILLENNIUM_DB_URL):
        super().__init__(username=username, password=password, db_url=db_url)


class MilliMilClient(VirgoDBClient):
    def __init__(self, username, password=None, db_url=MILLIMIL_DB_URL):
        super().__init__(username=username, password=password, db_url=db_url)


def connect(user, password=None, db_url=None):
    """Backwards-compatible helper to create a generic client.

    Returns a VirgoDBClient with optional db_url override.
    """
    return VirgoDBClient(user, password, db_url)


def execute_query(con, sql):
    return con.execute_query(sql)
