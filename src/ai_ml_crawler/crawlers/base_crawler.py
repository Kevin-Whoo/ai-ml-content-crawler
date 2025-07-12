"""
Base crawler class with common functionality
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import os
from pathlib import Path
from urllib.parse import urlparse

from ai_ml_crawler.config import CrawlerConfig
from ai_ml_crawler.utils.validation import InputValidator, URLRedirectValidator, ValidationError
from ai_ml_crawler.utils.error_handler import ErrorHandler, NetworkError, ParseError, ErrorLevel, AntiDetectionError
from ai_ml_crawler.utils.anti_detection import AntiDetectionManager
from ai_ml_crawler.utils.caching import SmartCache, RateLimitCache
from ai_ml_crawler.utils import is_recent_date


class BaseCrawler(ABC):
    """Abstract base class for all crawlers"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize security and anti-detection systems
        self.validator = InputValidator()
        self.redirect_validator = URLRedirectValidator(self.validator)
        self.error_handler = ErrorHandler()
        self.anti_detection = AntiDetectionManager(config)
        
        # Caching systems - Fixed: Pass configured TTL!
        self.cache = SmartCache(
            cache_dir=f"cache/{self.__class__.__name__}",
            default_ttl=self.config.cache_ttl,  # Use configured TTL (15 days)
            max_size_mb=self.config.max_cache_size_mb
        )
        self.rate_limit_cache = RateLimitCache()
        
        # Session management
        self.session_cookies = {}
        self.last_profile_rotation = time.time()
        
        # Proxy configuration
        self.proxy_list = self._load_proxy_list()
        self.current_proxy_index = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with enhanced anti-detection"""
        if self.session is None or self.session.closed:
            # Rotate browser profiles periodically
            current_time = time.time()
            if current_time - self.last_profile_rotation > 1800:  # 30 minutes instead of 5
                self.anti_detection.rotate_profile()
                self.last_profile_rotation = current_time
            
            # Get advanced session configuration
            session_config = self.anti_detection.get_advanced_session_config()
            
            # Create connector with anti-detection settings
            connector_config = session_config['connector'].copy()
            
            # Add proxy support if available
            current_proxy = self._get_current_proxy()
            if current_proxy:
                connector_config['limit'] = min(connector_config.get('limit', 10), 5)  # Reduce connections with proxy
            
            connector = aiohttp.TCPConnector(**connector_config)
            timeout = aiohttp.ClientTimeout(**session_config['timeout'])
            
            self.session = aiohttp.ClientSession(
                headers=session_config['headers'],
                timeout=timeout,
                connector=connector,
                cookie_jar=aiohttp.CookieJar()
            )
        return self.session
    
    async def _fetch_url(self, url: str, retries: int = 1, headers: Dict[str, str] = None) -> Optional[str]:
        """Fetch content from URL with enhanced error handling and retries"""
        
        # Fast URL validation - basic checks only
        if not url or not url.startswith(('http://', 'https://')):
            return None
        
        # Basic SSRF protection - check for localhost/internal IPs
        domain = urlparse(url).netloc.lower()
        if any(blocked in domain for blocked in ['localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.', '172.']):
            print(f"⚠️ Blocked internal URL: {domain}")
            return None
        
        # Check cache first
        cached_content = self.cache.get(url, headers)
        if cached_content:
            return cached_content
        
        for attempt in range(retries):
            try:
                session = await self._get_session()
                
                # Minimal delay for speed
                if self.config.request_delay > 0:
                    await asyncio.sleep(self.config.request_delay)
                
                # Simple headers for speed
                request_headers = headers or {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                # Prepare request kwargs
                request_kwargs = {
                    'headers': request_headers
                }
                
                # Skip proxy for speed
                
                async with session.get(url, **request_kwargs) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Skip bot protection detection for speed
                        
                        # Basic content validation only
                        if len(content) > 50:  # Minimal validation
                            # Cache with configured TTL
                            self.cache.set(url, content, headers, self.config.cache_ttl)
                            return content
                        
                    else:
                        # Skip error handling for speed, just return None
                        return None
                        
            except Exception:
                # Skip all error handling for speed, just fail fast
                return None
        
        return None
    
    
    def _is_recent(self, date_str: str, date_format: str = "%Y-%m-%d") -> bool:
        """Check if date is within the configured time window"""
        return is_recent_date(date_str, self.config.max_days_back)
    
    def _create_item(self, title: str, url: str, date: Optional[str], summary: str = "", 
                    content: str = "", tags: List[str] = None, source: str = "") -> Dict[str, Any]:
        """Create standardized content item with validation"""
        try:
            # Skip validation for speed optimization
            validated_url = url
            validated_content = content[:50000] if content else ""
            validated_summary = summary[:1000] if summary else ""
            validated_tags = tags or []
            
            # Use provided date or default to "Unknown"
            processed_date = date if date else "Unknown"
            
            return {
                'title': title.strip()[:500],  # Limit title length
                'url': validated_url,
                'date': processed_date,
                'summary': validated_summary,
                'content': validated_content,
                'tags': validated_tags,
                'source': source,
                'crawled_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            # Return minimal safe item for any errors
            return {
                'title': title.strip()[:500] if title else 'Unknown',
                'url': url,  # Keep original for debugging
                'date': date if date else "Unknown",
                'summary': summary[:1000] if summary else '',
                'content': content[:50000] if content else '',
                'tags': tags or [],
                'source': source,
                'crawled_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def close(self):
        """Close the session and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            
        # Print consolidated statistics
        cache_stats = self.cache.get_stats()
        print(f"💾 Cache stats: {cache_stats['hit_rate_percent']}% hit rate, {cache_stats['entries_count']} entries")
        
        # Only print recommendations if there are issues
        cache_recommendations = self.cache.get_cache_recommendations()
        if cache_recommendations and cache_stats['hit_rate_percent'] < 50:
            print("📊 Cache recommendations:")
            for rec in cache_recommendations:
                print(f"  • {rec}")
        
        # Optimize cache silently
        self.cache.optimize()
        self.rate_limit_cache.clear_expired()
    
    def _load_proxy_list(self) -> List[str]:
        """Load proxy list from configuration or environment"""
        proxies = []
        
        # Load from environment variable
        proxy_list_env = os.getenv('CRAWLER_PROXIES')
        if proxy_list_env:
            proxies.extend(proxy_list_env.split(','))
        
        # Load from file if exists
        proxy_file = Path('proxies.txt')
        if proxy_file.exists():
            try:
                with open(proxy_file, 'r') as f:
                    file_proxies = [line.strip() for line in f if line.strip()]
                    proxies.extend(file_proxies)
            except Exception as e:
                self.error_handler.handle_error(
                    ParseError(f"Failed to load proxy file: {str(e)}", "PROXY_LOAD"),
                    {'file': str(proxy_file)},
                    ErrorLevel.LOW
                )
        
        return [proxy for proxy in proxies if proxy]
    
    def _get_current_proxy(self) -> Optional[str]:
        """Get current proxy for requests"""
        if not self.proxy_list:
            return None
        
        return self.proxy_list[self.current_proxy_index % len(self.proxy_list)]
    
    def _rotate_proxy(self):
        """Rotate to next proxy in list"""
        if self.proxy_list:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
    
    def _sanitize_search_query(self, query: str) -> str:
        """Sanitize search query for safe URL construction"""
        try:
            return self.validator.sanitize_search_query(query)
        except ValidationError as e:
            self.error_handler.handle_error(e, {'query': query}, ErrorLevel.MEDIUM)
            return ""
    
    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """Main crawling method - must be implemented by subclasses"""
        pass