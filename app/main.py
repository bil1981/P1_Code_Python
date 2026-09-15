from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

import joblib
import lightgbm as lgb
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "lightgbm_model.txt"
FEATURE_NAMES_PATH = PROJECT_ROOT / "models" / "feature_names.joblib"
DECISION_THRESHOLD = 0.10


class PredictionRequest(BaseModel):
    SK_ID_CURR: int
    features: Dict[str, Any] = Field(default_factory=dict)


class PredictionResponse(BaseModel):
    SK_ID_CURR: int
    probability: float
    decision: str



# ...existing code...

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Modèle introuvable : {MODEL_PATH}")

    app.state.model = lgb.Booster(model_file=str(MODEL_PATH))

    # Utiliser les noms réellement enregistrés dans le modèle
    app.state.feature_names = list(
        app.state.model.feature_name()
    )

    print(
        f"{len(app.state.feature_names)} variables chargées depuis LightGBM"
    )

    yield


# ...existing code...
# ...existing code...

app = FastAPI(
    title="Credit Risk API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    request: Request,
) -> PredictionResponse:
    model = request.app.state.model
    feature_names = request.app.state.feature_names

    # Données brutes reçues depuis Streamlit
    raw_df = pd.DataFrame([payload.features])

    # Ajouter l'identifiant uniquement si le modèle l'attend
    if "SK_ID_CURR" in feature_names:
        raw_df["SK_ID_CURR"] = payload.SK_ID_CURR

    # Supprimer les colonnes cibles
    raw_df = raw_df.drop(
        columns=["TARGET", "DECISION"],
        errors="ignore",
    )

    # Identifier les variables catégorielles
    categorical_columns = raw_df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    # Même principe que pendant l'entraînement
    encoded_df = pd.get_dummies(
        raw_df,
        columns=categorical_columns,
        dummy_na=False,
    )

    # Ajouter les colonnes manquantes et respecter l'ordre du modèle
    encoded_df = encoded_df.reindex(
        columns=feature_names,
        fill_value=0,
    )

    # Conversion finale en données numériques
    encoded_df = encoded_df.apply(
        pd.to_numeric,
        errors="coerce",
    ).fillna(0)

    # Vérification finale
    if encoded_df.shape[1] != model.num_feature():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Nombre de variables incorrect : "
                f"{encoded_df.shape[1]} reçues, "
                f"{model.num_feature()} attendues."
            ),
        )

    probability = float(model.predict(encoded_df)[0])

    return PredictionResponse(
        SK_ID_CURR=payload.SK_ID_CURR,
        probability=probability,
        decision=(
            "REFUSED"
            if probability >= DECISION_THRESHOLD
            else "APPROVED"
        ),
    )