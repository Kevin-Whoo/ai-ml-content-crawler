"""
ArXiv research papers crawler for AI+Energy domain
"""

import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime, timedelta
import urllib.parse

from .base_crawler import BaseCrawler


class ArxivCrawler(BaseCrawler):
    """Crawler for ArXiv research papers focusing on AI+Energy"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_base = "http://export.arxiv.org/api/query"
    
    async def crawl(self) -> List[Dict[str, Any]]:
        # TODO: Add date filtering - filter items by self._is_recent(date) -> List[Dict[str, Any]]:
        """Crawl ArXiv papers"""
        results = []
        
        # Energy AI focused search queries
        search_queries = [
            "energy AND (artificial intelligence OR machine learning OR AI)",
            "smart grid AND (AI OR machine learning OR deep learning)",
            "power systems AND (AI OR neural network OR optimization)",
            "renewable energy AND (forecasting OR prediction OR AI)",
            "energy management AND (agent OR AI OR automation)",
            "microgrid AND (AI OR machine learning OR control)",
            "energy storage AND (optimization OR AI OR prediction)",
            "demand response AND (AI OR machine learning OR smart)"
        ]
        
        for query in search_queries:
            papers = await self._search_papers(query)
            results.extend(papers)
            await asyncio.sleep(self.config.request_delay)
        
        # Remove duplicates based on arxiv ID
        seen_ids = set()
        unique_results = []
        for paper in results:
            paper_id = paper.get('arxiv_id', '')
            if paper_id and paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_results.append(paper)
        
        await self.close()
        return unique_results[:self.config.max_results_per_source]
    
    async def _search_papers(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search ArXiv papers by query"""
        # Calculate date range for recent papers
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.max_days_back)
        
        # Build ArXiv API query
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.api_base}?{query_string}"
        
        content = await self._fetch_url(url)
        if not content:
            return []
        
        return self._parse_arxiv_response(content, start_date)
    
    def _parse_arxiv_response(self, xml_content: str, start_date: datetime) -> List[Dict[str, Any]]:
        """Parse ArXiv API XML response"""
        papers = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom',
                        'arxiv': 'http://arxiv.org/schemas/atom'}
            
            entries = root.findall('atom:entry', namespace)
            
            for entry in entries:
                try:
                    # Extract paper details
                    title_elem = entry.find('atom:title', namespace)
                    title = title_elem.text.strip() if title_elem is not None else ""
                    
                    # Clean up title (remove newlines and extra spaces)
                    title = ' '.join(title.split())
                    
                    # Extract ArXiv ID and URL
                    id_elem = entry.find('atom:id', namespace)
                    arxiv_url = id_elem.text if id_elem is not None else ""
                    arxiv_id = arxiv_url.split('/')[-1] if arxiv_url else ""
                    
                    # Extract published date
                    published_elem = entry.find('atom:published', namespace)
                    published_date = ""
                    if published_elem is not None:
                        published_date = published_elem.text.split('T')[0]  # Get date part only
                        
                        # Check if paper is recent enough
                        try:
                            paper_date = datetime.strptime(published_date, '%Y-%m-%d')
                            if paper_date < start_date:
                                continue  # Skip old papers
                        except ValueError:
                            pass  # Include if we can't parse date
                    
                    # Extract summary/abstract
                    summary_elem = entry.find('atom:summary', namespace)
                    summary = summary_elem.text.strip() if summary_elem is not None else ""
                    
                    # Clean summary
                    summary = ' '.join(summary.split())
                    if len(summary) > 500:
                        summary = summary[:497] + "..."
                    
                    # Extract authors
                    authors = []
                    author_elems = entry.findall('atom:author', namespace)
                    for author_elem in author_elems:
                        name_elem = author_elem.find('atom:name', namespace)
                        if name_elem is not None:
                            authors.append(name_elem.text)
                    
                    # Extract categories
                    categories = []
                    category_elems = entry.findall('atom:category', namespace)
                    for cat_elem in category_elems:
                        term = cat_elem.get('term')
                        if term:
                            categories.append(term)
                    
                    # Skip if no meaningful content
                    if not title or not arxiv_url:
                        continue
                    
                    paper = self._create_item(
                        title=title,
                        url=arxiv_url,
                        date=published_date,
                        summary=summary,
                        source="ArXiv",
                        tags=["arxiv", "research", "paper"] + categories[:3]
                    )
                    
                    # Add ArXiv specific metadata
                    paper['arxiv_id'] = arxiv_id
                    paper['authors'] = authors[:5]  # Limit to first 5 authors
                    paper['categories'] = categories
                    
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing ArXiv entry: {str(e)}")
                    continue
                    
        except ET.ParseError as e:
            print(f"⚠️  Error parsing ArXiv XML: {str(e)}")
        
        return papers