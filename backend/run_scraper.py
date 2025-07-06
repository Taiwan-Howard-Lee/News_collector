import asyncio
import argparse
import sys
import os

# Add the project root to the Python path to resolve import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.scrapers.async_pipeline import run_async_pipeline

def main():
    """
    Main function to run the asynchronous scraping pipeline.
    Accepts a command-line argument for the number of workers.
    """
    parser = argparse.ArgumentParser(description="Run the asynchronous news scraping pipeline.")
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='The maximum number of concurrent workers for scraping.'
    )
    args = parser.parse_args()

    asyncio.run(run_async_pipeline(max_workers=args.workers))

if __name__ == "__main__":
    main()
