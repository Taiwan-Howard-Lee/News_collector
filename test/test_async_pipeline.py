import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.scrapers.async_pipeline import run_async_pipeline

if __name__ == '__main__':
    # Set the number of workers for parallel processing
    NUM_WORKERS = 25
    
    # Run the asynchronous pipeline
    asyncio.run(run_async_pipeline(max_workers=NUM_WORKERS))
