"""
Date utility functions for parsing and normalizing dates from various sources.
"""

import re
from datetime import datetime, timezone
from typing import Optional, Union
from dateutil import parser as dateutil_parser
from dateutil.tz import tzutc


def parse_iso_or_fuzzy(date_string: str) -> Optional[str]:
    """
    Parse a date string from various formats and return ISO Z string.
    
    Handles:
    - ISO 8601 formats (e.g., "2024-05-13T10:30:00Z", "2024-05-13")
    - GitHub API dates (e.g., "2025-07-12T13:20:40Z")
    - HTML time elements (e.g., "2024-05-13T10:30:00")
    - Meta tag dates (e.g., "2024-05-13T10:30:00+00:00")
    - JSON-LD datePublished (e.g., "2024-05-13")
    - Fuzzy date strings (e.g., "May 13, 2024", "13 May 2024")
    
    Args:
        date_string: The date string to parse
        
    Returns:
        ISO Z format string (e.g., "2024-05-13T10:30:00Z") or None if parsing fails
    """
    if not date_string or not isinstance(date_string, str):
        return None
    
    date_string = date_string.strip()
    if not date_string:
        return None
    
    try:
        # First try to parse as ISO 8601 or common formats
        parsed_date = dateutil_parser.parse(date_string)
        
        # Convert to UTC if it has timezone info, otherwise assume UTC
        if parsed_date.tzinfo is not None:
            parsed_date = parsed_date.astimezone(tzutc())
        else:
            parsed_date = parsed_date.replace(tzinfo=tzutc())
        
        # Return in ISO Z format
        return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
    except (ValueError, TypeError, OverflowError):
        # Try to extract date patterns from the string
        return _extract_date_patterns(date_string)


def _extract_date_patterns(text: str) -> Optional[str]:
    """
    Extract date patterns from text using regex.
    
    Args:
        text: Text that might contain date patterns
        
    Returns:
        ISO Z format string or None if no patterns found
    """
    # Pattern for YYYY-MM-DD
    date_pattern = r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b'
    match = re.search(date_pattern, text)
    
    if match:
        try:
            year, month, day = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    # Pattern for MM/DD/YYYY or DD/MM/YYYY
    date_pattern2 = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
    match = re.search(date_pattern2, text)
    
    if match:
        try:
            # Assume MM/DD/YYYY format (US format)
            month, day, year = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    return None


def to_utc_iso(dt: Union[datetime, str]) -> str:
    """
    Convert a datetime object or string to UTC ISO Z format.
    
    Args:
        dt: datetime object or ISO string
        
    Returns:
        ISO Z format string (e.g., "2024-05-13T10:30:00Z")
        
    Raises:
        ValueError: If the input cannot be converted
    """
    if isinstance(dt, str):
        # Parse string first
        try:
            dt = dateutil_parser.parse(dt)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot parse date string: {dt}") from e
    
    if not isinstance(dt, datetime):
        raise ValueError(f"Expected datetime object or string, got {type(dt)}")
    
    # Convert to UTC if it has timezone info, otherwise assume UTC
    if dt.tzinfo is not None:
        dt = dt.astimezone(tzutc())
    else:
        dt = dt.replace(tzinfo=tzutc())
    
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_date_from_html(html_content: str) -> Optional[str]:
    """
    Extract publication date from HTML content using common patterns.
    
    Looks for:
    - <time datetime="..."> elements
    - <meta property="article:published_time" content="..."> tags
    - JSON-LD datePublished fields
    - URL path date patterns
    
    Args:
        html_content: HTML content to search
        
    Returns:
        ISO Z format string or None if no date found
    """
    from bs4 import BeautifulSoup
    import json
    
    if not html_content:
        return None
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try <time> elements with datetime attribute
        time_elements = soup.find_all('time', attrs={'datetime': True})
        for time_elem in time_elements:
            datetime_attr = time_elem.get('datetime')
            if datetime_attr:
                parsed_date = parse_iso_or_fuzzy(datetime_attr)
                if parsed_date:
                    return parsed_date
        
        # Try meta tags
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]',
            'meta[name="date"]',
            'meta[name="article:published_time"]',
            'meta[property="article:published"]',
            'meta[name="pubdate"]'
        ]
        
        for selector in meta_selectors:
            meta_elem = soup.select_one(selector)
            if meta_elem:
                content = meta_elem.get('content')
                if content:
                    parsed_date = parse_iso_or_fuzzy(content)
                    if parsed_date:
                        return parsed_date
        
        # Try JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    for item in data:
                        date_published = item.get('datePublished')
                        if date_published:
                            parsed_date = parse_iso_or_fuzzy(date_published)
                            if parsed_date:
                                return parsed_date
                elif isinstance(data, dict):
                    date_published = data.get('datePublished')
                    if date_published:
                        parsed_date = parse_iso_or_fuzzy(date_published)
                        if parsed_date:
                            return parsed_date
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Try searching for date patterns in the HTML text
        text_content = soup.get_text()
        return _extract_date_patterns(text_content)
        
    except Exception:
        return None


def extract_date_from_url(url: str) -> Optional[str]:
    """
    Extract date from URL path patterns.
    
    Looks for patterns like:
    - /2024/05/13/title
    - /2024/05/title
    - /blog/2024-05-13-title
    
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
    pattern3 = r'(\d{4})-(\d{1,2})-(\d{1,2})'
    match = re.search(pattern3, url)
    
    if match:
        try:
            year, month, day = match.groups()
            parsed_date = datetime(int(year), int(month), int(day), tzinfo=tzutc())
            return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    
    return None
