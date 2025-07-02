# ml_model_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="ML Inference API")

# Load ML model
ml_model = joblib.load("models/price_model.pkl")  # Ensure path is correct

class HouseData(BaseModel):
    rooms: int
    area: float
    location: str

@app.post("/predict/price")
async def predict_price(payload: HouseData):
    try:
        df = pd.DataFrame([payload.dict()])
        pred = ml_model.predict(df)[0]
        return {
            "prediction": pred,
            "_links": {
                "self": "/predict/price",
                "model_info": "/model/ml"
            }
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Prediction error: {str(e)}")

@app.get("/model/ml")
def get_model_info():
    return {
        "name": "LinearRegressor",
        "framework": "scikit-learn",
        "_links": {"predict": "/predict/price"}
    }

# To run:
# uvicorn ml_model_service:app --port 8001 --reload

