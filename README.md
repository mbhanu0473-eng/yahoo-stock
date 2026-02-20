# yahoo-stock

A Python utility for fetching stock data from Yahoo Finance that gracefully
handles rate-limiting errors with automatic exponential back-off retry logic.

## The problem

Yahoo Finance (and the unofficial `yfinance` wrapper) can return HTTP 429
"Too Many Requests" errors when you make too many consecutive requests.  The
error typically looks like:

```
Sorry, you have been rate-limited. Please wait a moment before trying again.
Error Code: rate_limited
```

## Solution

`yahoo_stock.py` solves this in two ways:

1. **Client-side throttling** – enforces a configurable minimum delay between
   requests so you are less likely to trigger the rate limit at all.
2. **Automatic retry with exponential back-off** – if a rate-limit error is
   still returned, the library retries the request up to `max_retries` times,
   doubling the wait time between each attempt.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from yahoo_stock import get_stock_info, get_stock_history

# Fetch general info (retries automatically on rate-limit errors)
info = get_stock_info("AAPL")
print(info.get("shortName"), info.get("currentPrice"))

# Fetch 1-month price history
history = get_stock_history("AAPL", period="1mo", interval="1d")
print(history.tail())
```

### Configuration

Both functions accept optional keyword arguments to tune the retry behaviour:

| Parameter              | Default | Description                                      |
|------------------------|---------|--------------------------------------------------|
| `max_retries`          | `5`     | Maximum retry attempts on rate-limit errors      |
| `backoff_base`         | `2.0`   | Base delay (s); doubles after each failed retry  |
| `min_request_interval` | `1.0`   | Minimum seconds between consecutive requests     |

```python
info = get_stock_info(
    "TSLA",
    max_retries=3,
    backoff_base=1.5,
    min_request_interval=0.5,
)
```

## Running tests

```bash
python -m pytest tests/ -v
```
