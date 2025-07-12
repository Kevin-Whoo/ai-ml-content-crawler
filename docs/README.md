# 🤖 Enhanced AI/ML Content Crawler

A secure, undetectable web crawler for gathering the latest AI/ML research content with advanced anti-detection capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Crawler
```bash
python main.py
```

That's it! The crawler will automatically gather content from all AI/ML sources.

## 📊 What It Does

- **🔍 Crawls 9 major AI/ML sources**: Anthropic, OpenAI, Meta AI, GitHub, Hugging Face, Medium, Google Scholar, ArXiv, IEEE
- **🎯 Finds relevant content** about Multimodal LLMs, AI Agents, and Energy AI
- **📝 Generates a comprehensive report** in markdown format
- **🛡️ Uses advanced security** and anti-detection features

## 🛡️ Enhanced Security Features

✅ **Input validation & SSRF protection**  
✅ **Anti-detection browser profiles**  
✅ **Smart caching system**  
✅ **Rate limiting awareness**  
✅ **Centralized error handling**  
✅ **Content validation**  

## ⚙️ Configuration (Optional)

### Basic Settings
```bash
# Slower but more stealthy
export CRAWLER_DELAY="4.0"

# GitHub token for higher API limits (recommended)
export GITHUB_TOKEN="your_github_token"

# Enable proxy rotation (optional)
export CRAWLER_ENABLE_PROXIES="true"
export CRAWLER_PROXIES="http://proxy1:8080,http://proxy2:8080"
```

### Custom Keywords
Edit `config.py` to modify:
- `multimodal_keywords` - Keywords for multimodal AI content
- `ai_agent_keywords` - Keywords for AI agent content  
- `energy_ai_keywords` - Keywords for energy AI content
- `max_days_back` - How far back to search (default: 90 days)
- `max_results_per_source` - Results per source (default: 25)

## 📁 Output

The crawler creates:
- `output/AI_ML_Resources_YYYYMMDD_HHMMSS.md` - Main comprehensive report
- `cache/` directory - Cached requests for better performance

## 🔧 Advanced Usage

### Proxy Setup (Optional)
Create `proxies.txt` with one proxy per line:
```
http://proxy1.example.com:8080
socks5://proxy2.example.com:1080
```

### Custom Configuration
Edit `config.py` directly for fine-tuning:
```python
# In config.py
request_delay: float = 2.0  # Seconds between requests
cache_ttl: int = 3600      # Cache time in seconds
max_results_per_source: int = 25
```

## 📊 Real-time Monitoring

The crawler shows live statistics:
```
🚀 Starting comprehensive AI/ML content crawl...
📡 Initiating github crawler...
✅ github: Found 25 relevant items
✅ anthropic: Found 12 relevant items
💾 Cache stats: 78.4% hit rate, 156 entries
🎉 Crawling complete! Found 67 relevant items
```

## 🚨 Troubleshooting

**Getting rate limited?**
```bash
export CRAWLER_DELAY="5.0"  # Increase delay
```

**Want to clear cache?**
```bash
rm -rf cache/
```

**Proxy not working?**
```bash
# Test your proxy first
curl --proxy http://your-proxy:8080 https://httpbin.org/ip
```

## 🔒 Security & Ethics

- **Respects rate limits** and server resources
- **Only accesses public research content**
- **Follows robots.txt** and terms of service
- **Validates all inputs** to prevent security issues
- **Uses domain allowlist** to prevent SSRF attacks

## 📄 File Structure

```
Web_Crawling/
├── main.py              # 🎯 Main runner (use this!)
├── config.py            # ⚙️ Configuration settings
├── requirements.txt     # 📦 Dependencies
├── crawlers/           # 🕷️ Crawler implementations
├── utils/              # 🛠️ Security & utility modules
├── output/             # 📊 Generated reports
└── cache/              # 💾 Request cache
```

## 🎯 Just Remember

**To run the crawler:** `python main.py`

Everything else is automatic! 🎉