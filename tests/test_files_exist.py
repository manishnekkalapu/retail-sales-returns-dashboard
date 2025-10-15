import os
import io
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_sample_csv_exists_and_has_rows():
    path = os.path.join(REPO_ROOT, "data", "sample_sales.csv")
    assert os.path.exists(path), f"Missing sample CSV at {path}"
    df = pd.read_csv(path)
    assert len(df) > 0, "sample_sales.csv exists but has 0 rows"

def test_etl_and_queries_exist_and_nonempty():
    etl_path = os.path.join(REPO_ROOT, "etl.py")
    sql_path = os.path.join(REPO_ROOT, "queries.sql")
    assert os.path.exists(etl_path), "etl.py is missing"
    assert os.path.getsize(etl_path) > 10, "etl.py looks empty"
    assert os.path.exists(sql_path), "queries.sql is missing"
    assert os.path.getsize(sql_path) > 10, "queries.sql looks empty"

def test_basic_dependencies_import():
    # quick import checks so CI will fail early if deps missing
    try:
        import pandas  # noqa: F401
        import sqlite3  # noqa: F401
    except Exception as e:
        raise AssertionError(f"Required dependency import failed: {e}")
