# 🏗️ AI/ML Content Crawler Architecture

## Overview

The AI/ML Content Crawler is designed as a modular, asynchronous web scraping system that efficiently gathers AI/ML content from multiple sources while maintaining ethical scraping practices.

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Entry Points                      │
│                   (cli.py / __main__.py)                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Main Orchestrator                        │
│                        (main.py)                             │
│  • Manages crawler lifecycle                                 │
│  • Coordinates concurrent execution                          │
│  • Aggregates results                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
     ┌────────────┴────────────┬────────────┬────────────┐
     ▼                         ▼            ▼            ▼
┌──────────┐          ┌──────────────┐ ┌─────────┐ ┌─────────────┐
│ Crawlers │          │Configuration │ │ Utils   │ │   Output    │
│          │          │   (config.py)│ │         │ │  Manager    │
├──────────┤          └──────────────┘ ├─────────┤ └─────────────┘
│• OpenAI  │                           │• Cache  │
│• Meta    │                           │• Filter │
│• GitHub  │                           │• Valid. │
│• ArXiv   │                           │• Error  │
│• Medium  │                           │• Anti-  │
│• HF      │                           │  detect │
│• Scholar │                           │• Date   │
│• Anthrop.│                           │  extract│
└──────────┘                           └─────────┘
```

## 🧩 Core Components

### 1. **Entry Points**
- `cli.py`: Command-line interface entry point
- `__main__.py`: Module execution entry point
- Both initialize the crawler system and handle user input

### 2. **Main Orchestrator** (`main.py`)
Primary controller that:
- Initializes configuration and dependencies
- Creates crawler instances
- Manages concurrent execution using `asyncio.gather()`
- Aggregates and processes results
- Handles error recovery and reporting

### 3. **Base Crawler** (`crawlers/base_crawler.py`)
Abstract base class providing:
- Common HTTP client management
- Anti-detection mechanisms
- Error handling framework
- Content validation
- Date filtering logic
- Session management

### 4. **Specialized Crawlers**
Each crawler inherits from `BaseCrawler` and implements:
- Source-specific URL construction
- Custom parsing logic
- Data extraction methods
- Response handling

Crawlers include:
- `OpenAICrawler`: OpenAI blog and research
- `MetaCrawler`: Meta AI publications
- `AnthropicCrawler`: Anthropic research
- `GitHubCrawler`: GitHub repositories (with API integration)
- `ArxivCrawler`: ArXiv research papers
- `MediumCrawler`: Medium AI/ML articles
- `HuggingFaceCrawler`: Models, datasets, papers
- `GoogleScholarCrawler`: Academic papers

### 5. **Configuration System** (`config.py`)
Centralized configuration using dataclasses:
```python
@dataclass
class CrawlerConfig:
    max_results_per_source: int = 25
    max_days_back: int = 180
    enable_caching: bool = True
    cache_ttl: int = 3600
    # ... more settings
```

### 6. **Utility Modules**

#### **Caching** (`utils/caching.py`)
- In-memory LRU cache with disk persistence
- TTL-based expiration
- Domain-specific cache management
- Hit rate tracking and statistics

#### **Content Filtering** (`utils/content_filter.py`)
- AI/ML relevance scoring
- Keyword matching algorithms
- Multi-category classification
- Score-based ranking

#### **Anti-Detection** (`utils/anti_detection.py`)
- Browser profile rotation
- User-agent management
- Request timing randomization
- Header generation

#### **Error Handling** (`utils/error_handler.py`)
- Centralized error logging
- Error categorization by severity
- Recovery strategies
- Statistics tracking

#### **Validation** (`utils/validation.py`)
- URL validation with allowlist
- SSRF protection
- Content sanitization
- Input validation

#### **Date Extraction** (`utils/date_extractor.py`)
- Multi-format date parsing
- Relative date handling
- Timezone normalization
- Fallback strategies

### 7. **Output Manager** (`output_manager.py`)
- Markdown report generation
- Data aggregation and formatting
- Statistics calculation
- File I/O management

## 🔄 Data Flow

1. **Initialization**
   ```
   User Input → CLI → Config → Main Orchestrator
   ```

2. **Crawling Process**
   ```
   Main → Crawler Instance → HTTP Request → Response
     ↓                           ↓            ↓
   Cache ← Anti-Detection ← Validation ← Parsing
   ```

3. **Result Processing**
   ```
   Raw Data → Content Filter → Relevance Scoring → Aggregation
      ↓            ↓                ↓                 ↓
   Cache ← Date Filter ← Deduplication ← Output Manager
   ```

4. **Output Generation**
   ```
   Aggregated Results → Markdown Formatting → File Output
                     → Statistics Generation ↗
   ```

## 🎯 Design Patterns

### 1. **Abstract Factory Pattern**
- `BaseCrawler` serves as abstract factory
- Concrete crawlers implement specific behaviors
- Promotes code reuse and consistency

### 2. **Strategy Pattern**
- Different parsing strategies per crawler
- Pluggable content filtering algorithms
- Configurable caching strategies

### 3. **Singleton Pattern**
- Configuration object
- Cache manager
- Error handler

### 4. **Observer Pattern**
- Progress tracking
- Error event handling
- Cache statistics monitoring

## 🚀 Async Architecture

The system leverages Python's `asyncio` for concurrent operations:

```python
async def crawl_all_sources(config):
    tasks = []
    for crawler_class in CRAWLER_CLASSES:
        crawler = crawler_class(config)
        tasks.append(crawler.crawl())
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

Benefits:
- Non-blocking I/O operations
- Concurrent HTTP requests
- Efficient resource utilization
- Scalable architecture

## 🔒 Security Considerations

1. **Input Validation**: All user inputs validated
2. **URL Allowlist**: Only approved domains crawled
3. **SSRF Protection**: Private IP ranges blocked
4. **Rate Limiting**: Prevents server overload
5. **Secure Storage**: No sensitive data persisted

## 📊 Performance Optimizations

1. **Caching Layer**: Reduces redundant requests
2. **Connection Pooling**: Reuses HTTP connections
3. **Concurrent Execution**: Parallel crawler operation
4. **Lazy Loading**: On-demand resource loading
5. **Batch Processing**: Efficient data aggregation

## 🔧 Extension Points

The architecture supports easy extension through:

1. **New Crawlers**: Inherit from `BaseCrawler`
2. **Custom Filters**: Implement filter interface
3. **Output Formats**: Extend `OutputManager`
4. **Cache Backends**: Implement cache interface
5. **Anti-Detection**: Add new browser profiles

## 📈 Scalability

The system can scale through:
- Horizontal scaling with multiple instances
- Distributed caching with Redis
- Queue-based job distribution
- Cloud deployment options
- Microservice architecture migration

---

*For implementation details, see the source code and API documentation.*
