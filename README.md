# Sales Intelligence Platform

AI-powered B2B sales intelligence for roofing distributors.

## Quick Start

### 1. Install Python & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```

### 2. OpenAI API Key
Edit .env file and add your API key from https://platform.openai.com/api-keys

### 3. Run the Pipeline
```bash
python3 scraper.py          # Step 1: Scrape data
python3 database.py         # Step 2: Load to database
python3 ai_insights.py      # Step 3: Generate insights
python3 evaluate_insights.py # Step 4: Evaluate quality
```

## Files
- **scraper.py** - Web scraping
- **database.py** - Data storage
- **ai_insights.py** - AI insight generation
- **evaluate_insights.py** - Quality evaluation

## Tech Stack
Python, Selenium, BeautifulSoup, SQLite, OpenAI API
