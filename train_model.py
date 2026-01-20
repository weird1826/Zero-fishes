import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Load the Dataset
# We assume the CSV has columns: 'text' (email body) and 'label' (1 for phishing, 0 for safe)
print("Loading dataset...")
try:
    data = pd.read_csv('./../data/phishing_email.csv')
    
    # Check if we have null values and drop them (Governance: Clean data = Safe AI)
    data.dropna(inplace=True)
    
    # Adjust these column names if your CSV is different!
    X = data['text'] 
    y = data['label'] 
except FileNotFoundError:
    print("Error: 'phishing_emails.csv' not found in data/folder.")
    exit()

# 2. Split Data (Governance: Validate before you deploy)
# We keep 20% of data hidden to test the model later
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Create the Pipeline
# This bundles the Pre-processing (TF-IDF) and the Model (Naive Bayes) into one object.
# TF-IDF: Converts words into numbers based on how rare/unique they are.
# MultinomialNB: The algorithm that calculates probability of spam.
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('classifier', MultinomialNB())
])

# 4. Train the Model
print("Training the model... (this might take a moment)")
pipeline.fit(X_train, y_train)

# 5. Evaluate
print("Evaluating model...")
predictions = pipeline.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, predictions)}")
print("\nDetailed Report:\n")
print(classification_report(y_test, predictions))

# 6. Save the Model
# We save this file so our API can load it later without retraining.
print("Saving model to 'models/phishing_model.pkl'...")
joblib.dump(pipeline, './phishing_model.pkl')
print("Done! Phase 1 Complete.")