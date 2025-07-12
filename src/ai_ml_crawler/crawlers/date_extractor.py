"""Date extraction helper for blog crawlers

This module provides utilities to extract publication dates from various HTML sources
including <time> elements, meta tags, and JSON-LD structured data.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from dateutil import parser
import logging


class DateExtractor:
    """Helper class for extracting publication dates from web content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_publication_date(self, soup: BeautifulSoup, url: str = "") -> str:
        """Extract publication date from various HTML sources
        
        Args:
            soup: BeautifulSoup object of the webpage
            url: URL of the webpage (for URL-based date extraction)
            
        Returns:
            str: ISO 8601 formatted date string or "Unknown" if no date found
        """
        
        # Try multiple extraction methods in order of reliability
        methods = [
            self._extract_from_time_element,
            self._extract_from_meta_tags,
            self._extract_from_json_ld,
            self._extract_from_url,
            self._extract_from_content_patterns
        ]
        
        for method in methods:
            try:
                date_str = method(soup, url)
                if date_str:
                    # Parse and normalize the date
                    normalized_date = self._normalize_date(date_str)
                    if normalized_date:
                        self.logger.debug(f"Extracted date '{normalized_date}' using {method.__name__}")
                        return normalized_date
            except Exception as e:
                self.logger.debug(f"Date extraction method {method.__name__} failed: {e}")
                continue
        
        self.logger.debug("No publication date found, returning 'Unknown'")
        return "Unknown"
    
    def _extract_from_time_element(self, soup: BeautifulSoup, url: str = "") -> Optional[str]:
        """Extract date from <time> elements"""
        
        # Look for time elements with datetime attribute
        time_elements = soup.find_all('time', attrs={'datetime': True})
        
        for time_elem in time_elements:
            datetime_attr = time_elem.get('datetime')
            if datetime_attr:
                # Check if this looks like a publication date
                if self._is_publication_date_element(time_elem):
                    return datetime_attr
        
        # Fallback: any time element with datetime
        if time_elements:
            return time_elements[0].get('datetime')
        
        return None
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup, url: str = "") -> Optional[str]:
        """Extract date from meta tags"""
        
        meta_properties = [
            'article:published_time',
            'article:modified_time',
            'og:updated_time',
            'og:published_time',
            'date',
            'pubdate',
            'publishedDate',
            'datePublished'
        ]
        
        for prop in meta_properties:
            # Try property attribute
            meta_tag = soup.find('meta', property=prop)
            if meta_tag and meta_tag.get('content'):
                return meta_tag.get('content')
            
            # Try name attribute
            meta_tag = soup.find('meta', attrs={'name': prop})
            if meta_tag and meta_tag.get('content'):
                return meta_tag.get('content')
        
        return None
    
    def _extract_from_json_ld(self, soup: BeautifulSoup, url: str = "") -> Optional[str]:
        """Extract date from JSON-LD structured data"""
        
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                if not script.string:
                    continue
                    
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    # Check for article/blog post types
                    item_type = item.get('@type', '')
                    if item_type in ['BlogPosting', 'Article', 'NewsArticle']:
                        # Try various date fields
                        date_fields = ['datePublished', 'dateCreated', 'dateModified']
                        for field in date_fields:
                            if item.get(field):
                                return item[field]
            
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                self.logger.debug(f"JSON-LD parsing error: {e}")
                continue
        
        return None
    
    def _extract_from_url(self, soup: BeautifulSoup, url: str = "") -> Optional[str]:
        """Extract date from URL patterns"""
        
        if not url:
            return None
        
        # Common URL date patterns
        patterns = [
            r'/(\d{4})/(\d{1,2})/(\d{1,2})/',  # /2024/03/15/
            r'/(\d{4})-(\d{1,2})-(\d{1,2})',   # /2024-03-15
            r'/(\d{4})/(\d{1,2})/',            # /2024/03/
            r'/(\d{4})/'                        # /2024/
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    if len(match.groups()) >= 3:
                        year, month, day = match.groups()[:3]
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    elif len(match.groups()) == 2:
                        year, month = match.groups()
                        return f"{year}-{month.zfill(2)}-01"
                    elif len(match.groups()) == 1:
                        year = match.groups()[0]
                        return f"{year}-01-01"
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_from_content_patterns(self, soup: BeautifulSoup, url: str = "") -> Optional[str]:
        """Extract date from content text patterns"""
        
        # Look for date patterns in specific elements
        date_containers = soup.find_all(['span', 'div', 'p'], 
                                      class_=re.compile(r'date|time|publish|post-date', re.I))
        
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',           # 2024-03-15
            r'(\d{1,2})/(\d{1,2})/(\d{4})',           # 03/15/2024
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',         # 15.03.2024
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',  # January 24, 2024
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})',  # Jan 24, 2024
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',     # 24 January 2024
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',     # 24 Jan 2024
        ]
        
        for container in date_containers:
            text = container.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    try:
                        # Try to parse the matched date
                        date_obj = parser.parse(match.group(0))
                        return date_obj.isoformat()[:10]  # Return just the date part
                    except (ValueError, parser.ParserError):
                        continue
        
        return None
    
    def _is_publication_date_element(self, time_elem) -> bool:
        """Check if a time element likely contains a publication date"""
        
        # Check class names for publication-related terms
        classes = time_elem.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
        
        publication_indicators = ['publish', 'post', 'date', 'created', 'article']
        
        for class_name in classes:
            if any(indicator in class_name.lower() for indicator in publication_indicators):
                return True
        
        # Check parent elements for context
        parent = time_elem.parent
        if parent and parent.name:
            parent_text = parent.get_text().lower()
            if any(indicator in parent_text for indicator in publication_indicators):
                return True
        
        return False
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO 8601 format
        
        Args:
            date_str: Raw date string from HTML
            
        Returns:
            str: ISO 8601 formatted date (UTC) or None if parsing fails
        """
        
        if not date_str or not isinstance(date_str, str):
            return None
        
        # Clean up the date string
        date_str = date_str.strip()
        
        # Skip if it looks like a current timestamp (contains today's date)
        today = datetime.now().strftime('%Y-%m-%d')
        if date_str.startswith(today):
            return None
        
        try:
            # Parse the date using dateutil
            parsed_date = parser.parse(date_str)
            
            # Convert to UTC if timezone-aware
            if parsed_date.tzinfo is not None:
                parsed_date = parsed_date.astimezone(timezone.utc)
            
            # Return ISO format (date only for simplicity)
            return parsed_date.strftime('%Y-%m-%d')
            
        except (ValueError, TypeError, parser.ParserError) as e:
            self.logger.debug(f"Date parsing failed for '{date_str}': {e}")
            return None
    
    def is_recent_date(self, date_str: str, max_days_back: int = 365) -> bool:
        """Check if a date is within the specified time window
        
        Args:
            date_str: Date string to check
            max_days_back: Maximum days back to consider recent
            
        Returns:
            bool: True if date is recent, False otherwise
        """
        
        if not date_str or date_str == "Unknown":
            return False
        
        try:
            parsed_date = parser.parse(date_str)
            cutoff_date = datetime.now() - timedelta(days=max_days_back)
            
            # Make both dates timezone-naive for comparison
            if parsed_date.tzinfo is not None:
                parsed_date = parsed_date.replace(tzinfo=None)
            
            if cutoff_date.tzinfo is not None:
                cutoff_date = cutoff_date.replace(tzinfo=None)
            
            return parsed_date.date() >= cutoff_date.date()
            
        except (ValueError, TypeError, parser.ParserError):
            return False


class DateExtractionMixin:
    """Mixin class to add date extraction capabilities to crawlers"""
    
    @property
    def date_extractor(self):
        """Lazy initialization of date extractor"""
        if not hasattr(self, '_date_extractor'):
            self._date_extractor = DateExtractor()
        return self._date_extractor
    
    def extract_publication_date(self, soup: BeautifulSoup, url: str = "") -> str:
        """Extract publication date from webpage content
        
        Args:
            soup: BeautifulSoup object of the webpage
            url: URL of the webpage
            
        Returns:
            str: ISO 8601 formatted date string or "Unknown"
        """
        return self.date_extractor.extract_publication_date(soup, url)
    
    def is_content_recent(self, date_str: str) -> bool:
        """Check if content date is within configured time window
        
        Args:
            date_str: Date string to check
            
        Returns:
            bool: True if content is recent
        """
        max_days = getattr(self.config, 'max_days_back', 365)
        return self.date_extractor.is_recent_date(date_str, max_days)
