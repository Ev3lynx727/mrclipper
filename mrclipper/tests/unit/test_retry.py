"""Tests for the retry decorator."""

import subprocess
from unittest.mock import Mock

import pytest

from mrclipper.utils import retry


def test_retry_success_after_failures(mocker):
    """Function that fails twice then succeeds should retry correctly."""
    mock_func = Mock(
        side_effect=[ConnectionError("Network error"), ConnectionError("Timeout"), "success"]
    )
    decorated = retry(tries=3, delay=0.01, backoff=2.0)(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_exhausts_tries_and_raises(mocker):
    """Function that always fails should raise exception after exhausting retries."""
    mock_func = Mock(side_effect=ConnectionError("Network error"))
    decorated = retry(tries=2, delay=0.01, backoff=2.0)(mock_func)

    with pytest.raises(ConnectionError, match="Network error"):
        decorated()

    assert mock_func.call_count == 2  # Called exactly `tries` times


def test_retry_non_retryable_exception_not_retried(mocker):
    """Non-retryable exceptions should be raised immediately without retry."""
    mock_func = Mock(side_effect=ValueError("Invalid input"))
    decorated = retry(tries=3, delay=0.01, backoff=2.0)(mock_func)

    with pytest.raises(ValueError, match="Invalid input"):
        decorated()

    assert mock_func.call_count == 1  # Only called once


def test_retry_with_multiple_exception_types(mocker):
    """Should retry on any configured exception type."""
    mock_func = Mock(
        side_effect=[
            subprocess.CalledProcessError(1, "cmd", stderr="error"),  # CalledProcessError
            TimeoutError("timeout"),  # TimeoutError
            "success",  # Success
        ]
    )
    decorated = retry(tries=3, delay=0.01, backoff=2.0)(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_backoff_timing(mocker, caplog):
    """Verify that backoff increases delay between retries."""
    # Mock time.sleep to track delays without actually waiting
    mock_sleep = mocker.patch("mrclipper.utils.time.sleep")
    mock_func = Mock(side_effect=[ConnectionError, ConnectionError, "success"])
    decorated = retry(tries=3, delay=1.0, backoff=2.0)(mock_func)

    decorated()

    assert mock_sleep.call_count == 2  # Sleep between retries (2 failures)
    # First retry: delay=1.0, second retry: delay=2.0 (1.0 * 2.0)
    expected_delays = [1.0, 2.0]
    actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays


def test_retry_logs_warnings(mocker, caplog):
    """Verify that retry attempts are logged as warnings."""
    mock_func = Mock(side_effect=[ConnectionError("fail"), "success"])
    decorated = retry(tries=2, delay=0.01, backoff=2.0)(mock_func)

    decorated()

    # Check that a warning was logged about retry
    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) >= 1
    assert "Retry" in warnings[0].message
    assert "1/2" in warnings[0].message  # First retry attempt number


def test_retry_with_zero_delay(mocker):
    """Retry with delay=0 should not sleep."""
    mock_sleep = mocker.patch("mrclipper.utils.time.sleep")
    mock_func = Mock(side_effect=[ConnectionError, "success"])
    decorated = retry(tries=2, delay=0.0, backoff=2.0)(mock_func)

    decorated()

    assert mock_sleep.call_count == 1
    assert mock_sleep.call_args[0][0] == 0.0


def test_retry_decorator_preserves_function_metadata(mocker):
    """Retry decorator should preserve original function name and docstring."""

    def sample_func(x, y):
        """Sample function docstring."""
        return x + y

    decorated = retry()(sample_func)

    assert decorated.__name__ == "sample_func"
    assert decorated.__doc__ == "Sample function docstring."


def test_retry_with_args_and_kwargs(mocker):
    """Retry should correctly pass args and kwargs to wrapped function."""
    mock_func = Mock(side_effect=[ConnectionError, "success"])
    decorated = retry(tries=2, delay=0.01)(mock_func)

    result = decorated(1, 2, key="value")

    assert result == "success"
    mock_func.assert_called_with(1, 2, key="value")


def test_retry_default_parameters(mocker):
    """Test retry with default parameters (tries=3, delay=1.0, backoff=2.0)."""
    mock_sleep = mocker.patch("mrclipper.utils.time.sleep")
    mock_func = Mock(side_effect=[ConnectionError, ConnectionError, "success"])
    decorated = retry()(mock_func)

    decorated()

    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2
    # Default delay=1.0, backoff=2.0 → delays: 1.0, 2.0
    actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
    assert actual_delays == [1.0, 2.0]
