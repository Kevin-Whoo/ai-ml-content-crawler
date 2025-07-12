# Date Handling Requirements and Regression Checklist

## 📅 Date Handling Issues Analysis

### Current Problems Identified

1. **OpenAI Crawler**: Using `datetime.now().isoformat()` as fallback instead of extracting actual publication dates
2. **Meta Crawler**: Using `datetime.now().isoformat()` as fallback instead of extracting actual publication dates  
3. **GitHub Crawler**: Correctly using `updated_at` from API (✅ WORKING)
4. **ArXiv Crawler**: Correctly using `published_date` from API (✅ WORKING)
5. **Anthropic Crawler**: Shows empty dates (`"date": ""`) instead of actual publication dates

### Root Cause Analysis

The main issue is in the fallback logic in crawlers where:
- When date extraction fails, crawlers use `datetime.now().isoformat()` 
- This creates timestamps like `2025-07-12T21:50:51.968682` instead of actual publication dates
- Blog crawlers (OpenAI, Meta, Anthropic) are not properly extracting dates from HTML

## 🎯 "Actual Publication/Creation Date" Definition by Source

### GitHub Repositories
- **Definition**: `updated_at` field from GitHub API (last commit/push date)
- **Format**: ISO 8601 (e.g., `2025-07-12T13:20:40Z`)
- **Source**: GitHub REST API response
- **Validation**: Should be within configured `max_days_back` period

### ArXiv Papers
- **Definition**: `published` field from ArXiv API (original submission date)
- **Format**: ISO 8601 date (e.g., `2024-12-15`)
- **Source**: ArXiv API XML response
- **Validation**: Should be within configured `max_days_back` period

### OpenAI Blog Posts
- **Definition**: Article publication date from blog post metadata
- **Expected Sources**:
  - `<time datetime="...">` HTML elements
  - `<meta property="article:published_time" content="...">` tags
  - JSON-LD `datePublished` field
  - URL path date patterns (e.g., `/2024/12/15/title`)
- **Format**: ISO 8601 or parsed date strings
- **Fallback**: If no date found, mark as "Unknown" instead of current timestamp

### Meta AI Blog Posts
- **Definition**: Article publication date from blog post metadata
- **Expected Sources**:
  - `<time datetime="...">` HTML elements
  - `<meta property="article:published_time" content="...">` tags
  - JSON-LD `datePublished` field
  - Date patterns in blog post content
- **Format**: ISO 8601 or parsed date strings
- **Fallback**: If no date found, mark as "Unknown" instead of current timestamp

### Anthropic Blog Posts
- **Definition**: Article publication date from blog post metadata
- **Expected Sources**:
  - `<time datetime="...">` HTML elements
  - `<meta property="article:published_time" content="...">` tags
  - JSON-LD `datePublished` field
  - Date patterns in blog post content
- **Format**: ISO 8601 or parsed date strings
- **Fallback**: If no date found, mark as "Unknown" instead of current timestamp

## 🔧 Required Code Changes

### 1. Update Base Crawler `_create_item` method
```python
def _create_item(self, title: str, url: str, date: str, summary: str = "", 
                content: str = "", tags: List[str] = None, source: str = "") -2  Dict[str, Any]:
    # If no date provided or date is current timestamp, mark as Unknown
    if not date or date.startswith(datetime.now().strftime("%Y-%m-%d")):
        date = "Unknown"
    
    return {
        'title': title.strip()[:500],
        'url': url,
        'date': date,  # Keep original date or "Unknown"
        'summary': summary[:1000] if summary else "",
        'content': content[:50000] if content else "",
        'tags': tags or [],
        'source': source,
        'crawled_at': datetime.now().isoformat()
    }
```

### 2. Blog Crawlers Date Extraction
Need to implement proper date extraction in:
- `openai_crawler.py`: Lines 127, 161, 264, 331
- `meta_crawler.py`: Lines 84, 109  
- `anthropic_crawler.py`: Need to add date extraction logic

### 3. Enhanced Date Extraction Methods
Add to each blog crawler:
```python
def _extract_publication_date(self, soup: BeautifulSoup, url: str) -2  str:
    """Extract publication date from various HTML sources"""
    # Try <time> elements with datetime attribute
    # Try meta tags (article:published_time, etc.)
    # Try JSON-LD structured data
    # Try URL path patterns
    # Return "Unknown" if no date found
```

## 📋 Regression Checklist

### ✅ GitHub Repositories
- [ ] Date format: ISO 8601 with timezone (e.g., `2025-07-12T13:20:40Z`)
- [ ] Date represents: Last update/commit time
- [ ] Example: `shibing624/agentica` should show `2025-07-10T16:55:58Z`
- [ ] Verify: No dates showing current crawl timestamp

### ✅ ArXiv Papers  
- [ ] Date format: YYYY-MM-DD (e.g., `2024-12-15`)
- [ ] Date represents: Original paper submission date
- [ ] Example: Recent AI papers should show actual submission dates
- [ ] Verify: No dates showing current crawl timestamp

### ❌ OpenAI Blog Posts
- [ ] Date format: ISO 8601 or "Unknown" (NO current timestamps)
- [ ] Date represents: Blog post publication date
- [ ] Example: GPT-4o announcement should show `2024-05-13` (not `2025-07-12T21:50:51.968682`)
- [ ] Verify: No dates showing current crawl timestamp like `2025-07-12T21:50:51.968682`

### ❌ Meta AI Blog Posts
- [ ] Date format: ISO 8601 or "Unknown" (NO current timestamps)
- [ ] Date represents: Blog post publication date  
- [ ] Example: LLaMA announcements should show actual publication dates
- [ ] Verify: No dates showing current crawl timestamp like `2025-07-12T21:50:53.861632`

### ❌ Anthropic Blog Posts
- [ ] Date format: ISO 8601 or "Unknown" (NO empty strings)
- [ ] Date represents: Blog post publication date
- [ ] Example: Claude announcements should show actual publication dates
- [ ] Verify: No empty dates (`"date": ""`) or current crawl timestamps

## 🧪 Test Cases for QA

### Test Case 1: OpenAI Blog
```json
{
  "title": "GPT-4o: Enhanced multimodal reasoning capabilities",
  "url": "https://openai.com/index/gpt-4o/",
  "date": "2024-05-13",  // NOT "2025-07-12T21:50:51.968682"
  "source": "OpenAI Blog"
}
```

### Test Case 2: Meta AI Blog
```json
{
  "title": "Introducing LLaMA 2",
  "url": "https://ai.meta.com/blog/llama-2/",
  "date": "2023-07-18",  // NOT "2025-07-12T21:50:53.861632"
  "source": "Meta AI Blog"
}
```

### Test Case 3: Anthropic Blog
```json
{
  "title": "Introducing Claude 3 Opus",
  "url": "https://www.anthropic.com/news/claude-3-opus",
  "date": "2024-03-04",  // NOT "" or current timestamp
  "source": "Anthropic Blog"
}
```

### Test Case 4: GitHub Repository
```json
{
  "title": "shibing624/agentica",
  "url": "https://github.com/shibing624/agentica",
  "date": "2025-07-10T16:55:58Z",  // ✅ CORRECT - actual update time
  "source": "GitHub"
}
```

### Test Case 5: ArXiv Paper
```json
{
  "title": "Multimodal Large Language Models: A Survey",
  "url": "http://arxiv.org/abs/2401.13601",
  "date": "2024-01-24",  // ✅ CORRECT - actual publication date
  "source": "ArXiv"
}
```

## 🚨 Critical Issues to Fix

1. **OpenAI Crawler**: Lines 127, 161, 264, 331 - Remove `datetime.now().isoformat()` fallback
2. **Meta Crawler**: Lines 84, 109 - Remove `datetime.now().isoformat()` fallback  
3. **Anthropic Crawler**: Add proper date extraction (currently returns empty strings)
4. **Base Crawler**: Update `_create_item` to handle "Unknown" dates properly

## 📊 Expected Behavior After Fix

### Blog Posts (OpenAI, Meta, Anthropic)
- **Success**: Show actual publication date (e.g., `2024-05-13`)
- **Failure**: Show `"Unknown"` (NOT current timestamp)
- **Never**: Show timestamps like `2025-07-12T21:50:51.968682`

### API Sources (GitHub, ArXiv)
- **Success**: Show actual dates from API responses
- **Failure**: Show `"Unknown"` (NOT current timestamp)
- **Format**: Maintain original API date formats

This regression checklist ensures QA can quickly verify that:
1. No current crawl timestamps appear in date fields
2. Actual publication dates are extracted when available
3. Missing dates are marked as "Unknown" instead of misleading timestamps
4. Each source type maintains its expected date format and meaning
