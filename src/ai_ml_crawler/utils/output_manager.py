"""
Output formatting and storage management
"""

import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

from ai_ml_crawler.config import CrawlerConfig


class OutputManager:
    """Manage output formatting and storage of crawled content"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    def now_utc(self) -> datetime:
        """Helper method to get current UTC datetime"""
        return datetime.utcnow()
    
    def save_results(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save results as optimized markdown report"""
        print(f"💾 Saving results to {self.config.output_dir}/")
        
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Save optimized markdown report
        self._save_optimized_markdown(results)
        
        print(f"✅ Results saved as optimized markdown report with timestamp {self.timestamp}")
    
    def _save_optimized_markdown(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save results in an optimized, well-structured markdown report"""
        filename = f"{self.config.output_dir}/AI_ML_Resources_{self.timestamp}.md"
        
        # Pre-calculate statistics for efficiency
        total_items = sum(len(items) for items in results.values())
        source_stats = {source: len(items) for source, items in results.items() if items}
        
        # Build content efficiently using list comprehension and join
        content_parts = []
        
        # Header section
        content_parts.extend([
            "# 🤖 Latest AI/ML Resources Report\n",
            f"**Generated:** {self.now_utc().strftime('%B %d, %Y at %H:%M UTC')}\n",
            f"**Total Resources:** {total_items}\n\n",
            "---\n\n"
        ])
        
        # Quick stats table
        content_parts.append("## 📊 Summary\n\n")
        content_parts.append("| Source | Count | Top Score |\n")
        content_parts.append("|--------|-------|-----------|\n")
        
        for source, items in results.items():
            if items:
                top_score = max(item.get('relevance_score', 0) for item in items)
                content_parts.append(f"| {self._format_source_name(source)} | {len(items)} | {top_score:.1f} |\n")
        
        content_parts.append("\n---\n\n")
        
        # Content sections - optimized loop
        for source, items in results.items():
            if not items:
                continue
                
            # Sort once, outside the loop
            items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            content_parts.append(f"## {self._get_source_emoji(source)} {self._format_source_name(source)}\n\n")
            
            # Process items efficiently
            for i, item in enumerate(items, 1):
                title = item.get('title', 'Untitled').strip()
                url = item.get('url', '')
                
                # Build item content efficiently
                item_parts = [f"### {i}. [{title}]({url})\n"]
                
                # Metadata line - build once
                metadata_parts = [f"**📅 Date:** {self._format_date(item.get('date', ''))}"]
                
                # Add GitHub-specific metadata
                if source == 'github':
                    stars = item.get('stars', 0)
                    language = item.get('language', '')
                    if stars:
                        metadata_parts.append(f"**⭐ Stars:** {stars:,}")
                    if language:
                        metadata_parts.append(f"**💻 Language:** {language}")
                
                # Add relevance score
                score = item.get('relevance_score', 0)
                if score > 0:
                    metadata_parts.append(f"**🎯 Score:** {score:.1f}")
                
                item_parts.append(" | ".join(metadata_parts) + "\n\n")
                
                # Summary (optimized)
                summary = item.get('summary', '').strip()
                if summary:
                    clean_summary = self._clean_summary(summary)
                    item_parts.append(f"**📝 Summary:** {clean_summary}\n\n")
                
                # Relevance reasons (optimized)
                reasons = item.get('relevance_reasons', [])
                if reasons:
                    item_parts.append(f"**🏷️ Tags:** {', '.join(reasons[:3])}\n\n")
                
                item_parts.append("---\n\n")
                
                content_parts.extend(item_parts)
        
        # Footer
        content_parts.extend([
            "## 🔗 Quick Links\n\n",
            "- [Papers With Code](https://paperswithcode.com/)\n",
            "- [arXiv AI Papers](https://arxiv.org/list/cs.AI/recent)\n",
            "- [Hugging Face Papers](https://huggingface.co/papers)\n\n",
            "*Generated by AI/ML Content Crawler*\n"
        ])
        
        # Write all content at once (more efficient)
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(content_parts)
    
    def _format_source_name(self, source: str) -> str:
        """Format source name for display"""
        source_names = {
            'anthropic': 'Anthropic Research & Blog',
            'openai': 'OpenAI Research & Blog', 
            'meta': 'Meta AI Research & Blog',
            'github': 'GitHub Repositories',
            'huggingface': 'Hugging Face Models & Papers',
            'medium': 'Medium Articles',
            'google_scholar': 'Google Scholar Papers'
        }
        return source_names.get(source, source.title())
    
    def _get_source_emoji(self, source: str) -> str:
        """Get emoji for source"""
        emojis = {
            'anthropic': '🏛️',
            'openai': '🤖', 
            'meta': '🔷',
            'github': '💻',
            'huggingface': '🤗',
            'medium': '📰',
            'google_scholar': '🎓'
        }
        return emojis.get(source, '📄')
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str:
            return "Unknown"
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    dt = datetime.strptime(date_str[:len(fmt)], fmt)
                    return dt.strftime('%B %d, %Y')
                except ValueError:
                    continue
            return date_str
        except (ValueError, TypeError, AttributeError):
            # Handle various date parsing errors
            return date_str
    
    def _clean_summary(self, summary: str) -> str:
        """Clean and format summary text"""
        if not summary:
            return "No description available."
        
        # Remove extra whitespace
        summary = ' '.join(summary.split())
        
        # Limit length
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        # Ensure it ends with proper punctuation
        if summary and summary[-1] not in '.!?':
            summary += "."
        
        return summary
    
    def _save_summary(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save a concise summary report"""
        filename = f"{self.config.output_dir}/crawl_summary_{self.timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("AI/ML Content Crawl Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Crawl completed: {self.now_utc().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            
            # Overall stats
            total_items = sum(len(items) for items in results.values())
            f.write(f"Total items found: {total_items}\n")
            f.write(f"Sources crawled: {len(results)}\n\n")
            
            # Source-specific stats
            f.write("Results by source:\n")
            for source, items in results.items():
                f.write(f"- {source.title()}: {len(items)} items\n")
            f.write("\n")
            
            # Top 5 items
            all_items = []
            for source, items in results.items():
                for item in items:
                    item['source_name'] = source
                    all_items.append(item)
            
            all_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            if all_items:
                f.write("Top 5 most relevant items:\n")
                for i, item in enumerate(all_items[:5], 1):
                    f.write(f"{i}. {item.get('title', 'Untitled')} "
                           f"(Score: {item.get('relevance_score', 0):.1f}, "
                           f"Source: {item.get('source_name', '').title()})\n")
            
            f.write(f"\nDetailed results saved to:\n")
            f.write(f"- JSON: ai_ml_content_{self.timestamp}.json\n")
            f.write(f"- CSV: ai_ml_content_{self.timestamp}.csv\n")
            f.write(f"- Markdown: ai_ml_content_{self.timestamp}.md\n")