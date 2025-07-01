from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib, torch
from torchvision import transforms
from PIL import Image
import io
import uvicorn
import pandas as pd

app = FastAPI(title="ML/DL Inference API")

# ========== Load Models ==========
ml_model = joblib.load("models/price_model.pkl")  # Scikit-learn
dl_model = torch.jit.load("models/resnet_scripted.pt").eval()  # TorchScript

# ========== Request Models ==========
class HouseData(BaseModel):
    rooms: int
    area: float
    location: str

# ========== Level 0: Single URI for all ==========
@app.post("/infer")  # Not RESTful (Level 0)
async def single_entry_point(model_type: str, data: dict):
    if model_type == "ml":
        result = ml_model.predict([[data["rooms"], data["area"], data["location"]]])
        return {"price": result[0]}
    elif model_type == "dl":
        return {"msg": "Use /predict/image endpoint instead"}
    else:
        raise HTTPException(400, "Invalid model type")

# ========== Level 1: Separate URI ==========
@app.post("/predict/price")  # ML model inference
async def predict_price(payload: HouseData):
    df = pd.DataFrame([{
        "rooms": payload.rooms,
        "area": payload.area,
        "location": payload.location
    }])

    # Predict using the model pipeline
    pred = ml_model.predict(df)[0]
    return {
        "prediction": pred,
        "_links": {
            "self": "/predict/price",
            "model_info": "/model/ml"
        }
    }

# ========== Level 2: Use HTTP Verbs ==========
@app.get("/model/ml")
def get_ml_model_info():
    return {
        "name": "LinearRegressor",
        "framework": "scikit-learn",
        "_links": {"predict": "/predict/price"}
    }

@app.get("/model/dl")
def get_dl_model_info():
    return {
        "name": "ResNet50",
        "framework": "PyTorch",
        "_links": {"predict": "/predict/image"}
    }

# ========== Level 3: DL Image Classifier with HATEOAS ==========
@app.post("/predict/image")
async def classify_image(file: UploadFile = File(...)):
    try:
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        input_tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            output = dl_model(input_tensor)
            pred_idx = output.argmax().item()

        return {
            "prediction": f"class_{pred_idx}",
            "_links": {
                "self": "/predict/image",
                "model_info": "/model/dl"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image error: {str(e)}")

if __name__ == "__main__":
   
    uvicorn.run("model_serve:app", host="127.0.0.1", port=8000, reload=True)
