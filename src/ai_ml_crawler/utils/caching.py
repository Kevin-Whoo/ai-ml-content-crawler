"""
Advanced caching system for web crawler requests
"""

import hashlib
import json
import os
import pickle
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    ttl: int  # Time to live in seconds
    size: int
    url: str
    headers: Dict[str, str]
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > (self.timestamp + timedelta(seconds=self.ttl))
    
    @property
    def age_seconds(self) -> int:
        """Get age of cache entry in seconds"""
        return int((datetime.now() - self.timestamp).total_seconds())


class SmartCache:
    """Intelligent caching system with anti-detection features"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 100, 
                 default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        
        # In-memory cache for fast access
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0
        }
        
        # Load existing cache entries
        self._load_cache_index()
    
    def _generate_cache_key(self, url: str, headers: Dict[str, str] = None) -> str:
        """Generate cache key from URL and headers"""
        cache_data = {
            'url': url,
            'headers': sorted((headers or {}).items())
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get file path for cache entry"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _load_cache_index(self):
        """Load cache index from disk for better hit rates"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index = json.load(f)
                
                # Load recent entries into memory
                for cache_key, metadata in index.items():
                    cache_file = self._get_cache_file_path(cache_key)
                    if cache_file.exists():
                        try:
                            entry = self._load_cache_entry(cache_key)
                            if entry and not entry.is_expired:
                                self.memory_cache[cache_key] = entry
                                self.cache_stats['size_bytes'] += entry.size
                        except Exception:
                            # Remove corrupted cache entry
                            cache_file.unlink(missing_ok=True)
                            
            except Exception:
                # Corrupted index, start fresh
                pass
    
    def _save_cache_index(self):
        """Save cache index to disk for persistence"""
        index = {}
        for cache_key, entry in self.memory_cache.items():
            index[cache_key] = {
                'timestamp': entry.timestamp.isoformat(),
                'ttl': entry.ttl,
                'url': entry.url,
                'size': entry.size
            }
        
        index_file = self.cache_dir / "cache_index.json"
        try:
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception:
            pass  # Continue without index if save fails
    
    def _load_cache_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Load cache entry from disk"""
        cache_file = self._get_cache_file_path(cache_key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def _save_cache_entry(self, cache_key: str, entry: CacheEntry):
        """Save cache entry to disk"""
        cache_file = self._get_cache_file_path(cache_key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception:
            pass  # Continue without caching if save fails
    
    def get(self, url: str, headers: Dict[str, str] = None) -> Optional[str]:
        """Get cached content for URL"""
        cache_key = self._generate_cache_key(url, headers)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if not entry.is_expired:
                self.cache_stats['hits'] += 1
                return entry.data
            else:
                # Remove expired entry
                self._evict_entry(cache_key)
        
        # Check disk cache
        entry = self._load_cache_entry(cache_key)
        if entry and not entry.is_expired:
            # Move to memory cache
            self.memory_cache[cache_key] = entry
            self.cache_stats['hits'] += 1
            self.cache_stats['size_bytes'] += entry.size
            return entry.data
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, url: str, content: str, headers: Dict[str, str] = None, 
            ttl: int = None):
        """Cache content for URL"""
        if not content:
            return
        
        cache_key = self._generate_cache_key(url, headers)
        ttl = ttl or self.default_ttl
        
        # Create cache entry
        entry = CacheEntry(
            data=content,
            timestamp=datetime.now(),
            ttl=ttl,
            size=len(content.encode('utf-8')),
            url=url,
            headers=headers or {}
        )
        
        # Check cache size limits
        self._ensure_cache_size_limit(entry.size)
        
        # Store in memory and disk
        self.memory_cache[cache_key] = entry
        self.cache_stats['size_bytes'] += entry.size
        self._save_cache_entry(cache_key, entry)
        
        # Save index more frequently for better persistence
        if len(self.memory_cache) % 10 == 0 or time.time() - getattr(self, '_last_index_save', 0) > 60:
            self._save_cache_index()
            self._last_index_save = time.time()
    
    def _ensure_cache_size_limit(self, new_entry_size: int):
        """Ensure cache doesn't exceed size limit"""
        target_size = self.max_size_bytes - new_entry_size
        
        while self.cache_stats['size_bytes'] > target_size and self.memory_cache:
            # Evict least recently used entries
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k].timestamp)
            self._evict_entry(oldest_key)
    
    def _evict_entry(self, cache_key: str):
        """Evict entry from cache"""
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            self.cache_stats['size_bytes'] -= entry.size
            self.cache_stats['evictions'] += 1
            del self.memory_cache[cache_key]
            
            # Remove from disk
            cache_file = self._get_cache_file_path(cache_key)
            cache_file.unlink(missing_ok=True)
    
    def clear_expired(self):
        """Remove all expired entries"""
        expired_keys = [key for key, entry in self.memory_cache.items() 
                       if entry.is_expired]
        
        for key in expired_keys:
            self._evict_entry(key)
    
    def clear_all(self):
        """Clear all cache entries"""
        # Clear memory cache
        self.memory_cache.clear()
        self.cache_stats['size_bytes'] = 0
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink(missing_ok=True)
        
        index_file = self.cache_dir / "cache_index.json"
        index_file.unlink(missing_ok=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'evictions': self.cache_stats['evictions'],
            'entries_count': len(self.memory_cache),
            'size_mb': round(self.cache_stats['size_bytes'] / (1024 * 1024), 2),
            'max_size_mb': round(self.max_size_bytes / (1024 * 1024), 2)
        }
    
    def get_cache_recommendations(self) -> List[str]:
        """Get recommendations for cache optimization"""
        recommendations = []
        stats = self.get_stats()
        
        if stats['hit_rate_percent'] < 30:
            recommendations.append("Low cache hit rate - consider increasing TTL or cache size")
        
        if stats['evictions'] > stats['hits'] * 0.5:
            recommendations.append("High eviction rate - consider increasing cache size")
        
        if stats['size_mb'] > stats['max_size_mb'] * 0.9:
            recommendations.append("Cache nearly full - consider clearing expired entries")
        
        return recommendations
    
    def optimize(self):
        """Optimize cache by removing expired entries and defragmenting"""
        # Clear expired entries
        self.clear_expired()
        
        # Save index
        self._save_cache_index()
        
        return self.get_stats()


class RateLimitCache:
    """Specialized cache for rate limiting information"""
    
    def __init__(self):
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
    
    def record_rate_limit(self, domain: str, status_code: int, 
                         retry_after: int = None):
        """Record rate limit hit for domain"""
        self.rate_limits[domain] = {
            'status_code': status_code,
            'timestamp': datetime.now(),
            'retry_after': retry_after or 60,
            'hit_count': self.rate_limits.get(domain, {}).get('hit_count', 0) + 1
        }
    
    def is_rate_limited(self, domain: str) -> bool:
        """Check if domain is currently rate limited"""
        if domain not in self.rate_limits:
            return False
        
        rate_limit = self.rate_limits[domain]
        wait_until = rate_limit['timestamp'] + timedelta(seconds=rate_limit['retry_after'])
        
        return datetime.now() < wait_until
    
    def get_wait_time(self, domain: str) -> int:
        """Get remaining wait time for rate limited domain"""
        if not self.is_rate_limited(domain):
            return 0
        
        rate_limit = self.rate_limits[domain]
        wait_until = rate_limit['timestamp'] + timedelta(seconds=rate_limit['retry_after'])
        remaining = wait_until - datetime.now()
        
        return max(0, int(remaining.total_seconds()))
    
    def clear_expired(self):
        """Clear expired rate limits"""
        current_time = datetime.now()
        expired_domains = []
        
        for domain, rate_limit in self.rate_limits.items():
            wait_until = rate_limit['timestamp'] + timedelta(seconds=rate_limit['retry_after'])
            if current_time >= wait_until:
                expired_domains.append(domain)
        
        for domain in expired_domains:
            del self.rate_limits[domain]