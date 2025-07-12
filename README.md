# 🤖 AI/ML Content Crawler

An intelligent web crawler that gathers the latest AI/ML research papers, blog posts, and repository updates from major sources.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the crawler (choose one):
# Option 1: As a module
python -m src

# Option 2: After installing with pip
pip install -e .
ai-ml-crawler
```

## 📁 Project Structure

```
ai-ml-content-crawler/
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
├── src/                   # Source code (ai_ml_crawler package)
│   ├── __main__.py       # Module entry point
│   ├── cli.py            # CLI entry point
│   ├── main.py           # Main crawler logic
│   ├── config.py         # Configuration settings
│   ├── crawlers/         # Individual crawler modules
│   └── utils/            # Utility modules
├── docs/                 # Documentation
│   ├── README.md         # Detailed documentation
│   ├── USAGE_GUIDE.md    # Usage instructions
│   ├── SECURITY.md       # Security guidelines
│   └── analysis/         # Analysis reports
├── output/               # Generated reports
├── cache/                # Cached web content
└── .env.example          # Environment variables template
```

## 📊 Features

- **8 Active Crawlers**: OpenAI, Meta, Anthropic, GitHub, ArXiv, Google Scholar, Medium, HuggingFace
- **Smart Caching**: 15-day TTL for efficient performance
- **Content Filtering**: AI/ML relevance scoring
- **Multiple Output Formats**: Markdown reports with metadata
- **Anti-Detection**: Browser profiles and rate limiting
- **Async Processing**: Concurrent crawler execution

## 📄 Latest Output

Check the `output/` directory for the most recent AI/ML resources report.

For detailed documentation, see `docs/README.md`.
