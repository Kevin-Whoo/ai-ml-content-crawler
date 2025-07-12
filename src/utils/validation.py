"""
Input validation and sanitization utilities for secure web crawling
"""

import re
import urllib.parse
from typing import List, Optional, Set
from ipaddress import ip_address, AddressValueError


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Allowed domains for SSRF protection
    ALLOWED_DOMAINS = {
        'anthropic.com', 'www.anthropic.com',
        'openai.com', 'www.openai.com',
        'ai.meta.com', 'meta.com',
        'github.com', 'api.github.com',
        'huggingface.co', 'www.huggingface.co',
        'medium.com', 'www.medium.com', 'towardsdatascience.com',
        'scholar.google.com', 'scholar.google.co.uk',
        'arxiv.org', 'export.arxiv.org',
        'ieeexplore.ieee.org', 'ieee.org'
    }
    
    # Blocked IP ranges (RFC 1918 private networks + localhost)
    BLOCKED_IP_PATTERNS = [
        r'^127\.',          # localhost
        r'^10\.',           # 10.0.0.0/8
        r'^192\.168\.',     # 192.168.0.0/16
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',  # 172.16.0.0/12
        r'^169\.254\.',     # link-local
        r'^::1$',           # IPv6 localhost
        r'^fc00:',          # IPv6 private
        r'^fe80:',          # IPv6 link-local
    ]
    
    def __init__(self):
        self.blocked_ip_regex = re.compile('|'.join(self.BLOCKED_IP_PATTERNS))
    
    def validate_url(self, url: str, allow_redirects: bool = True) -> str:
        """
        Validate and sanitize URL for SSRF protection
        
        Args:
            url: URL to validate
            allow_redirects: Whether to allow redirects
            
        Returns:
            Sanitized URL
            
        Raises:
            ValidationError: If URL is invalid or blocked
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string")
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url.strip())
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {e}")
        
        # Require HTTPS for security (except for specific allowed HTTP APIs)
        if parsed.scheme not in ['https', 'http']:
            raise ValidationError("Only HTTP/HTTPS URLs are allowed")
        
        # Allow HTTP only for specific trusted APIs
        if parsed.scheme == 'http':
            if parsed.netloc not in ['export.arxiv.org']:
                raise ValidationError("HTTP only allowed for specific trusted APIs")
        
        # Validate domain
        if not parsed.netloc:
            raise ValidationError("URL must have a valid domain")
        
        # Extract hostname (remove port if present)
        hostname = parsed.netloc.split(':')[0].lower()
        
        # Check if domain is in allowlist
        if not self._is_domain_allowed(hostname):
            raise ValidationError(f"Domain '{hostname}' is not in allowlist")
        
        # Check for IP addresses and block private ranges
        if self._is_ip_address(hostname):
            if self._is_blocked_ip(hostname):
                raise ValidationError(f"Access to IP address '{hostname}' is blocked")
        
        # Reconstruct clean URL
        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment for security
        ))
        
        return clean_url
    
    def sanitize_search_query(self, query: str, max_length: int = 200) -> str:
        """
        Sanitize search query to prevent injection attacks
        
        Args:
            query: Search query to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized query
            
        Raises:
            ValidationError: If query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
        
        # Remove leading/trailing whitespace
        query = query.strip()
        
        if len(query) > max_length:
            raise ValidationError(f"Query too long (max {max_length} characters)")
        
        # Remove potentially dangerous characters
        # Allow alphanumeric, spaces, common punctuation
        allowed_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.,!?(){}[\]"\']+$')
        if not allowed_pattern.match(query):
            raise ValidationError("Query contains invalid characters")
        
        # URL encode for safe inclusion in URLs
        return urllib.parse.quote_plus(query)
    
    def validate_keywords(self, keywords: List[str]) -> List[str]:
        """
        Validate and sanitize keyword list
        
        Args:
            keywords: List of keywords to validate
            
        Returns:
            List of sanitized keywords
        """
        if not isinstance(keywords, list):
            raise ValidationError("Keywords must be a list")
        
        sanitized = []
        for keyword in keywords:
            if isinstance(keyword, str) and keyword.strip():
                # Basic sanitization
                clean_keyword = re.sub(r'[^\w\s\-]', '', keyword.strip()).lower()
                if clean_keyword and len(clean_keyword) <= 50:
                    sanitized.append(clean_keyword)
        
        return sanitized
    
    def validate_content(self, content: str, max_length: int = 50000) -> str:
        """
        Validate scraped content for safety
        
        Args:
            content: Content to validate
            max_length: Maximum allowed length
            
        Returns:
            Validated content
            
        Raises:
            ValidationError: If content is unsafe
        """
        if not isinstance(content, str):
            return ""
        
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        # Remove potentially dangerous patterns
        # This is basic protection - could be enhanced based on specific needs
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript
            r'javascript:',               # JavaScript URLs
            r'data:.*base64',            # Data URLs with base64
            r'vbscript:',                # VBScript
        ]
        
        for pattern in dangerous_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content.strip()
    
    def _is_domain_allowed(self, hostname: str) -> bool:
        """Check if domain is in allowlist"""
        # Direct match
        if hostname in self.ALLOWED_DOMAINS:
            return True
        
        # Check subdomains
        parts = hostname.split('.')
        for i in range(len(parts)):
            domain = '.'.join(parts[i:])
            if domain in self.ALLOWED_DOMAINS:
                return True
        
        return False
    
    def _is_ip_address(self, hostname: str) -> bool:
        """Check if hostname is an IP address"""
        try:
            ip_address(hostname)
            return True
        except (AddressValueError, ValueError):
            return False
    
    def _is_blocked_ip(self, ip_str: str) -> bool:
        """Check if IP address is in blocked ranges"""
        return bool(self.blocked_ip_regex.search(ip_str))


class URLRedirectValidator:
    """Validate URL redirects to prevent SSRF"""
    
    def __init__(self, validator: InputValidator, max_redirects: int = 5):
        self.validator = validator
        self.max_redirects = max_redirects
        self.redirect_count = 0
    
    def validate_redirect(self, url: str) -> str:
        """
        Validate redirect URL
        
        Args:
            url: Redirect URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If redirect is invalid or exceeds limit
        """
        self.redirect_count += 1
        
        if self.redirect_count > self.max_redirects:
            raise ValidationError(f"Too many redirects (max {self.max_redirects})")
        
        return self.validator.validate_url(url)
    
    def reset(self):
        """Reset redirect counter"""
        self.redirect_count = 0