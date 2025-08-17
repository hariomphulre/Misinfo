"""
Advanced Social Media Data Collector
Supports multiple platforms with specialized extraction methods
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://misinformation-collector-zda54hwita-el.a.run.app")

class SocialMediaCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def send_to_backend(self, data, source_type="social_scraper"):
        """Send collected data to backend"""
        try:
            payload = {
                "source": source_type,
                "type": data.get("type", "social_post"),
                "content_text": data.get("content", ""),
                "metadata": json.dumps(data.get("metadata", {}))
            }
            
            response = requests.post(f"{API_BASE_URL}/collect", data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Data sent to backend successfully: {result.get('doc_id')}")
                return result
            else:
                logger.error(f"Failed to send to backend: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending to backend: {e}")
            return None

    def collect_news_articles(self, url):
        """Collect news article content"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # This is a simplified example - you'd want to use proper HTML parsing
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article content
            article_data = {
                "type": "news_article",
                "content": "",
                "metadata": {
                    "url": url,
                    "title": "",
                    "author": "",
                    "publication_date": "",
                    "source_domain": url.split('/')[2] if '/' in url else "",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Try different selectors for title
            title_selectors = ['h1', '.headline', '.article-title', '[data-testid="headline"]']
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    article_data["metadata"]["title"] = title_element.get_text().strip()
                    break
            
            # Try different selectors for article content
            content_selectors = ['article', '.article-content', '.post-content', '.entry-content', 'main']
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    article_data["content"] = content_element.get_text().strip()
                    break
            
            # Extract author
            author_selectors = ['.author', '.byline', '[rel="author"]', '.article-author']
            for selector in author_selectors:
                author_element = soup.select_one(selector)
                if author_element:
                    article_data["metadata"]["author"] = author_element.get_text().strip()
                    break
            
            # Extract publication date
            date_selectors = ['time', '.date', '.publish-date', '[datetime]']
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    article_data["metadata"]["publication_date"] = (
                        date_element.get('datetime') or date_element.get_text().strip()
                    )
                    break
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error collecting news article: {e}")
            return None

    def collect_public_social_content(self, platform, search_terms=None):
        """
        Collect publicly available social media content
        Note: This is a template - actual implementation would depend on platform APIs
        """
        
        if platform.lower() == "reddit":
            return self._collect_reddit_content(search_terms)
        elif platform.lower() == "news_aggregator":
            return self._collect_news_aggregator_content(search_terms)
        else:
            logger.warning(f"Platform {platform} not implemented yet")
            return None

    def _collect_reddit_content(self, search_terms):
        """Collect Reddit posts related to misinformation topics"""
        try:
            # Use Reddit's JSON API (public, no auth needed for reading)
            reddit_url = f"https://www.reddit.com/search.json?q={search_terms}&sort=relevance&limit=25"
            
            response = self.session.get(reddit_url)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                reddit_post = {
                    "type": "reddit_post",
                    "content": f"{post_data.get('title', '')} {post_data.get('selftext', '')}",
                    "metadata": {
                        "platform": "reddit",
                        "post_id": post_data.get('id'),
                        "subreddit": post_data.get('subreddit'),
                        "author": post_data.get('author'),
                        "score": post_data.get('score'),
                        "num_comments": post_data.get('num_comments'),
                        "created_utc": post_data.get('created_utc'),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                posts.append(reddit_post)
                
                # Send to backend
                self.send_to_backend(reddit_post, "reddit_scraper")
            
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting Reddit content: {e}")
            return None

    def _collect_news_aggregator_content(self, search_terms):
        """Collect news articles from various sources"""
        # This would use news APIs like NewsAPI, Google News API, etc.
        # For demo purposes, we'll create a template
        
        news_sources = [
            "https://newsapi.org/v2/everything",  # Requires API key
            # Add more news sources
        ]
        
        # Implementation would depend on specific news APIs
        logger.info(f"News aggregator collection for '{search_terms}' - implementation needed")
        return None

def main():
    """Example usage of the Social Media Collector"""
    collector = SocialMediaCollector()
    
    # Example: Collect news article
    news_url = "https://example-news-site.com/article"
    # article = collector.collect_news_articles(news_url)
    
    # Example: Collect Reddit posts about misinformation
    # reddit_posts = collector.collect_public_social_content("reddit", "misinformation OR fake news")
    
    # Example: Collect from news aggregator
    # news_posts = collector.collect_public_social_content("news_aggregator", "conspiracy theories")
    
    print("Social Media Collector initialized. Use specific methods to collect data.")

if __name__ == "__main__":
    main()
