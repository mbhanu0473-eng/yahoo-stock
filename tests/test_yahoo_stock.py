"""Tests for yahoo_stock module - rate-limit handling and retry logic."""

import time
import threading
import unittest
from unittest.mock import MagicMock, patch, call

import yahoo_stock as ys


class TestIsRateLimitError(unittest.TestCase):
    """Unit tests for _is_rate_limit_error helper."""

    def test_http_429_string(self):
        self.assertTrue(ys._is_rate_limit_error(Exception("HTTP 429 error")))

    def test_too_many_requests(self):
        self.assertTrue(ys._is_rate_limit_error(Exception("Too Many Requests")))

    def test_rate_keyword(self):
        self.assertTrue(ys._is_rate_limit_error(Exception("rate limit reached")))

    def test_rate_limited_code(self):
        self.assertTrue(ys._is_rate_limit_error(Exception("Error Code: rate_limited")))

    def test_exceeded_keyword(self):
        self.assertTrue(
            ys._is_rate_limit_error(
                Exception("Sorry, you have exceeded your quota exceeded limit.")
            )
        )

    def test_token_usage_keyword(self):
        self.assertTrue(
            ys._is_rate_limit_error(
                Exception("Sorry, you have exceeded your Copilot token usage.")
            )
        )

    def test_non_rate_limit_error(self):
        self.assertFalse(ys._is_rate_limit_error(Exception("Connection refused")))

    def test_value_error(self):
        self.assertFalse(ys._is_rate_limit_error(ValueError("invalid ticker")))


class TestThrottle(unittest.TestCase):
    """Tests for _throttle to ensure minimum interval enforcement."""

    def test_throttle_sleeps_when_called_too_quickly(self):
        ys._last_request_time = time.time()  # simulate a very recent request
        with patch("yahoo_stock.time") as mock_time:
            mock_time.time.return_value = ys._last_request_time + 0.3
            mock_time.sleep = MagicMock()
            # Use a real lock so the with-statement in _throttle works
            with patch("yahoo_stock._throttle_lock", threading.Lock()):
                ys._throttle(1.0)
            mock_time.sleep.assert_called_once()
            sleep_arg = mock_time.sleep.call_args[0][0]
            self.assertAlmostEqual(sleep_arg, 0.7, delta=0.05)

    def test_throttle_does_not_sleep_after_long_gap(self):
        ys._last_request_time = 0.0  # far in the past
        with patch("yahoo_stock.time") as mock_time:
            mock_time.time.return_value = 9999.0
            mock_time.sleep = MagicMock()
            with patch("yahoo_stock._throttle_lock", threading.Lock()):
                ys._throttle(1.0)
            mock_time.sleep.assert_not_called()


class TestFetchWithRetry(unittest.TestCase):
    """Tests for _fetch_with_retry retry / back-off behaviour."""

    def setUp(self):
        # Reset the module-level throttle timestamp so earlier tests don't
        # leave a "future" value that causes an unexpected sleep call.
        ys._last_request_time = 0.0

    def _run_fetch(self, fetch_fn, max_retries=3, backoff_base=0.01):
        return ys._fetch_with_retry(
            fetch_fn,
            ticker="TEST",
            max_retries=max_retries,
            backoff_base=backoff_base,
            min_request_interval=0.0,
        )

    def test_success_on_first_attempt(self):
        fetch_fn = MagicMock(return_value={"price": 100})
        result = self._run_fetch(fetch_fn)
        self.assertEqual(result, {"price": 100})
        fetch_fn.assert_called_once()

    def test_retries_on_rate_limit_then_succeeds(self):
        fetch_fn = MagicMock(
            side_effect=[
                Exception("HTTP 429 Too Many Requests"),
                Exception("HTTP 429 Too Many Requests"),
                {"price": 42},
            ]
        )
        with patch("yahoo_stock.time.sleep"):
            result = self._run_fetch(fetch_fn, max_retries=3)
        self.assertEqual(result, {"price": 42})
        self.assertEqual(fetch_fn.call_count, 3)

    def test_raises_runtime_error_after_max_retries(self):
        fetch_fn = MagicMock(
            side_effect=Exception("HTTP 429 Too Many Requests")
        )
        with patch("yahoo_stock.time.sleep"):
            with self.assertRaises(RuntimeError) as ctx:
                self._run_fetch(fetch_fn, max_retries=2)
        self.assertIn("Rate limit persists", str(ctx.exception))
        self.assertEqual(fetch_fn.call_count, 3)  # 1 initial + 2 retries

    def test_non_rate_limit_error_not_retried(self):
        fetch_fn = MagicMock(side_effect=ValueError("bad ticker"))
        with self.assertRaises(ValueError):
            self._run_fetch(fetch_fn, max_retries=5)
        fetch_fn.assert_called_once()

    def test_backoff_delays_increase_exponentially(self):
        fetch_fn = MagicMock(
            side_effect=Exception("rate limit")
        )
        sleep_calls = []
        with patch("yahoo_stock.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
            with self.assertRaises(RuntimeError):
                self._run_fetch(fetch_fn, max_retries=3, backoff_base=1.0)

        # delays should be 1, 2, 4 (base * 2^0, 2^1, 2^2)
        self.assertEqual(len(sleep_calls), 3)
        self.assertAlmostEqual(sleep_calls[0], 1.0)
        self.assertAlmostEqual(sleep_calls[1], 2.0)
        self.assertAlmostEqual(sleep_calls[2], 4.0)


class TestGetStockInfo(unittest.TestCase):
    """Integration-style tests for get_stock_info (yfinance mocked)."""

    @patch("yahoo_stock.yf.Ticker")
    def test_returns_info_dict(self, mock_ticker_cls):
        mock_ticker_cls.return_value.info = {"shortName": "Apple Inc.", "price": 150}
        result = ys.get_stock_info("AAPL", min_request_interval=0.0)
        self.assertEqual(result["shortName"], "Apple Inc.")

    @patch("yahoo_stock.yf.Ticker")
    def test_retries_on_rate_limit(self, mock_ticker_cls):
        mock_instance = MagicMock()
        # First access raises, second returns data
        type(mock_instance).info = property(
            MagicMock(
                side_effect=[
                    Exception("429 Too Many Requests"),
                    {"shortName": "Apple Inc."},
                ]
            )
        )
        mock_ticker_cls.return_value = mock_instance

        with patch("yahoo_stock.time.sleep"):
            result = ys.get_stock_info(
                "AAPL", max_retries=3, min_request_interval=0.0
            )
        self.assertEqual(result["shortName"], "Apple Inc.")


class TestGetStockHistory(unittest.TestCase):
    """Integration-style tests for get_stock_history (yfinance mocked)."""

    @patch("yahoo_stock.yf.Ticker")
    def test_returns_dataframe(self, mock_ticker_cls):
        import pandas as pd

        mock_df = pd.DataFrame({"Close": [100, 101, 102]})
        mock_ticker_cls.return_value.history.return_value = mock_df

        result = ys.get_stock_history("AAPL", period="5d", min_request_interval=0.0)
        self.assertEqual(list(result["Close"]), [100, 101, 102])
        mock_ticker_cls.return_value.history.assert_called_once_with(
            period="5d", interval="1d"
        )


if __name__ == "__main__":
    unittest.main()
