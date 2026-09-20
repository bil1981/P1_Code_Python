# Tests pytest - Credit Risk

Depuis la racine du projet :

```bash
pip install -r tests/requirements-test.txt
pytest -v
```

API uniquement :

```bash
pytest tests/test_main.py -v
```

Logique de prédiction :

```bash
pytest tests/test_prediction_logic.py -v
```

Base SQLite :

```bash
pytest tests/test_database.py -v
```

Le modèle `models/lightgbm_model.txt` doit être présent pour les tests API.
La base `credit_risk.db` doit être présente pour les tests SQLite.
