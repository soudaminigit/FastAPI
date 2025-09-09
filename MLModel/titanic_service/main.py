# main.py

from fastapi import FastAPI
from pydantic import BaseModel
import pickle

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("features.pkl", "rb") as f:
    features = pickle.load(f)

app = FastAPI()

class Passenger(BaseModel):
    Pclass: int
    Sex: int  # 0=female, 1=male
    Age: float
    SibSp: int
    Parch: int
    Fare: float

@app.post("/predict")
def predict(p: Passenger):
    X = [[p.Pclass, p.Sex, p.Age, p.SibSp, p.Parch, p.Fare]]
    y_pred = model.predict(X)[0]
    return {"survived": int(y_pred)}
