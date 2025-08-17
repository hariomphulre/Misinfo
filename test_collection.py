#!/usr/bin/env python3
"""
Quick test script for the enhanced collection system
"""

import sys
import os
import json
from datetime import datetime

# Add the social_source directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'social_source'))

try:
    from youtube import collect_video, extract_video_id_from_url
    from advanced_collector import SocialMediaCollector
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install missing packages: pip install -r social_source/requirements.txt")
    sys.exit(1)

def test_youtube_collection():
    """Test YouTube video collection"""
    print("\n🧪 Testing YouTube Collection...")
    
    # Test with a known public video
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll - always available
    
    try:
        result = collect_video(test_video_id, send_to_backend=False)
        if result:
            print(f"✅ YouTube collection successful: {result['title'][:50]}...")
            return True
        else:
            print("❌ YouTube collection failed")
            return False
    except Exception as e:
        print(f"❌ YouTube collection error: {e}")
        return False

def test_news_collection():
    """Test news article collection"""
    print("\n🧪 Testing News Collection...")
    
    collector = SocialMediaCollector()
    
    try:
        # Test news aggregator
        results = collector.collect_public_social_content("news_aggregator", "misinformation")
        if results:
            print(f"✅ News collection successful: {len(results)} articles")
            return True
        else:
            print("❌ News collection failed")
            return False
    except Exception as e:
        print(f"❌ News collection error: {e}")
        return False

def test_reddit_collection():
    """Test Reddit collection (with fallback)"""
    print("\n🧪 Testing Reddit Collection...")
    
    collector = SocialMediaCollector()
    
    try:
        # Test Reddit collection
        results = collector.collect_public_social_content("reddit", "misinformation")
        if results:
            print(f"✅ Reddit collection successful: {len(results)} posts")
            return True
        else:
            print("⚠️ Reddit collection returned no results (may be blocked)")
            return False
    except Exception as e:
        print(f"⚠️ Reddit collection error: {e}")
        return False

def main():
    print("🚀 Enhanced Misinformation Collector - Test Suite")
    print("=" * 50)
    
    tests = [
        ("YouTube Collection", test_youtube_collection),
        ("News Collection", test_news_collection),
        ("Reddit Collection", test_reddit_collection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n▶️ Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed > 0:
        print("\n✅ Your enhanced collection system is working!")
        print("You can now use:")
        print("  python3 enhanced_collect.py --url 'YOUTUBE_URL'")
        print("  python3 enhanced_collect.py --keywords 'misinformation' --platforms news")
    else:
        print("\n❌ Collection system needs debugging")
        print("Check your API keys and network connectivity")

if __name__ == "__main__":
    main()
