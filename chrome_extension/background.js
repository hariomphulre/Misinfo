// Configuration - Update this URL to your actual API endpoint
const API_BASE_URL = "https://misinformation-collector-322893934340.asia-south1.run.app";

chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: extractAndSendContent
  });
});

async function extractAndSendContent() {
  try {
    const content = document.body.innerText;
    const url = window.location.href;
    const title = document.title || "No title";
    
    // Basic content validation
    if (!content || content.trim().length === 0) {
      console.warn("No content found on this page");
      return;
    }
    
    const indianTime = new Date().toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata"
    });

    // Prepare form data
    const formData = new FormData();
    formData.append("source", "chrome_extension");
    formData.append("type", "text");
    formData.append("content_text", content.trim());
    formData.append("metadata", JSON.stringify({ 
      url: url,
      timestamp: indianTime,
      title: title
    }));
    
    // Send data to backend
    const response = await fetch(`${API_BASE_URL}/collect`, {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Data sent successfully:", data);
    
    // You could show a notification here
    chrome.notifications?.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'Content Collected',
      message: 'Page content collected successfully!'
    });
    
  } catch (error) {
    console.error("Error collecting content:", error);
    chrome.notifications?.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'Collection Failed',
      message: `Error: ${error.message}`
    });
  }
}
