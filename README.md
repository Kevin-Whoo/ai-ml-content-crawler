# 🤖 AI/ML Content Crawler

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Async](https://img.shields.io/badge/async-asyncio-green.svg)](https://docs.python.org/3/library/asyncio.html)

An intelligent web crawler that gathers the latest AI/ML research papers, blog posts, and repository updates from major sources.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-ml-content-crawler.git
cd ai-ml-content-crawler

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

### Running the Crawler

```bash
# Option 1: Run as a module
python -m src

# Option 2: Use the CLI (if installed)
ai-ml-crawler
```
# Option 3: Run this complicated one
PYTHONPATH=/home/kevin/ai-ml-content-crawler/src python -m ai_ml_crawler

## 📚 Documentation

Detailed guides are available in the [docs](docs/README.md) directory:

- **[Usage Guide](docs/USAGE_GUIDE.md)**: Step-by-step instructions
- **[Security Guidelines](docs/SECURITY.md)**: Security features and practices
- **[Architecture Overview](docs/ARCHITECTURE.md)**: System design and components
- **[Analysis Reports](docs/analysis)**: Code quality and performance reports

## 🚀 Key Features

- **8 Active Crawlers**: OpenAI, Meta, Anthropic, GitHub, ArXiv, Google Scholar, Medium, HuggingFace
- **Smart Caching**: 15-day TTL for efficient performance
- **Content Filtering**: AI/ML relevance scoring with keyword matching
- **Markdown Reports**: Comprehensive output with metadata and scoring
- **Anti-Detection**: Browser profiles, rate limiting, and request randomization
- **Async Processing**: Concurrent crawler execution for speed

## 📑 Output

The crawler generates comprehensive markdown reports in the `output/` directory with:
- Executive summary and statistics
- Categorized content by source
- Relevance scores and metadata
- Publication dates and tags

## 📊 Project Structure

```
ai-ml-content-crawler/
├── src/                  # Source code
│   ├── crawlers/        # Individual crawler implementations
│   ├── utils/           # Utility modules
│   └── config.py        # Configuration
├── docs/                 # Documentation
├── output/               # Generated reports
├── cache/                # Request cache
└── requirements.txt      # Dependencies
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Full Documentation](docs/README.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Security Guidelines](docs/SECURITY.md)
