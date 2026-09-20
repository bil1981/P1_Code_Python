import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# CHEMINS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "credit_risk.db"
LOG_DIR = PROJECT_ROOT / "logs"
REFERENCE_PATH = LOG_DIR / "reference_data.csv"


# ============================================================
# CREATION DU DATASET DE REFERENCE
# ============================================================

def create_reference_data():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Base SQLite introuvable : {DB_PATH}"
        )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DB_PATH)

    try:

        df = pd.read_sql_query(
            "SELECT * FROM client_features",
            conn,
        )

    finally:

        conn.close()

    if df.empty:
        raise ValueError(
            "La table client_features est vide."
        )

    # Colonnes techniques / résultat à exclure
    columns_to_remove = [
        "SK_ID_CURR",
        "TARGET",
        "DECISION",
    ]

    df_reference = df.drop(
        columns=columns_to_remove,
        errors="ignore",
    )

    df_reference.to_csv(
        REFERENCE_PATH,
        index=False,
    )

    print("=" * 50)
    print("REFERENCE DATA CREE")
    print("=" * 50)
    print(f"Lignes      : {len(df_reference)}")
    print(f"Colonnes    : {len(df_reference.columns)}")
    print(f"Fichier     : {REFERENCE_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    create_reference_data()