from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


# ============================================================
# CHEMINS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_PATH = PROJECT_ROOT / "logs" / "reference_data.csv"
PRODUCTION_PATH = PROJECT_ROOT / "logs" / "production_data.csv"

REPORT_PATH = PROJECT_ROOT / "monitoring_report.html"


# ============================================================
# VERIFICATIONS
# ============================================================

if not REFERENCE_PATH.exists():
    raise FileNotFoundError(
        f"Fichier de référence introuvable : {REFERENCE_PATH}"
    )

if not PRODUCTION_PATH.exists():
    raise FileNotFoundError(
        f"Fichier production introuvable : {PRODUCTION_PATH}"
    )


# ============================================================
# CHARGEMENT
# ============================================================

reference = pd.read_csv(REFERENCE_PATH)
production = pd.read_csv(PRODUCTION_PATH)

print("=" * 60)
print("EVIDENTLY MONITORING")
print("=" * 60)

print(
    f"Données référence  : {len(reference)} lignes"
)

print(
    f"Données production : {len(production)} lignes"
)


# ============================================================
# COLONNES A EXCLURE DU DATA DRIFT
# ============================================================

excluded_columns = {
    "timestamp",
    "SK_ID_CURR",
    "TARGET",
    "DECISION",
    "probability",
    "decision",
    "latency_ms",
    "status",
}


# ============================================================
# FEATURES COMMUNES
# ============================================================

features = [
    column
    for column in reference.columns
    if (
        column in production.columns
        and column not in excluded_columns
    )
]


if not features:
    raise ValueError(
        "Aucune feature commune trouvée entre "
        "reference_data.csv et production_data.csv."
    )


print()
print(
    f"Nombre de features surveillées : "
    f"{len(features)}"
)

print()
print("Features surveillées :")

for feature in features[:20]:
    print(f"  - {feature}")

if len(features) > 20:
    print(
        f"  ... et {len(features) - 20} autres"
    )


# ============================================================
# DATASETS POUR EVIDENTLY
# ============================================================

reference_monitoring = reference[
    features
].copy()

production_monitoring = production[
    features
].copy()

# ============================================================
# PREPARATION DES DONNEES POUR EVIDENTLY
# ============================================================

reference_monitoring = reference[
    features
].copy()

production_monitoring = production[
    features
].copy()


# ============================================================
# SUPPRESSION DES COLONNES VIDES EN PRODUCTION
# ============================================================

valid_features = []

ignored_features = []

for column in features:

    # Nombre de valeurs non nulles en production
    production_non_null = (
        production_monitoring[column]
        .notna()
        .sum()
    )

    # Si aucune donnée exploitable en production,
    # Evidently ne peut pas calculer le drift.
    if production_non_null == 0:

        ignored_features.append(column)

    else:

        valid_features.append(column)


# Garder uniquement les variables exploitables
reference_monitoring = reference_monitoring[
    valid_features
].copy()

production_monitoring = production_monitoring[
    valid_features
].copy()


print()
print(
    f"Features utilisées pour Evidently : "
    f"{len(valid_features)}"
)

print(
    f"Features ignorées car vides en production : "
    f"{len(ignored_features)}"
)

if ignored_features:

    print()
    print("Quelques features ignorées :")

    for feature in ignored_features[:20]:
        print(f"  - {feature}")

    if len(ignored_features) > 20:
        print(
            f"  ... et "
            f"{len(ignored_features) - 20} autres"
        )

# ============================================================
# RAPPORT EVIDENTLY
# ============================================================

print()
print("Génération du rapport Evidently...")

report = Report(
    [
        DataDriftPreset()
    ]
)

result = report.run(
    production_monitoring,
    reference_monitoring,
)


# ============================================================
# SAUVEGARDE
# ============================================================

result.save_html(
    str(REPORT_PATH)
)


# ============================================================
# METRIQUES PRODUCTION
# ============================================================

print()
print("-" * 60)
print("METRIQUES PRODUCTION")
print("-" * 60)


request_count = len(production)

print(
    f"Nombre de prédictions : "
    f"{request_count}"
)


# ------------------------------------------------------------
# ERREURS
# ------------------------------------------------------------

if "status" in production.columns:

    errors = (
        pd.to_numeric(
            production["status"],
            errors="coerce",
        ) >= 400
    ).sum()

    error_rate = (
        errors / request_count * 100
        if request_count > 0
        else 0
    )

    print(
        f"Erreurs              : {errors}"
    )

    print(
        f"Taux d'erreur        : "
        f"{error_rate:.2f} %"
    )


# ------------------------------------------------------------
# LATENCE
# ------------------------------------------------------------

if "latency_ms" in production.columns:

    latency = pd.to_numeric(
        production["latency_ms"],
        errors="coerce",
    )

    mean_latency = latency.mean()
    p95_latency = latency.quantile(0.95)

    print(
        f"Latence moyenne      : "
        f"{mean_latency:.2f} ms"
    )

    print(
        f"Latence P95          : "
        f"{p95_latency:.2f} ms"
    )


# ------------------------------------------------------------
# PROBABILITE
# ------------------------------------------------------------

if "probability" in production.columns:

    probability = pd.to_numeric(
        production["probability"],
        errors="coerce",
    )

    print(
        f"Probabilité moyenne  : "
        f"{probability.mean():.4f}"
    )


# ------------------------------------------------------------
# DECISIONS
# ------------------------------------------------------------

if "decision" in production.columns:

    print()
    print("Distribution des décisions :")

    print(
        production["decision"]
        .value_counts()
        .to_string()
    )


# ============================================================
# FIN
# ============================================================

print()
print("=" * 60)
print("RAPPORT EVIDENTLY GENERE")
print("=" * 60)

print(
    f"Fichier : {REPORT_PATH}"
)

print("=" * 60)