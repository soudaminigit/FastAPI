# Dockerfile.api

FROM python:3.11-slim

WORKDIR /app

COPY ./main.py .
COPY model.pkl .
COPY features.pkl .
RUN pip install fastapi uvicorn scikit-learn==1.3.2 pydantic

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
