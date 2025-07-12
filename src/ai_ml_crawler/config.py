"""
Configuration settings for the AI/ML content crawler
"""

import os
from dataclasses import dataclass
from typing import List, Dict


class Keywords:
    """Centralized keyword definitions for efficiency - expanded for better matching"""
    
    MULTIMODAL = [
        "multimodal", "vision language model", "vlm", "clip", "dall-e", 
        "gpt-4v", "gpt-4o", "gpt-4", "claude-3", "claude 3", "gemini pro vision", "llava",
        "visual question answering", "image captioning", "vision transformer",
        "text-to-image", "image-to-text", "visual reasoning", "multimodal ai",
        "vision-language", "visual language", "image understanding", "computer vision",
        "stable diffusion", "midjourney", "imagen", "blip", "flamingo", "kosmos",
        "visual ai", "image generation", "video understanding", "cross-modal"
    ]
    
    AI_AGENT = [
        "ai agent", "autonomous agent", "intelligent agent", "agentic ai",
        "agent framework", "multi-agent", "agent planning", "tool use",
        "function calling", "reasoning agent", "agent orchestration",
        "langchain", "autogen", "crewai", "agent workflow", "agentic system",
        "agent collaboration", "agent architecture", "agent reasoning",
        "autonomous system", "ai assistant", "chatbot", "conversational ai",
        "task automation", "workflow automation", "decision making", "planning"
    ]
    
    ENERGY_AI = [
        "energy ai", "smart grid", "energy management", "power systems ai",
        "renewable energy optimization", "energy forecasting", "demand response",
        "energy trading", "grid optimization", "energy efficiency ai",
        "power grid automation", "energy storage optimization", "microgrid",
        "energy analytics", "predictive maintenance energy", "carbon optimization",
        "energy digital twin", "smart meter", "energy iot", "energy blockchain",
        "energy market", "power system automation", "energy data analytics",
        "sustainability ai", "climate ai", "renewable energy", "carbon footprint"
    ]


@dataclass
class CrawlerConfig:
    """Configuration class for crawler settings - optimized"""
    
    # Output settings
    output_dir: str = "output"
    max_results_per_source: int = 25
    
    # Request settings - optimized for speed
    request_delay: float = 0.1  # minimal delay between requests
    timeout: int = 10
    user_agent: str = "AI-Research-Crawler/1.0"
    
    # Caching settings
    enable_caching: bool = True
    cache_ttl: int = 1296000  # 15 days for better hit rates
    max_cache_size_mb: int = 100
    enable_rate_limiting: bool = True
    
    # Anti-detection settings - optimized for speed
    rotate_user_agents: bool = False  # Disable rotation for speed
    enable_proxy_rotation: bool = False
    request_jitter: float = 0.0  # No random delay
    session_rotation_interval: int = 3600  # 1 hour
    
    # Content filtering keywords - use class constants
    multimodal_keywords: List[str] = None
    ai_agent_keywords: List[str] = None
    energy_ai_keywords: List[str] = None
    
    # Date filtering (days back from today) - extended to get more content
    max_days_back: int = 365  # Extended to 1 year for comprehensive content coverage
    
    # GitHub settings
    github_token: str = None  # Set via environment variable
    
    def __post_init__(self):
        # Use class constants for efficiency
        if self.multimodal_keywords is None:
            self.multimodal_keywords = Keywords.MULTIMODAL
        
        if self.ai_agent_keywords is None:
            self.ai_agent_keywords = Keywords.AI_AGENT
        
        if self.energy_ai_keywords is None:
            self.energy_ai_keywords = Keywords.ENERGY_AI
        
        # Get GitHub token from environment
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Load proxy settings from environment
        if os.getenv('CRAWLER_ENABLE_PROXIES', 'false').lower() == 'true':
            self.enable_proxy_rotation = True

# Target sources configuration
SOURCES_CONFIG = {
    "anthropic": {
        "blog_url": "https://www.anthropic.com/news",
        "research_url": "https://www.anthropic.com/research",
        "rss_feeds": []
    },
    "openai": {
        "blog_url": "https://openai.com/blog/",
        "research_url": "https://openai.com/research/",
        "api_url": "https://openai.com/api/research/",
        "rss_feeds": [],
        "additional_sources": [
            "https://openai.com/news/",
            "https://openai.com/index/",
            "https://help.openai.com/en/collections/3742473-chatgpt"
        ]
    },
    "meta": {
        "blog_url": "https://ai.meta.com/blog/",
        "research_url": "https://ai.meta.com/research/",
        "rss_feeds": []
    },
    "github": {
        "search_queries": [
            "multimodal LLM",
            "vision language model", 
            "AI agent framework",
            "autonomous agent",
            "energy AI agents",
            "smart grid AI",
            "energy management system",
            "power systems optimization"
        ],
        "sort_by": "updated",
        "min_stars": 10
    },
    # IEEE removed per user request
    "arxiv": {
        "base_url": "https://arxiv.org/search/",
        "categories": ["cs.AI", "eess.SY"],
        "search_topics": ["energy AI agents", "smart grid optimization"]
    },
    "energy_gov": {
        "blog_url": "https://www.energy.gov/articles",
        "search_topics": ["artificial intelligence", "machine learning"]
    },
    "iea": {
        "blog_url": "https://www.iea.org/topics/digitalization-and-energy",
        "search_topics": ["AI", "digitalization"]
    }
}