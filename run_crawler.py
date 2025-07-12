#!/usr/bin/env python3
"""
AI/ML Content Crawler - Main Launcher
Run this script to start the crawler.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

# Change working directory to project root for relative paths
os.chdir(project_root)

if __name__ == "__main__":
    # Import and run the main crawler
    from src.main import MasterCrawler, setup_enhanced_config
    from datetime import datetime
    
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
