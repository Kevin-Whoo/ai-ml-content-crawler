# 🔒 Security & Anti-Detection Features

This enhanced web crawler implements comprehensive security measures and advanced anti-detection capabilities while maintaining ethical scraping practices.

## 🛡️ Security Features

### Input Validation & SSRF Protection
- **URL Validation**: All URLs are validated against an allowlist of trusted domains
- **Input Sanitization**: Search queries and content are sanitized to prevent injection attacks
- **SSRF Protection**: Blocks access to private IP ranges and internal networks
- **Content Validation**: Scraped content is validated and cleaned of potentially dangerous patterns

### Centralized Error Handling
- **Structured Logging**: All errors are logged with context and severity levels
- **Recovery Strategies**: Automatic error recovery with configurable retry mechanisms
- **Exception Specificity**: Replaced all bare `except:` clauses with specific exception handling
- **Rate Limit Tracking**: Monitors and responds to rate limiting across domains

## 🥷 Anti-Detection Capabilities

### Browser Fingerprinting
- **Realistic Profiles**: Rotates between authentic browser profiles (Chrome, Firefox, Safari)
- **Dynamic Headers**: Generates realistic request headers with proper browser-specific values
- **Viewport Simulation**: Simulates real browser viewport sizes and platform information
- **Version Diversity**: Uses multiple browser versions to avoid fingerprint consistency

### Request Patterns
- **Intelligent Timing**: Human-like request delays with randomized jitter
- **Exponential Backoff**: Smart retry logic with increasing delays
- **Session Persistence**: Maintains cookies and session state like real browsers
- **Request Randomization**: Varies request patterns to avoid detection

### Advanced Evasion
- **Profile Rotation**: Automatically rotates browser profiles every 5 minutes
- **Proxy Support**: Optional proxy rotation for additional anonymity
- **Rate Limit Awareness**: Automatically backs off when rate limits are detected
- **Bot Protection Detection**: Identifies and responds to anti-bot measures

## 📊 Caching System

### Smart Caching
- **Content Caching**: Intelligent caching with domain-specific TTL values
- **Memory + Disk**: Hybrid caching for optimal performance
- **Cache Optimization**: Automatic cache cleanup and size management
- **Hit Rate Tracking**: Monitors cache performance and provides recommendations

### Rate Limit Caching
- **Domain Tracking**: Tracks rate limits per domain
- **Automatic Backoff**: Respects server-specified retry-after headers
- **Pattern Learning**: Learns and adapts to site-specific rate limiting

## 🔧 Configuration

### Environment Variables
```bash
# GitHub API token for higher rate limits
export GITHUB_TOKEN="your_github_token"

# Enable proxy rotation
export CRAWLER_ENABLE_PROXIES="true"

# Proxy list (comma-separated)
export CRAWLER_PROXIES="http://proxy1:8080,http://proxy2:8080"
```

### Proxy Configuration
Create a `proxies.txt` file with one proxy per line:
```
http://proxy1.example.com:8080
http://proxy2.example.com:8080
socks5://proxy3.example.com:1080
```

### Security Settings
```python
config = CrawlerConfig()
config.enable_caching = True
config.cache_ttl = 3600  # 1 hour
config.enable_rate_limiting = True
config.rotate_user_agents = True
config.enable_proxy_rotation = True
config.request_jitter = 0.5
```

## 🎯 Domain Allowlist

The crawler is restricted to these trusted domains:
- **AI Research**: anthropic.com, openai.com, ai.meta.com
- **Code Repositories**: github.com, api.github.com
- **ML Platforms**: huggingface.co
- **Academic**: scholar.google.com, arxiv.org, ieeexplore.ieee.org
- **Publications**: medium.com, towardsdatascience.com

## 📈 Monitoring & Statistics

### Real-time Monitoring
- **Cache Hit Rates**: Track caching effectiveness
- **Error Statistics**: Monitor error patterns and types
- **Anti-detection Status**: Review stealth recommendations
- **Rate Limit Status**: Track rate limiting across domains

### Performance Metrics
```
Cache stats: 85.4% hit rate, 1,234 entries
Anti-detection recommendations:
  • Vary target domains to avoid detection
Cache recommendations:
  • Cache nearly full - consider clearing expired entries
Session error statistics:
  • NetworkError: 3
  • ParseError: 1
```

## ⚡ Performance Optimizations

### Connection Management
- **Connection Pooling**: Reuses connections efficiently
- **Concurrent Limits**: Respects server capacity with connection limits
- **Keep-Alive**: Maintains persistent connections
- **DNS Caching**: Reduces DNS lookup overhead

### Request Optimization
- **Compression**: Supports gzip, deflate, and brotli compression
- **Conditional Requests**: Uses caching headers when appropriate
- **Request Deduplication**: Avoids duplicate requests
- **Priority Queuing**: Prioritizes important requests

## 🔍 Detection Avoidance

### Behavioral Patterns
- **Human-like Timing**: Varies request timing naturally
- **Session Simulation**: Maintains realistic browsing sessions
- **Error Handling**: Responds to errors like a real browser
- **Resource Loading**: Mimics complete page loading patterns

### Technical Evasion
- **TLS Fingerprinting**: Uses realistic TLS configurations
- **HTTP/2 Support**: Leverages modern protocol features
- **Cookie Management**: Properly handles session cookies
- **Redirect Handling**: Follows redirects naturally

## 🚨 Ethical Guidelines

### Responsible Scraping
- **Rate Limiting**: Never overwhelms target servers
- **Robot.txt Respect**: Honors robots.txt directives
- **Server Resources**: Minimizes server load impact
- **Data Usage**: Only collects publicly available research content

### Legal Compliance
- **Terms of Service**: Operates within site terms of service
- **Fair Use**: Limits data collection to research purposes
- **Attribution**: Properly attributes sources
- **Privacy**: Respects user privacy and data protection laws

## 🛠️ Troubleshooting

### Common Issues

**High Rate Limiting**
```bash
# Increase delays between requests
config.request_delay = 3.0
config.request_jitter = 1.0
```

**Cache Issues**
```bash
# Clear cache manually
rm -rf cache/
```

**Proxy Problems**
```bash
# Test proxy connectivity
curl --proxy http://proxy:8080 https://httpbin.org/ip
```

### Debug Mode
Enable detailed logging:
```python
error_handler = ErrorHandler(log_level="DEBUG", log_file="crawler.log")
```

## 📋 Security Checklist

- ✅ Input validation and sanitization
- ✅ SSRF protection with domain allowlist
- ✅ Centralized error handling
- ✅ Specific exception handling (no bare except)
- ✅ Anti-detection browser profiles
- ✅ Request caching and optimization
- ✅ Rate limiting awareness
- ✅ Proxy rotation support
- ✅ Session management
- ✅ Content validation
- ✅ Comprehensive monitoring

This security framework ensures the crawler operates safely, efficiently, and undetectably while maintaining ethical scraping standards.