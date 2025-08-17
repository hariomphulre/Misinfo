// Configuration - Update this URL to your actual API endpoint
const API_BASE_URL = "https://misinformation-collector-zda54hwita-el.a.run.app";

document.addEventListener('DOMContentLoaded', function() {
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
    
    // Extract comprehensive data from the page
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: (collectionType) => {
        const data = {
          url: window.location.href,
          title: document.title || "No title",
          timestamp: new Date().toISOString(),
          domain: window.location.hostname,
          socialPlatform: detectSocialPlatform(window.location.href)
        };

        function detectSocialPlatform(url) {
          if (url.includes('twitter.com') || url.includes('x.com')) return 'twitter';
          if (url.includes('facebook.com')) return 'facebook';
          if (url.includes('instagram.com')) return 'instagram';
          if (url.includes('youtube.com')) return 'youtube';
          if (url.includes('tiktok.com')) return 'tiktok';
          if (url.includes('linkedin.com')) return 'linkedin';
          if (url.includes('reddit.com')) return 'reddit';
          if (url.includes('whatsapp.com')) return 'whatsapp';
          if (url.includes('telegram.org')) return 'telegram';
          return detectNewsWebsite(url);
        }

        function detectNewsWebsite(url) {
          const newsKeywords = ['news', 'cnn', 'bbc', 'reuters', 'ap', 'nytimes', 'guardian', 'fox', 'abc', 'nbc', 'cbs'];
          for (let keyword of newsKeywords) {
            if (url.toLowerCase().includes(keyword)) return 'news';
          }
          return 'general';
        }

        // Collect text content
        if (collectionType === 'text' || collectionType === 'all') {
          data.textContent = document.body.innerText.trim();
          
          // Extract specific social media elements
          if (data.socialPlatform === 'twitter') {
            data.tweets = Array.from(document.querySelectorAll('[data-testid="tweet"]')).map(tweet => ({
              text: tweet.innerText,
              author: tweet.querySelector('[data-testid="User-Name"]')?.innerText || 'Unknown',
              time: tweet.querySelector('time')?.getAttribute('datetime') || ''
            }));
          }
          
          if (data.socialPlatform === 'facebook') {
            data.posts = Array.from(document.querySelectorAll('[data-pagelet="FeedUnit_0"], [data-pagelet^="FeedUnit"]')).map(post => ({
              text: post.innerText,
              author: post.querySelector('[role="link"]')?.innerText || 'Unknown'
            }));
          }

          // Extract article content for news sites
          if (data.socialPlatform === 'news') {
            const articleSelectors = ['article', '.article-content', '.post-content', '.entry-content', 'main'];
            for (let selector of articleSelectors) {
              const article = document.querySelector(selector);
              if (article) {
                data.articleContent = article.innerText.trim();
                data.headline = document.querySelector('h1')?.innerText || data.title;
                break;
              }
            }
          }
        }

        // Collect media content
        if (collectionType === 'media' || collectionType === 'all') {
          data.images = Array.from(document.querySelectorAll('img')).map(img => ({
            src: img.src,
            alt: img.alt || '',
            width: img.width || 0,
            height: img.height || 0
          })).filter(img => img.src && !img.src.includes('data:'));

          data.videos = Array.from(document.querySelectorAll('video')).map(video => ({
            src: video.src || video.currentSrc,
            poster: video.poster || '',
            duration: video.duration || 0
          })).filter(video => video.src);

          // YouTube specific
          if (data.socialPlatform === 'youtube') {
            data.videoId = window.location.href.match(/[?&]v=([^&]+)/)?.[1] || '';
            data.videoTitle = document.querySelector('h1.ytd-video-primary-info-renderer')?.innerText || '';
            data.channelName = document.querySelector('#channel-name a')?.innerText || '';
            data.views = document.querySelector('.view-count')?.innerText || '';
            data.description = document.querySelector('#description')?.innerText || '';
          }
        }

        // Collect links
        if (collectionType === 'links' || collectionType === 'all') {
          data.links = Array.from(document.querySelectorAll('a')).map(link => ({
            href: link.href,
            text: link.innerText.trim(),
            domain: new URL(link.href).hostname
          })).filter(link => link.href && link.href.startsWith('http'));
        }

        // Collect metadata
        if (collectionType === 'all') {
          data.metaTags = Array.from(document.querySelectorAll('meta')).map(meta => ({
            name: meta.name || meta.property || '',
            content: meta.content || ''
          })).filter(meta => meta.name && meta.content);

          data.ogTags = Array.from(document.querySelectorAll('meta[property^="og:"]')).map(meta => ({
            property: meta.property,
            content: meta.content
          }));
        }

        return data;
      },
      args: [type]
    });
    
    const pageData = results[0].result;
    
    // Send comprehensive data to backend
    const formData = new FormData();
    formData.append("source", "chrome_extension_enhanced");
    formData.append("type", type);
    formData.append("content_text", pageData.textContent || '');
    formData.append("metadata", JSON.stringify(pageData));
    
    // Send to backend
    const response = await fetch(`${API_BASE_URL}/collect`, {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Show success with details
    statusDiv.textContent = `✅ ${type} data collected successfully! (${pageData.socialPlatform || 'general'} platform)`;
    statusDiv.className = "success";
    
    // Reset status after delay
    setTimeout(() => {
      statusDiv.textContent = "";
      statusDiv.className = "";
    }, 5000);
    
  } catch (error) {
    console.error("Collection error:", error);
    statusDiv.textContent = `❌ Error: ${error.message}`;
    statusDiv.className = "error";
  } finally {
    // Re-enable all buttons
    buttons.forEach(btn => btn.disabled = false);
  }
}
