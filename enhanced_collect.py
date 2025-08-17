#!/usr/bin/env python3
"""
Enhanced Misinformation Collector - Main Orchestrator
Coordinates all data collection methods and sources
"""

import sys
import os
import argparse
import json
from datetime import datetime
import asyncio

# Add the social_source directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'social_source'))

try:
    from youtube import collect_video, extract_video_id_from_url
    from document_processor import DocumentProcessor
    from advanced_collector import SocialMediaCollector
    from content_monitor import ContentMonitor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Install required packages: pip install -r social_source/requirements.txt")
    sys.exit(1)

class EnhancedMisinfoCollector:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.social_collector = SocialMediaCollector()
        self.monitor = ContentMonitor()
        
    def collect_from_url(self, url, collection_type="auto"):
        """Smart URL-based collection that detects content type"""
        print(f"🔍 Analyzing URL: {url}")
        
        results = []
        
        # YouTube videos
        if "youtube.com" in url or "youtu.be" in url:
            video_id = extract_video_id_from_url(url)
            if video_id:
                print("📺 Detected YouTube video")
                result = collect_video(video_id)
                if result:
                    results.append({"type": "youtube_video", "data": result})
        
        # News articles
        elif any(news_domain in url for news_domain in [
            "cnn.com", "bbc.com", "reuters.com", "nytimes.com", 
            "washingtonpost.com", "guardian.com", "apnews.com"
        ]):
            print("📰 Detected news article")
            result = self.social_collector.collect_news_articles(url)
            if result:
                results.append({"type": "news_article", "data": result})
        
        # Social media posts (limited public access)
        elif "reddit.com" in url:
            print("🗨️ Detected Reddit post")
            # Extract subreddit and search terms from URL
            # Implementation would parse Reddit URL structure
            pass
        
        # General web content
        else:
            print("🌐 Collecting general web content")
            result = self.social_collector.collect_news_articles(url)  # Reuse method
            if result:
                results.append({"type": "web_content", "data": result})
        
        return results
    
    def collect_from_file(self, file_path):
        """Process and collect data from files"""
        print(f"📄 Processing file: {file_path}")
        
        result = self.doc_processor.process_file(file_path)
        if result:
            return [{"type": "document", "data": result}]
        return []
    
    def collect_from_directory(self, directory_path):
        """Batch process files from directory"""
        print(f"📁 Processing directory: {directory_path}")
        
        results = self.doc_processor.batch_process_directory(directory_path)
        return [{"type": "document", "data": result} for result in results]
    
    def monitor_keywords(self, keywords, platforms=None):
        """Monitor specific keywords across platforms"""
        if platforms is None:
            platforms = ["reddit"]  # Start with Reddit as it's publicly accessible
        
        print(f"🔍 Monitoring keywords: {keywords} on platforms: {platforms}")
        
        results = []
        for platform in platforms:
            if platform == "reddit":
                for keyword in keywords:
                    reddit_results = self.social_collector.collect_public_social_content("reddit", keyword)
                    if reddit_results:
                        results.extend([{"type": "reddit_post", "data": post} for post in reddit_results])
        
        return results
    
    def start_continuous_monitoring(self):
        """Start the automated monitoring system"""
        print("🤖 Starting continuous monitoring system...")
        self.monitor.start_monitoring()
    
    def generate_collection_report(self, results):
        """Generate a summary report of collected data"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(results),
            "by_type": {},
            "by_platform": {},
            "summary": []
        }
        
        for item in results:
            item_type = item.get("type", "unknown")
            report["by_type"][item_type] = report["by_type"].get(item_type, 0) + 1
            
            # Extract platform info
            platform = "unknown"
            if item_type == "youtube_video":
                platform = "youtube"
            elif item_type == "reddit_post":
                platform = "reddit"
            elif item_type == "news_article":
                platform = item.get("data", {}).get("metadata", {}).get("source_domain", "news")
            
            report["by_platform"][platform] = report["by_platform"].get(platform, 0) + 1
            
            # Add to summary
            content_preview = str(item.get("data", {}).get("content", ""))[:100]
            report["summary"].append({
                "type": item_type,
                "platform": platform,
                "content_preview": content_preview
            })
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Enhanced Misinformation Collector')
    parser.add_argument('--url', type=str, help='URL to collect from')
    parser.add_argument('--file', type=str, help='File to process')
    parser.add_argument('--directory', type=str, help='Directory to process')
    parser.add_argument('--keywords', type=str, nargs='+', help='Keywords to monitor')
    parser.add_argument('--platforms', type=str, nargs='+', default=['reddit'], 
                        help='Platforms to monitor (reddit, news_aggregator)')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--output', type=str, help='Output file for results')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    if not any([args.url, args.file, args.directory, args.keywords, args.monitor]):
        print("❌ Please specify at least one collection method:")
        print("   --url URL              Collect from URL")
        print("   --file FILE            Process a file")
        print("   --directory DIR        Process directory")
        print("   --keywords WORDS       Monitor keywords")
        print("   --monitor              Start continuous monitoring")
        return
    
    collector = EnhancedMisinfoCollector()
    all_results = []
    
    try:
        # URL-based collection
        if args.url:
            results = collector.collect_from_url(args.url)
            all_results.extend(results)
        
        # File-based collection
        if args.file:
            results = collector.collect_from_file(args.file)
            all_results.extend(results)
        
        # Directory-based collection
        if args.directory:
            results = collector.collect_from_directory(args.directory)
            all_results.extend(results)
        
        # Keyword monitoring
        if args.keywords:
            results = collector.monitor_keywords(args.keywords, args.platforms)
            all_results.extend(results)
        
        # Continuous monitoring
        if args.monitor:
            collector.start_continuous_monitoring()
            return
        
        # Generate report
        if all_results:
            if args.report:
                report = collector.generate_collection_report(all_results)
                print("\n📊 Collection Report:")
                print(json.dumps(report, indent=2))
            
            # Save results
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, indent=2, ensure_ascii=False)
                print(f"💾 Results saved to: {args.output}")
            
            print(f"\n✅ Collection complete! Gathered {len(all_results)} items")
            
            # Summary by type
            types_summary = {}
            for item in all_results:
                item_type = item.get("type", "unknown")
                types_summary[item_type] = types_summary.get(item_type, 0) + 1
            
            print("📋 Summary by type:")
            for item_type, count in types_summary.items():
                print(f"   {item_type}: {count}")
        else:
            print("⚠️ No data collected")
            
    except KeyboardInterrupt:
        print("\n🛑 Collection stopped by user")
    except Exception as e:
        print(f"❌ Error during collection: {e}")

if __name__ == "__main__":
    main()
