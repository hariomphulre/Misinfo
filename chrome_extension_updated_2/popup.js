// Configuration - Update this URL to your actual API endpoint
const API_BASE_URL = "https://misinformation-collector-322893934340.asia-south1.run.app";

document.addEventListener('DOMContentLoaded', function() {
  // Display current API URL for debugging
  document.getElementById("urlDisplay").textContent = `API: ${API_BASE_URL}`;
  
  // Add event listeners for different collection types
  document.getElementById("collectTextBtn").addEventListener("click", () => collectData('text'));
  document.getElementById("collectMediaBtn").addEventListener("click", () => collectData('media'));
  document.getElementById("collectLinksBtn").addEventListener("click", () => collectData('links'));
  document.getElementById("collectAllBtn").addEventListener("click", () => collectData('all'));
});

async function collectData(type) {
  const statusDiv = document.getElementById("status");
  const buttons = document.querySelectorAll("button");
  
  try {
    // Disable all buttons
    buttons.forEach(btn => btn.disabled = true);
    
    statusDiv.textContent = `Collecting ${type} data...`;
    statusDiv.className = "collecting";
    
    // Get current tab
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    
    // Extract basic data from the page
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: (collectionType) => {
        // Simple data extraction
        const data = {
          url: window.location.href,
          title: document.title || "No title",
          timestamp: new Date().toISOString(),
          domain: window.location.hostname
        };

        // Basic content collection
        if (collectionType === 'text' || collectionType === 'all') {
          data.textContent = document.body.innerText.trim();
        }

        if (collectionType === 'media' || collectionType === 'all') {
          data.images = Array.from(document.querySelectorAll('img')).map(img => img.src).filter(src => src && !src.includes('data:'));
          data.videos = Array.from(document.querySelectorAll('video')).map(video => video.src || video.currentSrc).filter(src => src);
        }

        if (collectionType === 'links' || collectionType === 'all') {
          data.links = Array.from(document.querySelectorAll('a')).map(link => link.href).filter(href => href && href.startsWith('http'));
        }

        return data;
      },
      args: [type]
    });
    
    const pageData = results[0].result;
    
    // Send data to backend using form data
    const formData = new FormData();
    formData.append("source", "chrome_extension_v2");
    formData.append("type", type);
    formData.append("content_text", pageData.textContent || '');
    formData.append("metadata", JSON.stringify(pageData));
    
    // Send to backend with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    try {
      const response = await fetch(`${API_BASE_URL}/collect`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
      }
      
      const result = await response.json();
      
      // Show success
      statusDiv.textContent = `Success! ${type} data collected (${pageData.domain})`;
      statusDiv.className = "success";
      
      // Reset status after delay
      setTimeout(() => {
        statusDiv.textContent = "";
        statusDiv.className = "";
      }, 5000);
      
    } catch (fetchError) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        throw new Error('Request timeout - server took too long');
      }
      throw fetchError;
    }
    
  } catch (error) {
    console.error("Collection error:", error);
    
    // Simple error reporting
    let errorMessage = error.message;
    if (error.message.includes("Failed to fetch")) {
      errorMessage = "Network error - check connection";
    } else if (error.message.includes("HTTP error")) {
      errorMessage = `Server error: ${error.message}`;
    }
    
    statusDiv.textContent = `Error: ${errorMessage}`;
    statusDiv.className = "error";
    
  } finally {
    // Re-enable all buttons
    buttons.forEach(btn => btn.disabled = false);
  }
}
