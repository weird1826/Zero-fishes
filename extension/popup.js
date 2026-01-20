document.getElementById('scanBtn').addEventListener('click', async () => {
    const resultDiv = document.getElementById('result');
    const btn = document.getElementById('scanBtn');
    
    // UI Loading State
    btn.disabled = true;
    btn.innerText = "Extracting Text...";
    resultDiv.style.display = 'none';

    try {
        // 1. Get the current active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // 2. Execute script to grab text from the page
        const extraction = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body.innerText // This runs inside the web page
        });

        const pageText = extraction[0].result;
        
        // Truncate text to first 2000 chars to save bandwidth/speed
        const textToAnalyze = pageText.substring(0, 2000); 

        btn.innerText = "Analyzing with AI...";

        // 3. Send to your Azure API
        // REPLACE with your actual URL
        const response = await fetch('https://YOUR-APP-NAME.azurewebsites.net/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': 'my-secret-student-key-123'
            },
            body: JSON.stringify({ text: textToAnalyze })
        });

        const data = await response.json();

        // 4. Show Result
        resultDiv.style.display = 'block';
        if (data.is_phishing) {
            resultDiv.textContent = `🚨 PHISHING DETECTED (${(data.confidence * 100).toFixed(1)}%)`;
            resultDiv.className = 'phishing';
        } else {
            resultDiv.textContent = `✅ Page Looks Safe (${(data.confidence * 100).toFixed(1)}%)`;
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