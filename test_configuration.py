#!/usr/bin/env python3
"""
Test script to verify date filtering and influence scoring
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import CrawlerConfig
from crawlers.base_crawler import BaseCrawler
from utils.content_filter import ContentFilter

# Create test crawler instance
class TestCrawler(BaseCrawler):
    async def crawl(self):
        pass

# Test configuration
config = CrawlerConfig()
print(f"\n📅 Configuration Analysis:")
print(f"  • max_days_back: {config.max_days_back} days (6 months)")
print(f"  • cache_ttl: {config.cache_ttl} seconds ({config.cache_ttl / 86400} days)")
print(f"  • max_results_per_source: {config.max_results_per_source}")

# Test date filtering
print(f"\n📅 Date Filtering Tests:")
test_crawler = TestCrawler(config)

test_dates = [
    (datetime.now().isoformat(), "Today"),
    ((datetime.now() - timedelta(days=30)).isoformat(), "1 month ago"),
    ((datetime.now() - timedelta(days=90)).isoformat(), "3 months ago"),
    ((datetime.now() - timedelta(days=179)).isoformat(), "179 days ago"),
    ((datetime.now() - timedelta(days=181)).isoformat(), "181 days ago"),
    ((datetime.now() - timedelta(days=365)).isoformat(), "1 year ago"),
    ("invalid-date", "Invalid date"),
    ("", "Empty date")
]

for date_str, description in test_dates:
    is_recent = test_crawler._is_recent(date_str)
    print(f"  • {description}: {date_str[:10] if date_str else 'None'} -> {'✅ INCLUDED' if is_recent else '❌ EXCLUDED'}")

# Test content filtering
print(f"\n🎯 Influence Scoring Tests:")
filter = ContentFilter(config)

test_items = [
    {
        "title": "GPT-4V: Multimodal Large Language Model",
        "summary": "OpenAI releases GPT-4V with vision capabilities",
        "source": "OpenAI Blog",
        "date": datetime.now().isoformat(),
        "tags": ["multimodal", "ai", "research"]
    },
    {
        "title": "LangChain v0.1.0 Released",
        "summary": "Major update to the AI agent framework",
        "source": "GitHub",
        "date": (datetime.now() - timedelta(days=30)).isoformat(),
        "stars": 15000,
        "forks": 2000,
        "tags": ["agent", "framework"]
    },
    {
        "title": "Energy AI for Smart Grids",
        "summary": "Using AI for renewable energy optimization",
        "source": "ArXiv",
        "date": (datetime.now() - timedelta(days=60)).isoformat(),
        "tags": ["energy", "ai", "paper"]
    },
    {
        "title": "Random Old Blog Post",
        "summary": "Some content from 2 years ago",
        "source": "Unknown",
        "date": (datetime.now() - timedelta(days=730)).isoformat(),
        "tags": ["blog"]
    }
]

filtered_items = filter.filter_content(test_items)

print(f"\nScoring Results:")
for item in filtered_items:
    print(f"\n  📄 {item['title']}")
    print(f"     Score: {item.get('relevance_score', 0):.1f}")
    print(f"     Source: {item['source']}")
    print(f"     Date: {item['date'][:10]}")
    print(f"     Reasons: {', '.join(item.get('relevance_reasons', []))}")

print(f"\n📊 Summary:")
print(f"  • Total items tested: {len(test_items)}")
print(f"  • Items with score > 0: {len(filtered_items)}")
print(f"  • Average score: {sum(item.get('relevance_score', 0) for item in filtered_items) / len(filtered_items) if filtered_items else 0:.1f}")
