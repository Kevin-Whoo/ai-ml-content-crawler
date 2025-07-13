#!/bin/bash
# Simple script to run the AI/ML Content Crawler

# Navigate to the project directory
cd "$(dirname "$0")"

# Run the crawler with the correct Python path
PYTHONPATH=src python -m ai_ml_crawler
