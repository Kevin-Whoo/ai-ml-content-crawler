"""
GitHub repository crawler for AI/ML projects
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .base_crawler import BaseCrawler


class GitHubCrawler(BaseCrawler):
    """Crawler for GitHub repositories related to multimodal LLMs and AI agents"""
    
    def __init__(self, config, github_config):
        super().__init__(config)
        self.api_base = "https://api.github.com"
        self.github_config = github_config
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": config.user_agent
        }
        if config.github_token:
            self.headers["Authorization"] = f"token {config.github_token}"
    
    async def crawl(self) -> List[Dict[str, Any]]:
        """Crawl GitHub repositories"""
        results = []
        
        # Search for repositories using different queries
        search_queries = self.github_config.get("search_queries", [])
        
        for query in search_queries:
            repos = await self._search_repositories(query)
            results.extend(repos)
            
            # Avoid rate limiting
            await asyncio.sleep(self.config.request_delay)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for repo in results:
            if repo['url'] not in seen_urls:
                seen_urls.add(repo['url'])
                unique_results.append(repo)
        
        await self.close()
        return unique_results[:self.config.max_results_per_source]
    
    async def _search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories"""
        search_url = f"{self.api_base}/search/repositories"
        
        # Build search parameters
        params = {
            'q': f"{query} language:python",
            'sort': 'updated',
            'order': 'desc',
            'per_page': 30
        }
        
        # Add minimum stars filter
        if "min_stars" in self.github_config:
            params['q'] += f" stars:>{self.github_config['min_stars']}"
        
        # Construct URL with parameters
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{search_url}?{param_str}"
        
        try:
            session = await self._get_session()
            async with session.get(full_url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_repositories(data.get('items', []))
                elif response.status == 403:
                    print(f"⚠️  GitHub API rate limit exceeded for query: {query}")
                    return []
                else:
                    print(f"⚠️  GitHub API error {response.status} for query: {query}")
                    return []
        except Exception as e:
            print(f"❌ Error searching GitHub for '{query}': {str(e)}")
            return []
    
    async def _parse_repositories(self, repos: List[Dict]) -> List[Dict[str, Any]]:
        """Parse repository data from GitHub API"""
        results = []
        
        for repo in repos:
            try:
                # Check if repository was created recently
                created_at = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                if not self._is_recent(created_at):
                    continue
                
                # Extract repository information
                title = repo['full_name']
                url = repo['html_url']
                description = repo.get('description', '') or ''
                
                # Get additional metrics
                stars = repo.get('stargazers_count', 0)
                forks = repo.get('forks_count', 0)
                language = repo.get('language', '')
                
                # Extract topics/tags
                topics = repo.get('topics', [])
                tags = ['github', 'repository'] + topics + ([language.lower()] if language else [])
                
                # Create summary with metrics
                summary = f"{description}\n\n⭐ {stars} stars | 🍴 {forks} forks"
                if language:
                    summary += f" | 📝 {language}"
                
                repo_item = self._create_item(
                    title=title,
                    url=url,
                    date=repo['created_at'],
                    summary=summary,
                    content=description,
                    source="GitHub",
                    tags=tags
                )
                
                # Add additional metadata
                repo_item.update({
                    'stars': stars,
                    'forks': forks,
                    'language': language,
                    'topics': topics,
                    'owner': repo['owner']['login'],
                    'created_at': repo['created_at'],
                    'last_updated': repo['updated_at']
                })
                
                results.append(repo_item)
                
            except Exception as e:
                print(f"⚠️  Error parsing repository: {str(e)}")
                continue
        
        return results