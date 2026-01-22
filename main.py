"""
Web App source file
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

# Grab API key from environment
API_KEY = os.environ['API_KEY']

# Verify API Key Header
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

# Initializing the app
app = FastAPI(title="Zero-fishes")

app.add_middleware(
    CORSMiddleware,                     # Required so the browser can allow the extension to send request to web server
    allow_origins=["*"],                # Replace "*" with specific origin(s) of your choice
    allow_credentials=True,
    allow_methods=["GET", "POST"],      # GET, POST, etc.
    allow_headers=["*"],                # Allow any headers
)

# Embedding the model
# Loading the model globally for efficiency
try:
    model = joblib.load('./models/phishing_model.pkl')
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model file not found. Run train_model.py")
    model = None

# Data structure for incoming request
# Pydantic ensures that whoever sends data sends it in the correct format.
class EmailRequest(BaseModel):
    text: str

# Prediction Endpoint
@app.post("/predict")
def predict_email(email: EmailRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    # predict() returns an array - extract the first item
    prediction_value = model.predict([email.text])[0]
    
    # Calculate confidence if the model supports it
    # predict_proba() returns probabilities for [Safe, Phishing]
    probabilities = model.predict_proba([email.text])[0]
    confidence = max(probabilities) # Take the highest probability
    
    # Convert 0/1 to human readable label
    label = "Phishing" if prediction_value == 1 else "Safe"
    
    return {
        "prediction": label,
        "confidence": float(confidence),
        "is_phishing": bool(prediction_value == 1)
    }

# Root Endpoint - Health Check
@app.get("/")
def read_root():
    return {"status": "API is online", "model_loaded": model is not None}