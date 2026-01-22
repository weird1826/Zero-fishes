# ML-Powered Phishing Detection Tool
### Project Summary
Zero-fishes is a DevSecOps and Machine Learning project designed to detect intent in emails in real-time. Unlike traditional signature-based detection, this system uses Natural Language Processing (NLP) to identify phishing patterns in the text itself.
The system consists of a REST API hosted on Render and a Chrome Extension for client-side analysis. To prevent the misuse of API endpoint, the connection between the endpoint and client is secured using a secure API key.

Architecture
---
A Naive Bayes classifier trained on phishing datasets using  scikit-learn  and TD-IDF vectorization.

### NLP Pipeline
The NLP pipeline used consists of three main concepts:
1.	TF-IDF – Method to convert text into numbers (feature extraction).
2.	Naive Bayes – Family of algorithms for classification.
3.	MultinomialNB – Version of Naïve Bayes designed for text data.

**TF-IDF (Term Frequency – Inverse Document Frequency)**

If a document written in English language is analysed, it is often the case that words like “the” or “is” dominate the word count, while important words like “quantum” or “recipe” are left out. TF-IDF balances this count by penalizing words that appear everywhere. It gives a high score to words that are frequent in the current document but rare across all other documents. It produces two metrics:
* TF: Term Frequency – Measure of how often does word t appear in document d?

  `TF(t, d) = (count of t in d) / (total words in d)`
  
  Note: This measures local importance.
* IDF: Inverse Document Frequency – How rare is word t across the entire set of documents?

  `IDF(t) = log[ (Total number of documents) / (Number of documents containing t) ]`

  Note: This measures global rarity. If a word appears in every document, the ratio is 1 and the log(1) is 0. The word effectively gets a score of 0.

The result is a vector where a word like “the” has a score near 0, while specific topic words like “GPU” and “lasagna” have high scores.

**Naïve Bayes**

Naïve Bayes is a probabilistic classifier based on Bayes’ Theorem. It calculates the probability that a data point belongs to a category A given some observed features B.

`P(A|B) = [P(B|A) . P(A) ] / P(B)]`
* P(A|B): Probability of the class given the data (Posterior).
* P(B|A): Probability of the data appearing the class (Likelihood).
* P(A): Initial probability of the class (Prior).
* P(B): Probability of the data occurring at all (Evidence).

The algorithm is called naive because it assumes that all features are independent of each other. For example, it assumes that the word “Artificial” has no relationship to the word “Intelligence”. While in reality, these words are highly correlated. Despite being naïve and technically incorrect subject to a human’s perspective, this assumption simplifies the math incredibly by allowing to just multiply probabilities together and works surprisingly well for text classification.

**MultinomialNB**

Naïve Bayes is a family of algorithms. The difference between them is how they calculate the Likelihood. For instance, Gaussian Naïve Bayes assumes data follows a bell curve (good for height, weight, or temperature); Bernoulli Naïve Bayes assumes data is binary (word is present/absent); Multinomial Naïve Bayes assumes data follows a multinomial distribution such as rolling a die with thousands of sides.
MultinomialNB is specifically designed for discrete counts. In text analysis, a document is treated as a bag of words. For instance, in case of a movie review, MultinomialNB looks at the counts/weights or the words like “bad”, “boring”, “acting”, and then calculates the probability of observing those specific word counts given the review is Negative vs Positive.

**All together**

While MultinomialNB technically expects integer counts, it works well with TF-IDF scores. The algorithm treats the TF-IDF weights as if they were weighted counts, allowing it to pay more attention to the important words and ignore the common ones.

### API & Hosting
A high-performance FastAPI application has been developed serving the model. The app is deployable on Azure via GitHub Actions or any other web service hosting provider for automated deployment.

### Client
A custom Chrome Extension that extracts DOM content and queries the API securely using the API key.

### Technology Stack
* Languages: Python, Shell
* ML Libraries: Scikit-Learn, Pandas, Numpy, Joblib
* Web Framework: FastAPI, Uvicorn
* Cloud: Azure Web Apps
* Security: API Key Authentication, Input Validation using Pydantic
* Frontend: JavaScript, Manifest V3

Security Governance
---
**API Security**: Endpoints are protected via header-based API key auth.

**Data Privacy**: No email data is stored; text is processed in memory and discarded immediately.

**CI/CD**: Automated build pipelines ensure code quality checks before deployment.

Hosting & Developing Your Own Extension
---
To use this API, you need to first host it on a web service provider. Once you set up, you'll get a URL which you have to specify in the environment variables of that application.
You also need to specify your own secure API key to make the use of this extension private.

To build a client-side extension, create folder e.g, `extensions`. Then create three files: `manifest.json`, `popup.html`, `popup.js`. Paste this in your `manifest.json`:
```JSON
{
  "manifest_version": 3,
  "name": "AI Phishing Detector",
  "version": "1.0",
  "description": "Detects phishing attempts using Azure AI.",
  "permissions": ["activeTab", "scripting"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icon.png", 
      "48": "icon.png",
      "128": "icon.png"
    }
  },
  "icons": {
    "16": "icon.png",
    "48": "icon.png",
    "128": "icon.png"
  }
}
```
Make sure that you use your own custom icon and place in the same `extension/` directory. Paste this code in `popup.html`:
```HTML
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 320px; padding: 20px; font-family: 'Segoe UI', sans-serif; text-align: center; }
    h2 { margin: 0 0 15px 0; color: #333; font-size: 18px; }
    button { 
      width: 100%; padding: 12px; background-color: #0078D4; 
      color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;
    }
    button:hover { background-color: #005a9e; }
    #result { margin-top: 20px; padding: 15px; border-radius: 5px; display: none; font-weight: bold; }
    .safe { background-color: #dff6dd; color: #107c10; border: 1px solid #107c10; }
    .phishing { background-color: #fde7e9; color: #a80000; border: 1px solid #a80000; }
    .loader { color: #666; font-size: 12px; margin-top: 10px; }
  </style>
</head>
<body>
  <h2>Zero-fishes</h2>
  <p style="font-size: 12px; color: #666; margin-bottom: 20px;">
    Open an email and click scan to analyze the content using the tool.
  </p>
  <button id="scanBtn">SCAN CURRENT PAGE</button>
  <div id="result"></div>
  <script src="popup.js"></script>
</body>
</html>
```
`popup.js` is the file which initiates the communication. Here is the boiler code for it:
```JS
document.getElementById('scanBtn').addEventListener('click', async () => {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('scanBtn');
    
    // UI Loading State
    btn.disabled = true;
    btn.innerText = "Extracting Text...";
    resultDiv.style.display = 'none';

    try {
        // Get the current active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Execute script to grab text from the page
        const extraction = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body.innerText // This runs inside the web page
        });

        const pageText = extraction[0].result;
        
        // Truncate text to first 2000 chars to save bandwidth/speed
        const textToAnalyze = pageText.substring(0, 2000); 

        btn.innerText = "Analyzing with AI...";

        // Send this to API
        const response = await fetch('<THE API ENDPOINT URL>/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': "<YOUR OWN CUSTOM API KEY>"
            },
            body: JSON.stringify({ text: textToAnalyze })
        });

        const data = await response.json();

        // Show Result
        resultDiv.style.display = 'block';
        if (data.is_phishing) {
            resultDiv.textContent = `PHISHING DETECTED (${(data.confidence * 100).toFixed(1)}%)`;
            resultDiv.className = 'phishing';
        } else {
            resultDiv.textContent = `Page Looks Safe (${(data.confidence * 100).toFixed(1)}%)`;
            resultDiv.className = 'safe';
        }

    } catch (error) {
        resultDiv.style.display = 'block';
        resultDiv.textContent = "Error: Could not read page or connect to API.";
        resultDiv.className = '';
        console.error(error);
    }

    btn.disabled = false;
    btn.innerText = "SCAN CURRENT PAGE";
});
```
### END OF DOCUMENT
