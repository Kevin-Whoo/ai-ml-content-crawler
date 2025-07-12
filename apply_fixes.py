#!/usr/bin/env python3
"""
Quick fix script for critical issues
"""

import os
import re

def fix_requirements():
    """Remove asyncio from requirements.txt"""
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    with open('requirements.txt', 'w') as f:
        for line in lines:
            if not line.startswith('asyncio'):
                f.write(line)
    print("✅ Fixed requirements.txt")

def add_date_filtering_reminder():
    """Add TODO comments to crawlers missing date filtering"""
    crawlers = [
        'src/crawlers/openai_crawler.py',
        'src/crawlers/meta_crawler.py',
        'src/crawlers/anthropic_crawler.py',
        'src/crawlers/arxiv_crawler.py',
        'src/crawlers/medium_crawler.py',
        'src/crawlers/huggingface_crawler.py',
        'src/crawlers/google_scholar_crawler.py'
    ]
    
    for crawler_file in crawlers:
        with open(crawler_file, 'r') as f:
            content = f.read()
        
        # Add TODO at the beginning of crawl method
        if 'TODO: Add date filtering' not in content:
            content = content.replace(
                'async def crawl(self)',
                'async def crawl(self)\n        # TODO: Add date filtering - filter items by self._is_recent(date)'
            )
            
            with open(crawler_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Added TODO to {crawler_file}")

def create_date_filter_example():
    """Create example of how to add date filtering"""
    example = '''# Example: How to add date filtering to crawlers

# In each crawler's crawl() method, after getting items:

filtered_items = []
for item in items:
    # Get the date field (might be different for each source)
    date_str = item.get('date') or item.get('published') or item.get('created_at', '')
    
    # Check if it's recent (within last 6 months)
    if self._is_recent(date_str):
        filtered_items.append(item)
    else:
        print(f"Skipping old item: {item.get('title', 'Unknown')} from {date_str}")

items = filtered_items
'''
    
    with open('DATE_FILTERING_EXAMPLE.py', 'w') as f:
        f.write(example)
    
    print("✅ Created DATE_FILTERING_EXAMPLE.py")

if __name__ == "__main__":
    print("🔧 Applying quick fixes...")
    fix_requirements()
    add_date_filtering_reminder()
    create_date_filter_example()
    print("\n⚠️  IMPORTANT: You still need to manually implement date filtering in each crawler!")
    print("See DATE_FILTERING_EXAMPLE.py for guidance.")
