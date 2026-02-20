"""
yahoo_stock.py - Fetch stock data from Yahoo Finance with rate-limit handling.

Automatically retries requests on HTTP 429 (Too Many Requests) responses using
exponential back-off, and enforces a configurable minimum delay between requests
to reduce the likelihood of being rate-limited in the first place.
"""

import time
import logging
import threading
from typing import Optional

import yfinance as yf

logger = logging.getLogger(__name__)

# Default retry / back-off settings
DEFAULT_MAX_RETRIES: int = 5
DEFAULT_BACKOFF_BASE: float = 2.0   # seconds; doubled on each retry
DEFAULT_MIN_REQUEST_INTERVAL: float = 1.0  # minimum seconds between requests

_last_request_time: float = 0.0
_throttle_lock = threading.Lock()


def _throttle(min_interval: float) -> None:
    """Sleep if necessary to enforce *min_interval* seconds between requests.

    Thread-safe: a lock ensures only one thread updates ``_last_request_time``
    at a time so concurrent callers do not bypass the minimum interval.
    """
    global _last_request_time
    with _throttle_lock:
        elapsed = time.time() - _last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _last_request_time = time.time()


def get_stock_info(
    ticker: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
) -> dict:
    """Return general information for *ticker* with automatic retry on rate limits.

    Parameters
    ----------
    ticker:
        Stock ticker symbol, e.g. ``"AAPL"``.
    max_retries:
        Maximum number of retry attempts when a rate-limit error is received.
    backoff_base:
        Base delay (seconds) for exponential back-off.  The delay after attempt
        *n* is ``backoff_base * 2 ** n``.
    min_request_interval:
        Minimum time (seconds) to wait between consecutive requests.

    Returns
    -------
    dict
        The ``yfinance`` ``.info`` dictionary for the ticker.

    Raises
    ------
    RuntimeError
        If the request continues to fail after *max_retries* attempts.
    """
    return _fetch_with_retry(
        lambda: yf.Ticker(ticker).info,
        ticker=ticker,
        max_retries=max_retries,
        backoff_base=backoff_base,
        min_request_interval=min_request_interval,
    )


def get_stock_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
):
    """Return price history for *ticker* with automatic retry on rate limits.

    Parameters
    ----------
    ticker:
        Stock ticker symbol, e.g. ``"AAPL"``.
    period:
        Data period to download.  Valid values: ``1d``, ``5d``, ``1mo``,
        ``3mo``, ``6mo``, ``1y``, ``2y``, ``5y``, ``10y``, ``ytd``, ``max``.
    interval:
        Data interval.  Valid values: ``1m``, ``2m``, ``5m``, ``15m``,
        ``30m``, ``60m``, ``90m``, ``1h``, ``1d``, ``5d``, ``1wk``, ``1mo``,
        ``3mo``.
    max_retries:
        Maximum number of retry attempts when a rate-limit error is received.
    backoff_base:
        Base delay (seconds) for exponential back-off.
    min_request_interval:
        Minimum time (seconds) to wait between consecutive requests.

    Returns
    -------
    pandas.DataFrame
        Historical OHLCV data.

    Raises
    ------
    RuntimeError
        If the request continues to fail after *max_retries* attempts.
    """
    return _fetch_with_retry(
        lambda: yf.Ticker(ticker).history(period=period, interval=interval),
        ticker=ticker,
        max_retries=max_retries,
        backoff_base=backoff_base,
        min_request_interval=min_request_interval,
    )


def _is_rate_limit_error(exc: Exception) -> bool:
    """Return *True* if *exc* looks like a Yahoo Finance rate-limit error."""
    msg = str(exc).lower()
    rate_limit_phrases = (
        "rate",
        "429",
        "too many requests",
        "rate_limited",
        "quota exceeded",
        "requests exceeded",
        "token usage",
    )
    return any(phrase in msg for phrase in rate_limit_phrases)


def _fetch_with_retry(
    fetch_fn,
    *,
    ticker: str,
    max_retries: int,
    backoff_base: float,
    min_request_interval: float,
):
    """Execute *fetch_fn* with exponential back-off retries on rate-limit errors.

    Parameters
    ----------
    fetch_fn:
        Zero-argument callable that performs the actual fetch operation.
    ticker:
        Ticker symbol used only for log messages.
    max_retries:
        Maximum number of retry attempts.
    backoff_base:
        Base delay (seconds) for exponential back-off.
    min_request_interval:
        Minimum time (seconds) to enforce between requests.
    """
    last_exc: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        _throttle(min_request_interval)
        try:
            result = fetch_fn()
            return result
        except Exception as exc:
            last_exc = exc
            if _is_rate_limit_error(exc):
                if attempt < max_retries:
                    delay = backoff_base * (2 ** attempt)
                    logger.warning(
                        "Rate limit hit for %s (attempt %d/%d). "
                        "Retrying in %.1f seconds.",
                        ticker,
                        attempt + 1,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    raise RuntimeError(
                        f"Rate limit persists for '{ticker}' after "
                        f"{max_retries} retries. "
                        "Please wait before trying again."
                    ) from exc
            else:
                raise

    raise RuntimeError(
        f"Failed to fetch data for '{ticker}' after {max_retries} retries."
    ) from last_exc
