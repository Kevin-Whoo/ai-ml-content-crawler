#!/usr/bin/env python3
"""
CLI entry point for AI/ML Content Crawler
"""

import sys
import os
from pathlib import Path

from ai_ml_crawler.main import MasterCrawler, setup_enhanced_config
from datetime import datetime


def main():
    print("🤖 AI/ML Content Crawler")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        config = setup_enhanced_config()
        crawler = MasterCrawler(config)
        crawler.run()

        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except KeyboardInterrupt:
        print("\n⏹️ Crawling interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
