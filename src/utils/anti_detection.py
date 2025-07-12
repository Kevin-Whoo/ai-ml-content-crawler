"""
Advanced anti-detection system for web crawling
"""

import random
import time
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp


@dataclass
class BrowserProfile:
    """Browser fingerprint profile"""
    user_agent: str
    accept: str
    accept_language: str
    accept_encoding: str
    sec_fetch_dest: str
    sec_fetch_mode: str
    sec_fetch_site: str
    viewport: Tuple[int, int]
    platform: str
    browser_name: str
    version: str


class AntiDetectionManager:
    """Comprehensive anti-detection system"""
    
    def __init__(self, config=None):
        self.config = config
        self.session_cookies = {}
        self.request_history = []
        self.current_profile = None
        self.last_request_time = {}
        
        # Initialize browser profiles
        self.browser_profiles = self._create_browser_profiles()
        
        # Request timing patterns
        self.timing_patterns = {
            'human_like': (2.0, 8.0),      # 2-8 seconds
            'aggressive': (0.5, 2.0),      # 0.5-2 seconds  
            'cautious': (5.0, 15.0),       # 5-15 seconds
            'random': (1.0, 10.0)          # 1-10 seconds
        }
    
    def _create_browser_profiles(self) -> List[BrowserProfile]:
        """Create realistic browser profiles"""
        profiles = []
        
        # Chrome profiles
        chrome_versions = ['120.0.0.0', '121.0.0.0', '122.0.0.0', '123.0.0.0']
        for version in chrome_versions:
            profiles.extend([
                BrowserProfile(
                    user_agent=f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    accept_language='en-US,en;q=0.9',
                    accept_encoding='gzip, deflate, br',
                    sec_fetch_dest='document',
                    sec_fetch_mode='navigate',
                    sec_fetch_site='none',
                    viewport=(1920, 1080),
                    platform='Win32',
                    browser_name='Chrome',
                    version=version
                ),
                BrowserProfile(
                    user_agent=f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    accept_language='en-US,en;q=0.9',
                    accept_encoding='gzip, deflate, br',
                    sec_fetch_dest='document',
                    sec_fetch_mode='navigate',
                    sec_fetch_site='none',
                    viewport=(1440, 900),
                    platform='MacIntel',
                    browser_name='Chrome',
                    version=version
                )
            ])
        
        # Firefox profiles
        firefox_versions = ['121.0', '122.0', '123.0']
        for version in firefox_versions:
            profiles.extend([
                BrowserProfile(
                    user_agent=f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    accept_language='en-US,en;q=0.5',
                    accept_encoding='gzip, deflate, br',
                    sec_fetch_dest='document',
                    sec_fetch_mode='navigate',
                    sec_fetch_site='none',
                    viewport=(1920, 1080),
                    platform='Win32',
                    browser_name='Firefox',
                    version=version
                ),
                BrowserProfile(
                    user_agent=f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    accept_language='en-US,en;q=0.5',
                    accept_encoding='gzip, deflate, br',
                    sec_fetch_dest='document',
                    sec_fetch_mode='navigate',
                    sec_fetch_site='none',
                    viewport=(1440, 900),
                    platform='MacIntel',
                    browser_name='Firefox',
                    version=version
                )
            ])
        
        # Safari profiles
        safari_versions = ['17.2', '17.3', '17.4']
        for version in safari_versions:
            profiles.append(
                BrowserProfile(
                    user_agent=f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    accept_language='en-US,en;q=0.9',
                    accept_encoding='gzip, deflate, br',
                    sec_fetch_dest='document',
                    sec_fetch_mode='navigate',
                    sec_fetch_site='none',
                    viewport=(1440, 900),
                    platform='MacIntel',
                    browser_name='Safari',
                    version=version
                )
            )
        
        return profiles
    
    def get_random_profile(self) -> BrowserProfile:
        """Get a random browser profile"""
        return random.choice(self.browser_profiles)
    
    def rotate_profile(self) -> BrowserProfile:
        """Rotate to a new browser profile"""
        # Avoid using the same profile consecutively
        available_profiles = [p for p in self.browser_profiles if p != self.current_profile]
        self.current_profile = random.choice(available_profiles)
        return self.current_profile
    
    def get_headers(self, domain: str = None, referer: str = None, 
                   profile: BrowserProfile = None) -> Dict[str, str]:
        """Generate realistic headers with optional customization"""
        if not profile:
            profile = self.current_profile or self.rotate_profile()
        
        headers = {
            'User-Agent': profile.user_agent,
            'Accept': profile.accept,
            'Accept-Language': profile.accept_language,
            'Accept-Encoding': profile.accept_encoding,
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': profile.sec_fetch_dest,
            'Sec-Fetch-Mode': profile.sec_fetch_mode,
            'Sec-Fetch-Site': profile.sec_fetch_site,
            'Cache-Control': 'max-age=0'
        }
        
        # Add domain-specific headers
        if domain:
            if 'github.com' in domain:
                headers.update({
                    'Accept': 'application/vnd.github.v3+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                })
            elif 'medium.com' in domain:
                headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'X-Requested-With': 'XMLHttpRequest'
                })
        
        # Add referer if provided
        if referer:
            headers['Referer'] = referer
        
        # Randomly add some optional headers
        if random.random() < 0.7:  # 70% chance
            headers['Sec-Ch-Ua'] = f'"{profile.browser_name}";v="{profile.version}", "Chromium";v="{profile.version}", "Not_A Brand";v="8"'
            headers['Sec-Ch-Ua-Mobile'] = '?0'
            headers['Sec-Ch-Ua-Platform'] = f'"{profile.platform}"'
        
        return headers
    
    async def calculate_delay(self, domain: str, pattern: str = 'human_like') -> float:
        """Fast delay calculation"""
        return 0.1  # Fixed minimal delay for speed
    
    def simulate_human_behavior(self) -> Dict[str, any]:
        """Simulate human-like browsing behavior"""
        behaviors = []
        
        # Random mouse movements (simulated)
        if random.random() < 0.3:
            behaviors.append({
                'type': 'mouse_move',
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'timestamp': time.time()
            })
        
        # Random scrolling (simulated)
        if random.random() < 0.4:
            behaviors.append({
                'type': 'scroll',
                'direction': random.choice(['up', 'down']),
                'amount': random.randint(100, 500),
                'timestamp': time.time()
            })
        
        # Random page interactions
        if random.random() < 0.2:
            behaviors.append({
                'type': 'interaction',
                'action': random.choice(['click', 'hover', 'focus']),
                'timestamp': time.time()
            })
        
        return {
            'behaviors': behaviors,
            'session_duration': random.randint(30, 300),  # 30s to 5min
            'page_views': random.randint(1, 5)
        }
    
    def manage_cookies(self, domain: str, response_cookies=None) -> Dict[str, str]:
        """Manage cookies for session persistence"""
        if domain not in self.session_cookies:
            self.session_cookies[domain] = {}
        
        # Add response cookies
        if response_cookies:
            for cookie in response_cookies:
                self.session_cookies[domain][cookie.key] = cookie.value
        
        # Generate realistic session cookies if none exist
        if not self.session_cookies[domain]:
            self.session_cookies[domain] = self._generate_session_cookies(domain)
        
        return self.session_cookies[domain]
    
    def _generate_session_cookies(self, domain: str) -> Dict[str, str]:
        """Generate realistic session cookies"""
        cookies = {}
        
        # Common session cookies
        session_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
        cookies['session_id'] = session_id
        
        # Tracking prevention
        cookies['privacy_settings'] = 'essential_only'
        
        # Timezone and locale
        cookies['timezone'] = random.choice(['America/New_York', 'America/Los_Angeles', 'Europe/London'])
        cookies['locale'] = random.choice(['en-US', 'en-GB'])
        
        # Domain-specific cookies
        if 'github.com' in domain:
            cookies['preferred_color_mode'] = random.choice(['light', 'dark'])
            cookies['tz'] = 'America/New_York'
        elif 'medium.com' in domain:
            cookies['uid'] = ''.join(random.choices('0123456789abcdef', k=16))
        
        return cookies
    
    def detect_bot_protection(self, content: str, headers: Dict[str, str]) -> bool:
        """Detect if page has bot protection"""
        protection_indicators = [
            'cloudflare',
            'captcha',
            'bot protection',
            'access denied',
            'rate limit',
            'too many requests',
            'suspicious activity',
            'challenge',
            'verification'
        ]
        
        content_lower = content.lower()
        
        # Check content for protection indicators
        for indicator in protection_indicators:
            if indicator in content_lower:
                return True
        
        # Check response headers
        protected_headers = [
            'cf-ray',  # Cloudflare
            'x-served-by',  # Fastly
            'x-cache',  # Various CDNs
        ]
        
        for header in protected_headers:
            if header.lower() in [h.lower() for h in headers.keys()]:
                return True
        
        return False
    
    def get_advanced_session_config(self) -> Dict[str, any]:
        """Get advanced aiohttp session configuration"""
        profile = self.current_profile or self.rotate_profile()
        
        # Create connector with realistic settings
        connector_config = {
            'limit': random.randint(8, 15),  # Connection pool size
            'limit_per_host': random.randint(2, 4),  # Connections per host
            'ttl_dns_cache': 300,  # DNS cache TTL
            'use_dns_cache': True,
            'keepalive_timeout': 30,
            'enable_cleanup_closed': True,
            'force_close': False,  # Keep connections alive
        }
        
        # Fast timeout configuration
        timeout_config = {
            'total': 10,  # Fast total timeout
            'connect': 5,  # Fast connection timeout
            'sock_read': 8,  # Fast socket read timeout
        }
        
        return {
            'connector': connector_config,
            'timeout': timeout_config,
            'headers': self.get_headers(),
            'cookies': self.session_cookies.get('default', {}),
            'read_timeout': timeout_config['sock_read'],
            'conn_timeout': timeout_config['connect']
        }
    
    def log_request(self, url: str, method: str = 'GET', status: int = None):
        """Log request for pattern analysis"""
        self.request_history.append({
            'url': url,
            'method': method,
            'status': status,
            'timestamp': datetime.now(),
            'profile': self.current_profile.browser_name if self.current_profile else None
        })
        
        # Keep only last 1000 requests
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def get_stealth_recommendations(self) -> Dict[str, str]:
        """Get recommendations for stealth improvements"""
        recommendations = []
        
        # Analyze request patterns
        if len(self.request_history) > 10:
            recent_requests = self.request_history[-10:]
            
            # Check for too frequent requests
            timestamps = [req['timestamp'] for req in recent_requests]
            if len(timestamps) > 1:
                avg_interval = sum((timestamps[i] - timestamps[i-1]).total_seconds() 
                                 for i in range(1, len(timestamps))) / (len(timestamps) - 1)
                
                if avg_interval < 2.0:
                    recommendations.append("Increase delay between requests")
            
            # Check for pattern detection
            domains = [req['url'].split('/')[2] for req in recent_requests if '/' in req['url']]
            if len(set(domains)) == 1 and len(domains) > 5:
                recommendations.append("Vary target domains to avoid detection")
        
        return {
            'recommendations': recommendations,
            'current_profile': self.current_profile.browser_name if self.current_profile else 'None',
            'request_count': len(self.request_history),
            'last_request': self.request_history[-1]['timestamp'].isoformat() if self.request_history else None
        }