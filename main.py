from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib

# 1. Initialize the App
app = FastAPI(title="Phishing Detector API")

# 2. Load the Model (The "Brain")
# We load this globally so we don't have to reload it for every single request (Efficiency!)
try:
    model = joblib.load('./models/phishing_model.pkl')
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model file not found. Did you run train_model.py?")
    model = None

# 3. Define the Data Structure (Governance)
# Pydantic ensures that whoever sends data sends it in the CORRECT format.
class EmailRequest(BaseModel):
    text: str

# 4. The Prediction Endpoint
@app.post("/predict")
def predict_email(email: EmailRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    # Make the prediction
    # predict() returns an array (e.g., [1]), we take the first item
    prediction_value = model.predict([email.text])[0]
    
    # Calculate confidence (probability) if the model supports it
    # predict_proba() returns probabilities for [Safe, Phishing]
    probabilities = model.predict_proba([email.text])[0]
    confidence = max(probabilities) # Take the highest probability
    
    # Convert 0/1 to human readable label
    label = "Phishing" if prediction_value == 1 else "Safe"
    
    return {
        "prediction": label,
        "confidence": float(confidence), # e.g., 0.98
        "is_phishing": bool(prediction_value == 1)
    }

# 5. A Simple Root Endpoint (Health Check)
@app.get("/")
def read_root():
    return {"status": "API is online", "model_loaded": model is not None}