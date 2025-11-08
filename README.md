# Reddit Scraper and AI Analysis

Scrapes Reddit posts and uses Google Gemini AI to classify and summarize each post. Designed for analyzing personal finance and FIRE (Financial Independence Retire Early) subreddits.

## What It Does

- Scrapes Reddit posts from any subreddit (up to 5000 posts)
- Classifies posts into finance domains (spending, saving, investment, etc.)
- Identifies question nature (definition, advice, calculation, etc.)
- Generates concise summaries for each post
- Exports results to CSV with metadata

Controls:
- Enter subreddit name when prompted
- Enter Gemini API key in the script before running

## How It Works

1. **Reddit Scraping**: Uses HTTP requests to fetch posts from Reddit JSON API
2. **Rate Limiting**: Implements random delays (1.5-3.5s) between requests
3. **AI Classification**: Sends post content to Gemini API for two-layer classification
4. **Data Extraction**: Collects post metadata (title, author, score, comments, etc.)
5. **Export**: Saves classified data to CSV file

## Dependencies

- `httpx` - HTTP client for API requests
- `pandas` - Data manipulation and CSV export
- `Google Gemini 2.5 Flash API` - AI classification and summarization

## Technical Details

- Max Posts: 5000 per run
- Retry Logic: 100 attempts with exponential backoff
- Output Format: CSV with columns for classification, summary, and metadata
- API: Reddit JSON API, Google Gemini API
