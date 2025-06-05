import asyncio
import csv
import json
import os
from datetime import datetime, timedelta, timezone
import ssl

import aiohttp

from environ.constants import DATA_PATH

# API Key provided by the user
GRAPH_API_KEY = os.getenv("GRAPH_API_KEY")

UNISWAP_V3_SUBGRAPH_URL = f"https://gateway.thegraph.com/api/{GRAPH_API_KEY}/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"


async def query_swaps_batch_async(
    session: aiohttp.ClientSession,
    start_timestamp: int,
    end_timestamp: int,
    limit: int = 1000,
    last_id: str | None = None,
) -> list[dict] | None:
    """
    Queries a batch of Uniswap V3 swaps asynchronously using attribute-based pagination (id_gt).
    API key is part of UNISWAP_V3_SUBGRAPH_URL.
    """
    where_clauses = [
        f"timestamp_gte: {start_timestamp}",
        f"timestamp_lte: {end_timestamp}",
    ]
    if last_id:
        where_clauses.append(f'id_gt: "{last_id}"')

    where_string = ", ".join(where_clauses)

    query = f"""
    {{
      swaps(
        first: {limit},
        orderBy: id,  # Order by ID for consistent pagination
        orderDirection: asc,
        where: {{ {where_string} }}
      ) {{
        id
        transaction {{ id blockNumber timestamp }}
        pool {{ id token0 {{ id symbol name decimals }} token1 {{ id symbol name decimals }} }}
        token0 {{ id symbol }} # Corresponds to amount0
        token1 {{ id symbol }} # Corresponds to amount1
        sender
        recipient
        origin
        amount0
        amount1
        amountUSD
        sqrtPriceX96
        tick
        logIndex
      }}
    }}
    """
    payload = {"query": query}

    try:
        async with session.post(UNISWAP_V3_SUBGRAPH_URL, json=payload) as response:
            response.raise_for_status()  # Raises an exception for HTTP errors
            data = await response.json()

            if "errors" in data:
                # Simplified error logging for async context
                error_message = data["errors"][0].get(
                    "message", "Unknown GraphQL error"
                )
                print(
                    f"  GraphQL Error (period: {start_timestamp}-{end_timestamp}, last_id: {last_id}): {error_message}"
                )
                return None

            return data.get("data", {}).get("swaps", [])

    except aiohttp.ClientResponseError as http_err:
        print(
            f"  HTTP error (last_id: {last_id}, status: {http_err.status}): {http_err.message}"
        )
        return None
    except (
        aiohttp.ClientError
    ) as e:  # Catches other aiohttp client errors (e.g., connection issues)
        print(f"  AIOHTTP client error (last_id: {last_id}): {e}")
        return None
    except json.JSONDecodeError:
        print(f"  JSON decode error (last_id: {last_id}).")
        return None
    except Exception as e:  # Catch-all for unexpected errors
        print(
            f"  Unexpected error in query_swaps_batch_async (last_id: {last_id}): {e}"
        )
        return None


async def fetch_all_swaps_for_period_async(
    session: aiohttp.ClientSession, start_ts: int, end_ts: int, limit: int = 1000
) -> list[dict]:
    """
    Fetches all swaps for a given period asynchronously, handling attribute-based pagination.
    """
    all_swaps_for_period = []
    last_fetched_id = None
    retries = 3
    retry_delay = 5

    while True:
        batch = None
        for attempt in range(retries):
            batch = await query_swaps_batch_async(
                session, start_ts, end_ts, limit=limit, last_id=last_fetched_id
            )
            if batch is not None:
                break
            print(
                f"  Batch fetch failed (last_id: {last_fetched_id}), attempt {attempt + 1}/{retries}. Retrying in {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)  # Use asyncio.sleep

        if batch is None:
            print(
                f"  Error fetching batch (last_id: {last_fetched_id}) after {retries} attempts. Returning collected data for this period."
            )
            return all_swaps_for_period  # Return whatever was collected so far

        if not batch:  # Empty list indicates no more data
            break

        all_swaps_for_period.extend(batch)
        last_fetched_id = batch[-1]["id"]

        if len(batch) < limit:
            break

    return all_swaps_for_period


# --- CSV Export Logic (Synchronous, called from async context) ---


def save_swaps_to_file(swaps_data: list[dict], filename: str) -> None:
    """
    Saves a list of swap data to a CSV file. This function remains synchronous.
    Uses user-preferred simplified column names.
    """
    if not swaps_data:
        return

    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print(f"  Saving {len(swaps_data)} swaps to {os.path.basename(filename)}.")
    try:
        # save as json
        with open(filename.with_suffix(".json"), "w", encoding="utf-8") as jsonfile:
            json.dump(swaps_data, jsonfile, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"  I/O error writing to {os.path.basename(filename)}: {e}")
    except Exception as e:
        print(f"  Unexpected error writing to {os.path.basename(filename)}: {e}")


# --- Main Asynchronous Orchestration ---


async def process_day_async(
    session: aiohttp.ClientSession, current_dt: datetime, semaphore: asyncio.Semaphore
) -> None:
    """
    Asynchronously fetches and saves swap data for a single day,
    respecting the semaphore to limit concurrency.
    """
    async with semaphore:  # Acquire semaphore
        day_str = current_dt.strftime("%Y-%m-%d")
        print(f"Processing day: {day_str}")

        day_start_dt = current_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_dt = current_dt.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        day_start_timestamp = int(day_start_dt.timestamp())
        day_end_timestamp = int(day_end_dt.timestamp())

        try:
            daily_swaps = await fetch_all_swaps_for_period_async(
                session, day_start_timestamp, day_end_timestamp
            )

            print(f"  Fetched {len(daily_swaps)} swaps for {day_str}.")
            if daily_swaps:
                file_name = DATA_PATH / "uniswap" / f"uniswap_v3_swaps_{day_str}.json"

                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, save_swaps_to_file, daily_swaps, file_name
                )
        except Exception as e:
            print(f"Error processing day {day_str}: {e}")
        finally:
            # Semaphore is released automatically when exiting 'async with semaphore' block
            print(f"Finished processing day: {day_str}")


async def fetch_uniswap_v3(
    overall_start_date_str: str = "2021-05-04",
    overall_end_date_str: str = "2023-01-31",  # Inclusive
    max_concurrent_days: int = 8,  # User-defined limit
) -> None:
    """
    Main asynchronous function to coordinate fetching data for all days.
    """
    if (
        not GRAPH_API_KEY
        or GRAPH_API_KEY == "YOUR_API_KEY"
        or "[api-key]" in UNISWAP_V3_SUBGRAPH_URL
        or "YOUR_PLACEHOLDER_API_KEY" in UNISWAP_V3_SUBGRAPH_URL
    ):
        print(
            "Error: GRAPH_API_KEY is not properly set or UNISWAP_V3_SUBGRAPH_URL is incorrect."
        )
        print(
            "Please ensure GRAPH_API_KEY is valid and UNISWAP_V3_SUBGRAPH_URL is correctly formatted with your API key."
        )
        return

    try:
        overall_start_dt = datetime.strptime(
            overall_start_date_str, "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)
        overall_end_dt = datetime.strptime(overall_end_date_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
    except ValueError as ve:
        print(
            f"Date parsing error: {ve}. Please ensure dates are in 'YYYY-MM-DD' format."
        )
        return

    tasks = []
    semaphore = asyncio.Semaphore(max_concurrent_days)

    ssl_context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_CLIENT
    )  # or ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        current_dt = overall_start_dt
        while current_dt <= overall_end_dt:
            # Pass the semaphore to each task
            tasks.append(process_day_async(session, current_dt, semaphore))
            current_dt += timedelta(days=1)

        await asyncio.gather(*tasks)

    print("\nDaily swap export process complete.")


if __name__ == "__main__":
    try:
        # Standard way to run asyncio program
        asyncio.run(
            fetch_uniswap_v3(
                overall_start_date_str="2024-05-04",
                overall_end_date_str="2024-05-04",  # Inclusive
                max_concurrent_days=8,
            )
        )
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
