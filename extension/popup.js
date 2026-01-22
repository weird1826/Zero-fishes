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
        const response = await fetch('https://ml-powered-phishing-api.onrender.com/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': "dvkljwfij248uqiek@#$_$#Feneiiefn"
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