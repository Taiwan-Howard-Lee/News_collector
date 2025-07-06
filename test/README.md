# Test Suite for Trafilatura Scraper

This folder contains tests for the trafilatura-based news content extractor.

## Test Files

### `test_trafilatura_scraper.py`
Basic functionality test that verifies the scraper works with two specific URLs:
- CapitaLand news article
- Business Times homepage

**Features tested:**
- URL scraping with Playwright
- Multiple extraction methods (full, bare, metadata, baseline)
- Content extraction success/failure detection
- Performance timing

### `detailed_test_results.py`
Detailed extraction test that shows complete results and saves them to JSON files for inspection.

**Features tested:**
- Full content extraction details
- Metadata extraction (title, date, tags, etc.)
- Text content extraction
- JSON output generation

### `run_tests.py`
Test runner script that executes all tests and provides a summary.

## Test URLs

The tests use these URLs to verify scraper functionality:

1. **CapitaLand News Article**: 
   - URL: `https://www.capitaland.com/en/about-capitaland/newsroom/news-releases/international/2025/june/ESG-CLI-launch-retail-maverick-challenge.html`
   - Type: Structured news article
   - Expected: Title, date, content extraction

2. **Business Times Homepage**:
   - URL: `https://www.businesstimes.com.sg/`
   - Type: News homepage with multiple articles
   - Expected: Site title, multiple content links

## Running Tests

### Run all tests:
```bash
cd test
python3 run_tests.py
```

### Run individual tests:
```bash
cd test
python3 test_trafilatura_scraper.py
python3 detailed_test_results.py
```

## Expected Results

All tests should pass with the following outcomes:
- ✅ Successful HTML fetching with Playwright
- ✅ Multiple extraction methods working
- ✅ Content extraction with metadata
- ✅ Text content extraction
- ✅ JSON output generation

## Output Files

The detailed test generates JSON files with complete extraction results:
- `extraction_result_1.json` - CapitaLand article results
- `extraction_result_2.json` - Business Times homepage results

## Dependencies

Tests require the same dependencies as the main scraper:
- trafilatura
- playwright
- playwright-stealth

Make sure to install dependencies before running tests:
```bash
pip install trafilatura playwright playwright-stealth
playwright install chromium
```
