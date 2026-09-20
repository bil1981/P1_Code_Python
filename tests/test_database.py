import sqlite3
from pathlib import Path
import pytest

def get_database_path():
    for path in (Path("credit_risk.db"), Path("data/credit_risk.db")):
        if path.exists(): return path
    return None

@pytest.fixture
def db_connection():
    path = get_database_path()
    if path is None: pytest.skip("credit_risk.db introuvable")
    conn = sqlite3.connect(path)
    try: yield conn
    finally: conn.close()

def table_exists(conn, name):
    return conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()

def columns(conn, name):
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{name}")')}

def test_predictions_table_exists(db_connection): assert table_exists(db_connection, "predictions") is not None
def test_client_features_table_exists(db_connection): assert table_exists(db_connection, "client_features") is not None
def test_feature_importance_table_exists(db_connection): assert table_exists(db_connection, "feature_importance") is not None
def test_predictions_has_required_columns(db_connection): assert {"SK_ID_CURR", "TARGET", "DECISION"} <= columns(db_connection, "predictions")
def test_client_features_has_sk_id_curr(db_connection): assert "SK_ID_CURR" in columns(db_connection, "client_features")
def test_feature_importance_has_required_columns(db_connection): assert {"feature", "importance"} <= columns(db_connection, "feature_importance")
