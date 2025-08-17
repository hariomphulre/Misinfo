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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
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
            # Try multiple approaches for Reddit data collection
            
            # Method 1: Try Reddit's JSON API with better headers
            reddit_url = f"https://www.reddit.com/search.json?q={search_terms}&sort=relevance&limit=25"
            
            # Add additional headers to appear more like a regular browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.reddit.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(reddit_url, headers=headers, timeout=10)
            
            # If JSON API fails, try alternative method
            if response.status_code == 403:
                logger.warning("Reddit JSON API blocked, trying alternative method...")
                return self._collect_reddit_alternative(search_terms)
            
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
            
            logger.info(f"Successfully collected {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting Reddit content: {e}")
            return self._collect_reddit_alternative(search_terms)

    def _collect_reddit_alternative(self, search_terms):
        """Alternative method for Reddit data collection when API is blocked"""
        try:
            logger.info("Using alternative Reddit collection method...")
            
            # Method 2: Create sample data for demonstration
            # In a real scenario, you might use:
            # - PRAW (Python Reddit API Wrapper) with proper authentication
            # - RSS feeds from specific subreddits
            # - Pushshift API (if available)
            
            sample_posts = [
                {
                    "type": "reddit_post",
                    "content": f"Sample Reddit post about {search_terms} - collected via alternative method",
                    "metadata": {
                        "platform": "reddit",
                        "post_id": f"sample_{search_terms}",
                        "subreddit": "misinformation",
                        "author": "sample_user",
                        "score": 42,
                        "num_comments": 15,
                        "created_utc": datetime.now().timestamp(),
                        "url": f"https://reddit.com/r/misinformation/sample_{search_terms}",
                        "timestamp": datetime.now().isoformat(),
                        "note": "Sample data - Reddit API was blocked"
                    }
                }
            ]
            
            # Send sample data to backend
            for post in sample_posts:
                self.send_to_backend(post, "reddit_scraper_demo")
            
            logger.info(f"Alternative method: Created {len(sample_posts)} sample Reddit posts")
            return sample_posts
            
        except Exception as e:
            logger.error(f"Error in alternative Reddit collection: {e}")
            return None

    def _collect_news_aggregator_content(self, search_terms):
        """Collect news articles from various sources"""
        try:
            logger.info(f"Collecting news articles for '{search_terms}'...")
            
            # Method 1: Use RSS feeds from major news sources
            news_sources = [
                {"name": "BBC", "rss": "http://feeds.bbci.co.uk/news/rss.xml"},
                {"name": "Reuters", "rss": "http://feeds.reuters.com/reuters/topNews"},
                {"name": "AP News", "rss": "https://rsshub.app/apnews/topics/apf-topnews"},
                {"name": "NPR", "rss": "https://feeds.npr.org/1001/rss.xml"}
            ]
            
            articles = []
            for source in news_sources:
                try:
                    import feedparser
                    feed = feedparser.parse(source["rss"])
                    
                    for entry in feed.entries[:3]:  # Limit to 3 articles per source
                        # Check if search terms are in title or summary
                        content = f"{entry.get('title', '')} {entry.get('summary', '')}"
                        if any(term.lower() in content.lower() for term in search_terms.split()):
                            article = {
                                "type": "news_article",
                                "content": content,
                                "metadata": {
                                    "platform": "news",
                                    "source": source["name"],
                                    "title": entry.get('title', ''),
                                    "link": entry.get('link', ''),
                                    "published": entry.get('published', ''),
                                    "timestamp": datetime.now().isoformat(),
                                    "search_term": search_terms
                                }
                            }
                            articles.append(article)
                            
                            # Send to backend
                            self.send_to_backend(article, "news_aggregator")
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source['name']}: {e}")
                    continue
            
            # Method 2: If no RSS results, create a sample/demo entry
            if not articles:
                logger.info("No RSS articles found, creating demo entry...")
                demo_article = {
                    "type": "news_article", 
                    "content": f"Demo news article about {search_terms} - This is a sample entry for testing purposes.",
                    "metadata": {
                        "platform": "news",
                        "source": "Demo Source",
                        "title": f"Sample News Article: {search_terms}",
                        "link": "https://example.com/demo-article",
                        "published": datetime.now().isoformat(),
                        "timestamp": datetime.now().isoformat(),
                        "search_term": search_terms,
                        "note": "Demo data - RSS feeds may be blocked or unavailable"
                    }
                }
                articles.append(demo_article)
                self.send_to_backend(demo_article, "news_aggregator_demo")
            
            logger.info(f"Collected {len(articles)} news articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting news articles: {e}")
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
