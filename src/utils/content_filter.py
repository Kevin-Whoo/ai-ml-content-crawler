"""
Content filtering and relevance ranking system
"""

import re
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta

from config import CrawlerConfig


class ContentFilter:
    """Filter and rank content based on relevance to multimodal LLMs and AI agents"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.multimodal_keywords = set(keyword.lower() for keyword in config.multimodal_keywords)
        self.ai_agent_keywords = set(keyword.lower() for keyword in config.ai_agent_keywords)
        self.energy_ai_keywords = set(keyword.lower() for keyword in config.energy_ai_keywords)
        
        # Additional high-value keywords
        self.high_value_keywords = {
            'gpt-4o', 'gpt-4v', 'claude-3', 'gemini pro vision', 'dall-e 3',
            'midjourney', 'stable diffusion', 'llava', 'blip', 'flamingo',
            'palm-e', 'kosmos', 'bard', 'chatgpt', 'copilot', 'langchain',
            'autogen', 'crewai', 'semantic kernel', 'llm', 'transformer',
            'attention mechanism', 'reinforcement learning', 'fine-tuning'
        }
        
        # Company/organization keywords for boosting
        self.company_keywords = {
            'openai', 'anthropic', 'meta', 'google', 'microsoft', 'deepmind',
            'hugging face', 'nvidia', 'stability ai', 'cohere', 'inflection'
        }
    
    def filter_content(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank content items by relevance"""
        filtered_items = []
        
        for item in items:
            # Calculate relevance score
            score = self._calculate_relevance_score(item)
            
            # Only include items with minimum relevance
            if score > 0:
                item['relevance_score'] = score
                item['relevance_reasons'] = self._get_relevance_reasons(item)
                filtered_items.append(item)
        
        # Sort by relevance score (highest first)
        filtered_items.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_items
    
    def _calculate_relevance_score(self, item: Dict[str, Any]) -> float:
        """Calculate relevance score for an item - optimized version"""
        score = 0.0
        
        # Efficiently combine text content
        text_parts = []
        if item.get('title'):
            text_parts.append(item['title'])
        if item.get('summary'):
            text_parts.append(item['summary'])
        if item.get('content'):
            text_parts.append(item['content'])
        if item.get('tags'):
            text_parts.extend(item['tags'])
        
        text_content = ' '.join(text_parts).lower()
        
        # Single pass keyword matching for efficiency
        keyword_matches = self._count_all_keyword_matches(text_content)
        
        # Apply weights
        score += keyword_matches['multimodal'] * 2.0
        score += keyword_matches['ai_agent'] * 2.0
        score += keyword_matches['energy_ai'] * 2.5
        score += keyword_matches['high_value'] * 1.5
        score += keyword_matches['company'] * 1.0
        
        # Boost content from major AI companies
        source = item.get('source', '').lower()
        if any(company in source for company in ['openai', 'anthropic', 'meta']):
            score += 2.0  # Significant boost for major AI companies
        
        # Add bonuses
        score += self._get_recency_bonus(item)
        
        if item.get('source') == 'GitHub':
            score += self._get_github_engagement_bonus(item)
        
        # Research paper bonus
        tags = item.get('tags', [])
        if any(tag in ['research', 'paper'] for tag in tags):
            score += 1.0
        
        # Boost for general AI/ML terms to catch more content
        general_ai_terms = ['artificial intelligence', 'machine learning', 'deep learning', 
                           'neural network', 'ai', 'ml', 'llm', 'gpt', 'claude', 'gemini']
        for term in general_ai_terms:
            if term in text_content:
                score += 0.5
                break  # Only count once per item
        
        return score
    
    def _count_all_keyword_matches(self, text: str) -> Dict[str, int]:
        """Count all keyword matches in a single pass - optimized"""
        matches = {
            'multimodal': 0,
            'ai_agent': 0,
            'energy_ai': 0,
            'high_value': 0,
            'company': 0
        }
        
        # Single pass through text for all keyword sets
        for keyword in self.multimodal_keywords:
            if keyword in text:
                matches['multimodal'] += 1
        
        for keyword in self.ai_agent_keywords:
            if keyword in text:
                matches['ai_agent'] += 1
        
        for keyword in self.energy_ai_keywords:
            if keyword in text:
                matches['energy_ai'] += 1
        
        for keyword in self.high_value_keywords:
            if keyword in text:
                matches['high_value'] += 1
        
        for keyword in self.company_keywords:
            if keyword in text:
                matches['company'] += 1
        
        return matches
    
    def _count_keyword_matches(self, text: str, keywords: Set[str]) -> int:
        """Count how many keywords appear in the text"""
        return sum(1 for keyword in keywords if keyword in text)
    
    def _get_recency_bonus(self, item: Dict[str, Any]) -> float:
        """Calculate bonus points for recent content"""
        try:
            date_str = item.get('date', '')
            if not date_str:
                return 0.0
            
            # Try to parse the date
            if isinstance(date_str, str):
                # Handle various date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                    try:
                        post_date = datetime.strptime(date_str[:len(fmt)], fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return 0.0
            else:
                post_date = date_str
            
            days_ago = (datetime.now() - post_date).days
            
            # More recent content gets higher bonus (extended for 6 months)
            if days_ago <= 7:
                return 2.0
            elif days_ago <= 30:
                return 1.8
            elif days_ago <= 90:
                return 1.5
            elif days_ago <= 180:
                return 1.0
            else:
                return 0.5
                
        except Exception:
            return 0.0
    
    def _get_github_engagement_bonus(self, item: Dict[str, Any]) -> float:
        """Calculate bonus for GitHub repository engagement"""
        try:
            stars = item.get('stars', 0)
            forks = item.get('forks', 0)
            
            # Logarithmic scaling for stars and forks
            star_bonus = min(2.0, stars / 1000.0)
            fork_bonus = min(1.0, forks / 100.0)
            
            return star_bonus + fork_bonus
            
        except Exception:
            return 0.0
    
    def _get_relevance_reasons(self, item: Dict[str, Any]) -> List[str]:
        """Get human-readable reasons for why content is relevant - optimized"""
        reasons = []
        
        # Efficiently combine text content (reuse from scoring)
        text_parts = []
        if item.get('title'):
            text_parts.append(item['title'])
        if item.get('summary'):
            text_parts.append(item['summary'])
        if item.get('content'):
            text_parts.append(item['content'])
        if item.get('tags'):
            text_parts.extend(item['tags'])
        
        text_content = ' '.join(text_parts).lower()
        
        # Find matching keywords efficiently
        keyword_findings = self._find_matching_keywords(text_content)
        
        # Build reasons from findings
        if keyword_findings['multimodal']:
            reasons.append(f"Multimodal AI: {', '.join(keyword_findings['multimodal'][:3])}")
        
        if keyword_findings['ai_agent']:
            reasons.append(f"AI Agents: {', '.join(keyword_findings['ai_agent'][:3])}")
        
        if keyword_findings['energy_ai']:
            reasons.append(f"Energy AI: {', '.join(keyword_findings['energy_ai'][:3])}")
        
        if keyword_findings['high_value']:
            reasons.append(f"Key Tech: {', '.join(keyword_findings['high_value'][:3])}")
        
        # Check for recent content (reuse score calculation)
        if self._get_recency_bonus(item) >= 1.5:
            reasons.append("Recent content")
        
        # Check for GitHub engagement
        if item.get('source') == 'GitHub' and item.get('stars', 0) > 500:
            reasons.append(f"High engagement ({item.get('stars')} stars)")
        
        return reasons[:4]  # Limit to top 4 reasons
    
    def _find_matching_keywords(self, text: str) -> Dict[str, List[str]]:
        """Find matching keywords in text for relevance reasons"""
        findings = {
            'multimodal': [],
            'ai_agent': [],
            'energy_ai': [],
            'high_value': []
        }
        
        # Find matches for each category
        for keyword in self.multimodal_keywords:
            if keyword in text:
                findings['multimodal'].append(keyword)
        
        for keyword in self.ai_agent_keywords:
            if keyword in text:
                findings['ai_agent'].append(keyword)
        
        for keyword in self.energy_ai_keywords:
            if keyword in text:
                findings['energy_ai'].append(keyword)
        
        for keyword in self.high_value_keywords:
            if keyword in text:
                findings['high_value'].append(keyword)
        
        return findings
