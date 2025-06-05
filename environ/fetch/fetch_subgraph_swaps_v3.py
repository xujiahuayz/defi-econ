import requests  # Keep for potential fallback or type hinting, though aiohttp is primary
import json
from datetime import datetime, timezone, timedelta
import csv
import os
import time
import asyncio
import aiohttp
from gas.environ.constants import DATA_PATH

# API Key provided by the user
GRAPH_API_KEY = "YOUR_API_KEY"

# Updated The Graph API endpoint for Uniswap V3, with API key embedded
if GRAPH_API_KEY and GRAPH_API_KEY != "YOUR_API_KEY":  # YOUR_API_KEY is a placeholder
    UNISWAP_V3_SUBGRAPH_URL = f"https://gateway.thegraph.com/api/{GRAPH_API_KEY}/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
else:
    # This case should ideally not be hit if GRAPH_API_KEY is correctly set.
    UNISWAP_V3_SUBGRAPH_URL = f"https://gateway.thegraph.com/api/YOUR_PLACEHOLDER_API_KEY/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
    print(
        "Warning: GRAPH_API_KEY is not the expected one or is a placeholder. The URL might not be correct."
    )


# --- GraphQL Query and Fetching Logic (Asynchronous) ---


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
    session: aiohttp.ClientSession, start_ts: int, end_ts: int
) -> list[dict]:
    """
    Fetches all swaps for a given period asynchronously, handling attribute-based pagination.
    """
    all_swaps_for_period = []
    last_fetched_id = None
    page_size = 1000
    retries = 3
    retry_delay = 5

    while True:
        batch = None
        for attempt in range(retries):
            batch = await query_swaps_batch_async(
                session, start_ts, end_ts, limit=page_size, last_id=last_fetched_id
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

        if len(batch) < page_size:
            break

    return all_swaps_for_period


# --- CSV Export Logic (Synchronous, called from async context) ---


def save_swaps_to_csv(swaps_data: list[dict], filename: str = "swaps.csv") -> None:
    """
    Saves a list of swap data to a CSV file. This function remains synchronous.
    Uses user-preferred simplified column names.
    """
    if not swaps_data:
        return

    # User-preferred simplified headers
    headers = [
        "swap_id",
        "transaction",
        "block_number",
        "timestamp",
        "datetime_utc",
        "pool",
        "token0_id",
        "token0_symbol",
        "token0_name",
        "token0_decimals",  # For pool's token0
        "token1_id",
        "token1_symbol",
        "token1_name",
        "token1_decimals",  # For pool's token1
        "sender",
        "recipient",
        "origin",
        "amount0",
        "amount1",
        "amountUSD",
        "sqrtPriceX96",
        "tick",
        "logIndex",
    ]

    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print(f"  Saving {len(swaps_data)} swaps to {os.path.basename(filename)}.")
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for swap in swaps_data:
                transaction_timestamp_str = swap.get("transaction", {}).get("timestamp")
                transaction_timestamp = (
                    int(transaction_timestamp_str) if transaction_timestamp_str else 0
                )

                row = {
                    "swap_id": swap.get("id"),
                    "transaction": swap.get("transaction", {}).get("id"),
                    "block_number": swap.get("transaction", {}).get("blockNumber"),
                    "timestamp": transaction_timestamp,
                    "datetime_utc": (
                        datetime.fromtimestamp(
                            transaction_timestamp, timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S %Z")
                        if transaction_timestamp
                        else ""
                    ),
                    "pool": swap.get("pool", {}).get("id"),  # Pool ID
                    # Pool's token0 details
                    "token0_id": swap.get("pool", {}).get("token0", {}).get("id"),
                    "token0_symbol": swap.get("pool", {})
                    .get("token0", {})
                    .get("symbol"),
                    "token0_name": swap.get("pool", {}).get("token0", {}).get("name"),
                    "token0_decimals": swap.get("pool", {})
                    .get("token0", {})
                    .get("decimals"),
                    # Pool's token1 details
                    "token1_id": swap.get("pool", {}).get("token1", {}).get("id"),
                    "token1_symbol": swap.get("pool", {})
                    .get("token1", {})
                    .get("symbol"),
                    "token1_name": swap.get("pool", {}).get("token1", {}).get("name"),
                    "token1_decimals": swap.get("pool", {})
                    .get("token1", {})
                    .get("decimals"),
                    "sender": swap.get("sender"),
                    "recipient": swap.get("recipient"),
                    "origin": swap.get("origin"),
                    "amount0": swap.get("amount0"),
                    "amount1": swap.get("amount1"),
                    "amountUSD": swap.get("amountUSD", ""),
                    "sqrtPriceX96": swap.get("sqrtPriceX96"),
                    "tick": swap.get("tick"),
                    "logIndex": swap.get("logIndex"),
                }
                writer.writerow(row)
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
                csv_filename = DATA_PATH / "uniswap_v3_swaps_{day_str}.csv"

                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, save_swaps_to_csv, daily_swaps, csv_filename
                )
        except Exception as e:
            print(f"Error processing day {day_str}: {e}")
        finally:
            # Semaphore is released automatically when exiting 'async with semaphore' block
            print(f"Finished processing day: {day_str}")


async def fetch_uniswap_v3() -> None:
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

    overall_start_date_str = "2021-05-04"
    overall_end_date_str = "2023-01-31"  # Inclusive
    max_concurrent_days = 8  # User-defined limit

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

    async with aiohttp.ClientSession() as session:
        current_dt = overall_start_dt
        while current_dt <= overall_end_dt:
            # Pass the semaphore to each task
            tasks.append(process_day_async(session, current_dt, semaphore))
            current_dt += timedelta(days=1)

        await asyncio.gather(*tasks)

    print("\nDaily swap export process complete.")


if __name__ == "__main__":
    pass
