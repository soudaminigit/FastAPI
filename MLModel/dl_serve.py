# ml_model_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image
import io
import json
import requests

app = FastAPI()

# ---- Load TorchScripted model ----
model = torch.jit.load("resnet_scripted.pt", map_location="cpu")
model.eval()

# ---- Load ImageNet class labels ----
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
imagenet_classes = requests.get(LABELS_URL).text.strip().split("\n")

# ---- Preprocessing for ResNet ----
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # as per ImageNet
        std=[0.229, 0.224, 0.225]
    )
])

# ---- Prediction Route ----
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)  # Shape: [1, 3, 224, 224]

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        top1_prob, top1_class = torch.max(probs, dim=0)
        class_name = imagenet_classes[top1_class.item()]
    
    return JSONResponse({
        "prediction": class_name,
        "confidence": round(top1_prob.item(), 3)
    })
