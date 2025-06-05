import asyncio
from environ.fetch.fetch_subgraph_swaps_v3 import fetch_uniswap_v3

if __name__ == "__main__":
    try:
        # Standard way to run asyncio program
        asyncio.run(fetch_uniswap_v3())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # Fallback for environments like Jupyter where a loop is already running
            print(
                "Detected a running event loop. Attempting to use it to run main_async()."
            )
            loop = asyncio.get_event_loop()
            loop.run_until_complete(fetch_uniswap_v3())
        else:
            # Re-raise other RuntimeError exceptions
            raise
