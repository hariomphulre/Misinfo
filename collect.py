#!/usr/bin/env python3
"""
Main integration script for the Misinformation Collector project.
This script demonstrates how to use the social source components together.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add the social_source directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'social_source'))

# Import available modules
TWITTER_AVAILABLE = False
YOUTUBE_AVAILABLE = False

try:
    from youtube import collect_video, extract_video_id_from_url
    YOUTUBE_AVAILABLE = True
    print("✅ YouTube collector loaded successfully")
except ImportError as e:
    print(f"⚠️  YouTube collector not available: {e}")

try:
    from twitter import collect_tweet
    TWITTER_AVAILABLE = True
    print("✅ Twitter collector loaded successfully")
except ImportError as e:
    print(f"⚠️  Twitter collector not available: {e}")

if not TWITTER_AVAILABLE and not YOUTUBE_AVAILABLE:
    print("❌ No social media collectors available!")
    print("Make sure you have installed the requirements for social_source:")
    print("pip install -r social_source/requirements.txt")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Misinformation Collector CLI')
    
    # Only add Twitter option if it's available
    if TWITTER_AVAILABLE and YOUTUBE_AVAILABLE:
        parser.add_argument('--source', choices=['twitter', 'youtube'], required=True,
                            help='Source platform to collect from')
    elif YOUTUBE_AVAILABLE:
        parser.add_argument('--source', choices=['youtube'], required=True,
                            help='Source platform to collect from (Twitter not available)')
    elif TWITTER_AVAILABLE:
        parser.add_argument('--source', choices=['twitter'], required=True,
                            help='Source platform to collect from (YouTube not available)')
    else:
        print("❌ No collectors available!")
        return
    
    parser.add_argument('--url', type=str, help='URL to collect from')
    parser.add_argument('--id', type=str, help='Direct ID to collect (tweet ID or video ID)')
    parser.add_argument('--no-backend', action='store_true', 
                        help='Skip sending data to backend')
    parser.add_argument('--output', type=str, help='Output file to save results')
    
    args = parser.parse_args()
    
    send_to_backend = not args.no_backend
    result = None
    
    try:
        if args.source == 'twitter' and TWITTER_AVAILABLE:
            if args.id:
                tweet_id = args.id
            elif args.url:
                # Extract tweet ID from URL (simplified)
                tweet_id = args.url.split('/')[-1].split('?')[0]
            else:
                print("Error: Please provide either --url or --id for Twitter")
                return
            
            print(f"Collecting tweet: {tweet_id}")
            result = collect_tweet(tweet_id, send_to_backend)
            
        elif args.source == 'youtube' and YOUTUBE_AVAILABLE:
            if args.id:
                video_id = args.id
            elif args.url:
                video_id = extract_video_id_from_url(args.url)
                if not video_id:
                    print("Error: Could not extract video ID from URL")
                    return
            else:
                print("Error: Please provide either --url or --id for YouTube")
                return
            
            print(f"Collecting video: {video_id}")
            result = collect_video(video_id, send_to_backend)
        
        else:
            print(f"Error: {args.source} collector is not available")
            return
        
        if result:
            print("\nCollection successful!")
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Results saved to: {args.output}")
            else:
                print("Result:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            if send_to_backend and 'backend_doc_id' in result:
                print(f"Data sent to backend with ID: {result['backend_doc_id']}")
        else:
            print("Collection failed!")
            
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
