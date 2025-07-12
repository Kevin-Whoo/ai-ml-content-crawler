"""
Helper functions for improved blog crawling
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class BlogCrawlerHelper:
    """Helper class for extracting blog content from modern websites"""
    
    @staticmethod
    def find_blog_posts(soup: BeautifulSoup, domain: str) -> List[Dict[str, Any]]:
        """Find blog posts using domain-specific strategies"""
        
        if 'openai.com' in domain:
            return BlogCrawlerHelper._find_openai_posts(soup)
        elif 'anthropic.com' in domain:
            return BlogCrawlerHelper._find_anthropic_posts(soup)
        elif 'ai.meta.com' in domain:
            return BlogCrawlerHelper._find_meta_posts(soup)
        elif 'medium.com' in domain:
            return BlogCrawlerHelper._find_medium_posts(soup)
        else:
            return BlogCrawlerHelper._find_generic_posts(soup)
    
    @staticmethod
    def _find_openai_posts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract OpenAI blog posts"""
        posts = []
        
        # Strategy 1: Look for JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['BlogPosting', 'Article']:
                            posts.append({
                                'title': item.get('headline', ''),
                                'url': item.get('url', ''),
                                'date': item.get('datePublished', ''),
                                'summary': item.get('description', '')
                            })
            except:
                continue
        
        # Strategy 2: Look for links with recent keywords
        if not posts:
            recent_keywords = [
                'gpt-4o', 'o1', 'sora', 'dall-e-3', 'chatgpt', 'openai-api',
                'multimodal', 'reasoning', 'safety', 'alignment', 'announcement'
            ]
            
            links = soup.find_all('a', href=re.compile(r'/(blog|news|research)/'))
            for link in links:
                text = link.get_text().lower()
                href = link.get('href', '')
                
                if any(keyword in text for keyword in recent_keywords):
                    posts.append({
                        'title': link.get_text().strip(),
                        'url': href if href.startswith('http') else f"https://openai.com{href}",
                        'date': datetime.now().isoformat(),
                        'summary': text[:200]
                    })
        
        return posts[:10]
    
    @staticmethod
    def _find_anthropic_posts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Anthropic blog posts"""
        posts = []
        
        # Look for Claude/Anthropic specific content
        recent_keywords = [
            'claude-3', 'claude-3.5', 'sonnet', 'haiku', 'opus', 'constitutional-ai',
            'anthropic', 'safety', 'harmlessness', 'helpful', 'announcement'
        ]
        
        # Try different selector strategies
        selectors = [
            'a[href*="/news/"]',
            'a[href*="/research/"]',
            'article a',
            '.post-link',
            '.news-item a'
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    text = link.get_text().lower()
                    href = link.get('href', '')
                    
                    if any(keyword in text for keyword in recent_keywords):
                        posts.append({
                            'title': link.get_text().strip(),
                            'url': href if href.startswith('http') else f"https://www.anthropic.com{href}",
                            'date': datetime.now().isoformat(),
                            'summary': text[:200]
                        })
                        
                if posts:
                    break
            except:
                continue
        
        return posts[:10]
    
    @staticmethod
    def _find_meta_posts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Meta AI blog posts"""
        posts = []
        
        recent_keywords = [
            'llama', 'llama-2', 'llama-3', 'meta-ai', 'pytorch', 'fairseq',
            'multimodal', 'embodied-ai', 'metaverse', 'announcement', 'release'
        ]
        
        links = soup.find_all('a', href=re.compile(r'/(blog|research|news)/'))
        for link in links:
            text = link.get_text().lower()
            href = link.get('href', '')
            
            if any(keyword in text for keyword in recent_keywords):
                posts.append({
                    'title': link.get_text().strip(),
                    'url': href if href.startswith('http') else f"https://ai.meta.com{href}",
                    'date': datetime.now().isoformat(),
                    'summary': text[:200]
                })
        
        return posts[:10]
    
    @staticmethod
    def _find_medium_posts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Medium posts"""
        posts = []
        
        # Medium has specific article structure
        articles = soup.find_all(['article', 'div'], attrs={'data-testid': re.compile(r'post|article')})
        
        for article in articles:
            try:
                title_elem = article.find(['h1', 'h2', 'h3'])
                link_elem = article.find('a')
                
                if title_elem and link_elem:
                    posts.append({
                        'title': title_elem.get_text().strip(),
                        'url': link_elem.get('href', ''),
                        'date': datetime.now().isoformat(),
                        'summary': ''
                    })
            except:
                continue
        
        return posts[:10]
    
    @staticmethod
    def _find_generic_posts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Generic blog post extraction"""
        posts = []
        
        # Look for common blog patterns
        selectors = [
            'article h2 a, article h3 a',
            '.post-title a',
            '.entry-title a',
            'h2 a[href*="blog"], h3 a[href*="blog"]',
            '.blog-post a',
            'a[href*="/20"]'  # Date-based URLs
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    posts.append({
                        'title': link.get_text().strip(),
                        'url': link.get('href', ''),
                        'date': datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                if posts:
                    break
            except:
                continue
        
        return posts[:10]
    
    @staticmethod
    def extract_recent_releases(text: str) -> List[str]:
        """Extract mentions of recent releases from text"""
        release_patterns = [
            r'(gpt-4o|gpt-4|claude-3\.5|claude-3|llama-3|gemini)',
            r'(announcing|released|introducing|launch)',
            r'(version \d+\.\d+|v\d+\.\d+)',
            r'(beta|alpha|preview|early access)',
            r'(multimodal|vision|reasoning|safety)'
        ]
        
        releases = []
        for pattern in release_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            releases.extend(matches)
        
        return list(set(releases))