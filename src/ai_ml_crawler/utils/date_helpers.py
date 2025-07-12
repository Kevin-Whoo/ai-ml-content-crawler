"""
Date helper utilities for the AI/ML content crawler.

This module consolidates all date-related functionality used across different crawlers,
providing a single source of truth for date parsing, filtering, and normalization.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, List
from dateutil import parser as dateutil_parser
from dateutil.tz import tzutc
from bs4 import BeautifulSoup
import json
import logging


logger = logging.getLogger(__name__)


def parse_date_safe(raw_date: str) -> str:
    """
    Parse date string safely and convert to ISO format with UTC timezone.
    
    This function replaces the duplicate _parse_date_safe methods found in multiple crawlers.
    
    Args:
        raw_date: Raw date string in various formats
        
    Returns:
        ISO format string (e.g., "2024-05-13T10:30:00Z") or "Unknown" if parsing fails
    """
    if not raw_date or not isinstance(raw_date, str):
        return "Unknown"
    
    raw_date = raw_date.strip()
    if not raw_date:
        return "Unknown"
    
    # Try dateutil parser first (handles many formats)
    try:
        parsed_date = dateutil_parser.parse(raw_date)
        
        # Convert to UTC if it has timezone info, otherwise assume UTC
        if parsed_date.tzinfo is not None:
            parsed_date = parsed_date.astimezone(tzutc())
        else:
            parsed_date = parsed_date.replace(tzinfo=tzutc())
        
        # Return in ISO Z format
        return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
    except (ValueError, TypeError, OverflowError):
        pass
    
    # Try manual parsing for common formats that dateutil might miss
    date_formats = [
        '%Y-%m-%dT%H:%M:%S%z',  # ISO with timezone
        '%Y-%m-%dT%H:%M:%SZ',   # ISO with Z
        '%Y-%m-%dT%H:%M:%S',    # ISO without timezone
        '%Y-%m-%d %H:%M:%S',    # Standard datetime
        '%Y-%m-%d',             # Date only
        '%B %d, %Y',            # Month day, year
        '%b %d, %Y',            # Short month day, year
        '%d %B %Y',             # Day month year
        '%d %b %Y',             # Day short month year
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(raw_date, fmt)
            dt = dt.replace(tzinfo=tzutc())
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    
    # Try to extract date patterns from the string
    date_str = extract_date_patterns(raw_date)
    if date_str:
        return date_str
    
    # If all parsing fails, return "Unknown"
    return "Unknown"


def extract_date_patterns(text: str) -> Optional[str]:
    """
    Extract date patterns from text using regex.
    
    Args:
        text: Text that might contain date patterns
        
    Returns:
        ISO Z format string or None if no patterns found
    """
    # Pattern for YYYY-MM-DD
    date_pattern = r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b'
    match = re.search(date_pattern, text)
    
    if match:
        try:
            year, month, day = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    # Pattern for MM/DD/YYYY or DD/MM/YYYY
    date_pattern2 = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
    match = re.search(date_pattern2, text)
    
    if match:
        try:
            # Assume MM/DD/YYYY format (US format)
            month, day, year = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    # Pattern for year only (e.g., "2024")
    year_pattern = r'\b(20\d{2})\b'
    match = re.search(year_pattern, text)
    
    if match:
        try:
            year = match.group(1)
            parsed_date = datetime(int(year), 1, 1, tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    return None


def is_recent_date(date_str: Union[str, datetime], max_days_back: int = 365) -> bool:
    """
    Check if a date is within the specified time window.
    
    This function replaces the duplicate _is_recent methods found in multiple crawlers.
    
    Args:
        date_str: Date string or datetime object to check
        max_days_back: Maximum days back to consider recent
        
    Returns:
        bool: True if date is recent or unknown (to avoid filtering out content), False otherwise
    """
    # Handle "Unknown" dates - include them to avoid filtering out content
    if date_str == "Unknown":
        return True
    
    try:
        if isinstance(date_str, datetime):
            post_date = date_str
        else:
            # Try to parse the date string
            parsed = parse_date_safe(date_str)
            if parsed == "Unknown":
                return True  # Include unknown dates
            
            # Parse the ISO format we just created
            post_date = datetime.fromisoformat(parsed.replace('Z', '+00:00'))
        
        # Remove timezone info for comparison
        if post_date.tzinfo is not None:
            post_date = post_date.replace(tzinfo=None)
        
        cutoff_date = datetime.now() - timedelta(days=max_days_back)
        return post_date >= cutoff_date
        
    except (ValueError, TypeError) as e:
        logger.debug(f"Could not parse date {date_str}: {e}")
        return True  # Include when date parsing fails


def extract_date_from_html_element(element, url: str = "") -> str:
    """
    Extract publication date from a BeautifulSoup element.
    
    This consolidates various date extraction strategies used across crawlers.
    
    Args:
        element: BeautifulSoup element (could be article, div, etc.)
        url: URL of the page (for URL-based date extraction)
        
    Returns:
        str: ISO formatted date string or "Unknown"
    """
    date_str = ""
    
    # Strategy 1: Try <time datetime> attribute
    time_elem = element.find('time', attrs={'datetime': True})
    if time_elem:
        date_str = time_elem.get('datetime')
        if date_str:
            return parse_date_safe(date_str)
    
    # Strategy 2: Try meta tags within the element
    meta_properties = [
        'article:published_time',
        'article:modified_time',
        'datePublished',
        'dateCreated',
        'dateModified'
    ]
    
    for prop in meta_properties:
        meta_elem = element.find('meta', property=prop) or element.find('meta', attrs={'name': prop})
        if meta_elem and meta_elem.get('content'):
            date_str = meta_elem.get('content')
            if date_str:
                return parse_date_safe(date_str)
    
    # Strategy 3: Try visible date text in time or date-related elements
    date_elem = element.find(['time', 'span', 'div', 'p'], class_=re.compile(r'date|time|publish|posted', re.I))
    if date_elem:
        date_str = date_elem.get_text(strip=True)
        if date_str:
            parsed = parse_date_safe(date_str)
            if parsed != "Unknown":
                return parsed
    
    # Strategy 4: Try to extract from URL if provided
    if url:
        url_date = extract_date_from_url(url)
        if url_date:
            return url_date
    
    # Strategy 5: Look for date patterns in the text
    text = element.get_text()
    if text:
        date_str = extract_date_patterns(text)
        if date_str:
            return date_str
    
    return "Unknown"


def extract_date_from_url(url: str) -> Optional[str]:
    """
    Extract date from URL path patterns.
    
    Args:
        url: URL to extract date from
        
    Returns:
        ISO Z format string or None if no date found
    """
    if not url:
        return None
    
    # Pattern for /YYYY/MM/DD/
    pattern1 = r'/(\d{4})/(\d{1,2})/(\d{1,2})/'
    match = re.search(pattern1, url)
    
    if match:
        try:
            year, month, day = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    # Pattern for /YYYY/MM/
    pattern2 = r'/(\d{4})/(\d{1,2})/'
    match = re.search(pattern2, url)
    
    if match:
        try:
            year, month = match.groups()
            parsed_date = datetime(int(year), int(month), 1, tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    # Pattern for YYYY-MM-DD in URL
    pattern3 = r'(\d{4})[-](\d{1,2})[-](\d{1,2})'
    match = re.search(pattern3, url)
    
    if match:
        try:
            year, month, day = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    return None


def extract_date_from_json_ld(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract date from JSON-LD structured data in the page.
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        ISO formatted date string or None
    """
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    for script in json_ld_scripts:
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
                            parsed = parse_date_safe(item[field])
                            if parsed != "Unknown":
                                return parsed
        
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
    
    return None


def normalize_date_format(date_str: str) -> str:
    """
    Normalize any date string to a consistent ISO format.
    
    Args:
        date_str: Date string in any format
        
    Returns:
        str: ISO formatted date or "Unknown"
    """
    return parse_date_safe(date_str)


def get_current_iso_date() -> str:
    """
    Get current date in ISO Z format.
    
    Returns:
        str: Current date in ISO format
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class DateExtractionHelper:
    """
    Helper class that can be used as a mixin or standalone for date extraction.
    
    This provides backwards compatibility for crawlers using the DateExtractionMixin.
    """
    
    @staticmethod
    def extract_publication_date(soup_or_element, url: str = "") -> str:
        """
        Extract publication date from webpage content.
        
        Args:
            soup_or_element: BeautifulSoup object or element
            url: URL of the webpage
            
        Returns:
            str: ISO formatted date string or "Unknown"
        """
        # If it's a full soup, try JSON-LD first
        if hasattr(soup_or_element, 'find_all'):
            json_ld_date = extract_date_from_json_ld(soup_or_element)
            if json_ld_date:
                return json_ld_date
        
        # Then try element-based extraction
        return extract_date_from_html_element(soup_or_element, url)
    
    @staticmethod
    def is_content_recent(date_str: str, max_days_back: int = 365) -> bool:
        """
        Check if content date is within the specified time window.
        
        Args:
            date_str: Date string to check
            max_days_back: Maximum days to consider recent
            
        Returns:
            bool: True if content is recent
        """
        return is_recent_date(date_str, max_days_back)
