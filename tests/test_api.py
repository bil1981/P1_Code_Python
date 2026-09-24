from api import app

def test_app_exists():
    assert app is not None # vérifie probablement que l application FastAPI existe bien
    assert app.title == "Credit Risk API" # 

def test_predict_endpoint_returns_valid_response(client):
    payload = {"SK_ID_CURR": 100001, "features": {"AMT_INCOME_TOTAL": 135000, "AMT_CREDIT": 568800, "AMT_ANNUITY": 20500, "DAYS_BIRTH": -12000, "DAYS_EMPLOYED": -2000}}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200 # vérifie l'endpoint /predict et que la requête valide vers /predict retourne une réponse correcte
    data = response.json()
    assert data["SK_ID_CURR"] == 100001
    assert isinstance(data["probability"], float)
    assert 0.0 <= data["probability"] <= 1.0
    assert data["decision"] in {"APPROVED", "REFUSED"}

def test_predict_requires_sk_id_curr(client):
    # vérifie que sk_id_curr est obligatoire
    assert client.post("/predict", json={"features": {}}).status_code == 422

def test_predict_response_contains_expected_fields(client):
    # vérifie que la réponse de l API contient bien les champs attendus
    response = client.post("/predict", json={"SK_ID_CURR": 100001, "features": {}})
    assert response.status_code == 200
    assert set(response.json()) == {"SK_ID_CURR", "probability", "decision"}

def test_predict_rejects_invalid_sk_id_curr_type(client):
    # vérifie que l'API refuse un mauvais type pour sk_id_curr, ex.  "sk_id_curr": "bonjour"
    response = client.post("/predict", json={"SK_ID_CURR": "abc", "features": {}})
    assert response.status_code == 422
