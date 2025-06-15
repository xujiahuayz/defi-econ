import asyncio
import argparse
from environ.fetch.fetch_subgraph_swaps_v3 import fetch_uniswap_v3

if __name__ == "__main__":
    # --- Argument Parsing Setup ---
    parser = argparse.ArgumentParser(
        description="Fetch Uniswap V3 swap data for a given date range."
    )
    parser.add_argument(
        "--start_date",
        required=True,
        help="The start date for fetching data (format: YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end_date",
        required=True,
        help="The end date for fetching data (format: YYYY-MM-DD, inclusive).",
    )
    parser.add_argument(
        "--max_concurrent",
        type=int,
        default=8,
        help="Maximum number of concurrent days to process.",
    )
    args = parser.parse_args()

    # --- Main Execution ---
    try:
        # Run the main async function with arguments from the command line
        asyncio.run(
            fetch_uniswap_v3(
                overall_start_date_str=args.start_date,
                overall_end_date_str=args.end_date,
                max_concurrent_days=args.max_concurrent,
            )
        )
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            print("Detected a running event loop. Attempting to use it.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                fetch_uniswap_v3(
                    overall_start_date_str=args.start_date,
                    overall_end_date_str=args.end_date,
                    max_concurrent_days=args.max_concurrent,
                )
            )
        else:
            raise