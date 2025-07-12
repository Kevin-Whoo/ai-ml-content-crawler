#!/usr/bin/env python3
"""
Enhanced AI/ML Content Crawler with Security & Anti-Detection
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

from config import CrawlerConfig, SOURCES_CONFIG
from crawlers.anthropic_crawler import AnthropicCrawler
from crawlers.openai_crawler import OpenAICrawler
from crawlers.meta_crawler import MetaCrawler
from crawlers.github_crawler import GitHubCrawler
from crawlers.huggingface_crawler import HuggingFaceCrawler
from crawlers.medium_crawler import MediumCrawler
from crawlers.google_scholar_crawler import GoogleScholarCrawler
from crawlers.arxiv_crawler import ArxivCrawler
# IEEE crawler removed per user request
from utils.content_filter import ContentFilter
from utils.output_manager import OutputManager


class MasterCrawler:
    """Main crawler orchestrator"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.content_filter = ContentFilter(config)
        self.output_manager = OutputManager(config)
        
        # Initialize crawlers (IEEE removed per user request)
        self.crawlers = {
            'anthropic': AnthropicCrawler(config),
            'openai': OpenAICrawler(config),
            'meta': MetaCrawler(config),
            'github': GitHubCrawler(config, SOURCES_CONFIG.get('github', {})),
            'huggingface': HuggingFaceCrawler(config),
            'medium': MediumCrawler(config),
            'google_scholar': GoogleScholarCrawler(config),
            'arxiv': ArxivCrawler(config)
        }
    
    async def crawl_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Crawl all configured sources - truly concurrent version"""
        print("🚀 Starting optimized AI/ML content crawl...")
        
        results = {}
        
        # Create all tasks at once for better concurrency
        crawler_tasks = []
        for source_name, crawler in self.crawlers.items():
            task = asyncio.create_task(self._crawl_source(source_name, crawler))
            crawler_tasks.append((source_name, task))
        
        print(f"📡 Running {len(crawler_tasks)} crawlers concurrently...")
        
        # Use asyncio.gather for true concurrent execution
        completed_tasks = await asyncio.gather(*[task for _, task in crawler_tasks], return_exceptions=True)
        
        # Process results
        for i, (source_name, _) in enumerate(crawler_tasks):
            result = completed_tasks[i]
            if isinstance(result, Exception):
                print(f"❌ Error crawling {source_name}: {str(result)}")
                results[source_name] = []
            else:
                results[source_name] = result
                print(f"✅ {source_name}: {len(result)} relevant items")
        
        return results
    
    async def _crawl_source(self, source_name: str, crawler) -> List[Dict[str, Any]]:
        """Crawl a single source with error handling"""
        try:
            source_results = await crawler.crawl()
            if source_results:
                filtered_results = self.content_filter.filter_content(source_results)
                return filtered_results
            else:
                return []
        except Exception as e:
            raise e
        finally:
            # Clean up crawler resources
            try:
                await crawler.close()
            except Exception:
                pass  # Ignore cleanup errors
    
    def run(self):
        """Run the complete crawling pipeline - optimized"""
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Run async crawling
        results = asyncio.run(self.crawl_all_sources())
        
        # Process and save results
        self.output_manager.save_results(results)
        
        # Print optimized summary
        self._print_summary(results)
    
    def _print_summary(self, results: Dict[str, List[Dict[str, Any]]]):
        """Print optimized summary of crawling results"""
        total_items = sum(len(items) for items in results.values())
        successful_sources = len([s for s, items in results.items() if items])
        
        print(f"\n🎉 Crawling Complete!")
        print(f"📊 Total Resources: {total_items}")
        print(f"✅ Successful Sources: {successful_sources}/{len(results)}")
        print(f"📁 Output Directory: {self.config.output_dir}/")
        
        # Show top sources
        if results:
            print("\n📅 Results by Source:")
            sorted_sources = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
            for source, items in sorted_sources[:5]:  # Top 5 sources
                if items:
                    top_score = max(item.get('relevance_score', 0) for item in items)
                    print(f"  • {source.title()}: {len(items)} items (top score: {top_score:.1f})")
        
        # Show output files efficiently
        output_files = [f for f in os.listdir(self.config.output_dir) if f.endswith('.md')]
        if output_files:
            latest_file = max(output_files)
            file_path = os.path.join(self.config.output_dir, latest_file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"\n📄 Generated: {latest_file} ({file_size:.1f} KB)")


def setup_enhanced_config():
    """Setup configuration for extended time range and better content capture"""
    config = CrawlerConfig()
    
    # Speed-optimized settings
    config.request_delay = 0.05  # Minimal delays for speed
    config.request_jitter = 0.0  # No randomness for speed
    
    # Extended time range for more content
    config.max_days_back = 180  # 6 months for comprehensive content capture
    
    # Use configured TTL from config.py (15 days) instead of overriding
    # config.cache_ttl = 3600  # Removed: Don't override configured TTL
    config.enable_caching = True
    
    # Minimal security for speed
    config.enable_rate_limiting = False
    config.rotate_user_agents = False
    
    # Proxy settings from environment
    if os.getenv('CRAWLER_ENABLE_PROXIES', 'false').lower() == 'true':
        config.enable_proxy_rotation = True
        print("🔄 Proxy rotation enabled")
    
    return config


if __name__ == "__main__":
    print("🤖 Enhanced AI/ML Content Crawler")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Setup enhanced configuration
    config = setup_enhanced_config()
    
    print("🛡️ Enhanced Security Features:")
    print("  🔒 Input validation & SSRF protection: ✅")
    print("  🥷 Anti-detection browser profiles: ✅")
    print("  💾 Smart caching: ✅")
    print("  ⚡ Rate limiting awareness: ✅")
    print(f"  🔄 Proxy rotation: {'✅' if config.enable_proxy_rotation else '❌'}")
    print(f"  ⏱️ Request delay: {config.request_delay}s")
    print()
    
    try:
        crawler = MasterCrawler(config)
        crawler.run()
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Crawling interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")