import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Loading the dataset
# Dataset used in this program has two columns: text, label
print("Loading dataset...")
try:
    data = pd.read_csv('./data/phishing_email.csv')
    
    # Drop null values if any
    data.dropna(inplace=True)
    
    # Column Names
    X = data['text'] 
    y = data['label'] 
except FileNotFoundError:
    print("Error: 'phishing_emails.csv' not found in data/folder.")
    exit()

# Splitting the daata
# Tweak the test size to keep that x% of data hidden to test the model later
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pipeline config
# This bundles the Pre-processing (TF-IDF) and the Model (Naive Bayes) into one object.
# TF-IDF: Converts words into numbers based on how rare/unique they are.
# MultinomialNB: The algorithm that calculates probability of spam.
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('classifier', MultinomialNB())
])

# Train the Model
print("Training the model... (this might take a moment)")
pipeline.fit(X_train, y_train)

# Evaluate
print("Evaluating model...")
predictions = pipeline.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, predictions)}")
print("\nDetailed Report:\n")
print(classification_report(y_test, predictions))

# Save the Model so the API can load it later without retraining.
print("Saving model to 'models/phishing_model.pkl'...")
joblib.dump(pipeline, './phishing_model.pkl')
print("Done! Phase 1 Complete.")