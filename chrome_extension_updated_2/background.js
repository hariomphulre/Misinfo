// Configuration - Update this URL to your actual API endpoint
const API_BASE_URL = "https://misinformation-collector-322893934340.asia-south1.run.app";

chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: extractContent,
    args: [API_BASE_URL] // Pass the URL as argument
  });
});

function extractContent(apiUrl) {
  try {
    const content = document.body.innerText;
    const url = window.location.href;
    const title = document.title || "No title";
    
    // Basic content validation
    if (!content || content.trim().length === 0) {
      console.warn("No content found on this page");
      return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append("source", "chrome_extension");
    formData.append("type", "text");
    formData.append("content_text", content.trim());
    formData.append("metadata", JSON.stringify({ 
      url: url,
      timestamp: new Date().toISOString(),
      title: title
    }));
    
    // Send data to backend using form data
    fetch(`${apiUrl}/collect`, {
      method: "POST",
      body: formData // Use FormData instead of JSON
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log("Data sent successfully:", data);
      // You could show a notification here
    })
    .catch(error => {
      console.error("Error sending data:", error);
    });
    
  } catch (error) {
    console.error("Error extracting content:", error);
  }
}
