import time
from typing import Optional
from .logger import Logger


class ExponentialBackoff:
    """Exponential backoff e.g. when errors occur. First try again in 1 minute,
    then 4 minutes, then 15 minutes, etc.. Usage:
    
    ```python
    import src
    exponential_backoff = src.utils.ExponentialBackoff(logger)
    while True:
        try:
            # do something
            exponential_backoff.reset()
        except Exception as e:
            logger.exception(e)
            exponential_backoff.sleep()
    ```"""
    def __init__(
        self,
        logger: Logger,
        buckets: list[int] = [60, 240, 900, 3600, 14400],
    ) -> None:
        """Create a new exponential backoff object.

        Args:
            logger: The logger to use for logging when waiting certain amount of time.
            buckets: The buckets to use for the exponential backoff."""

        self.buckets = buckets
        self.bucket_index = 0  # index of the next wait time bucket
        self.logger = logger

    def sleep(self, max_sleep_time: Optional[float]) -> int:
        """Wait and increase the wait time to the next bucket.
        
        Args:
            max_sleep_time: The maximum time to sleep. If None, no maximum is set.
        
        Returns:
            The amount of seconds waited."""

        sleep_seconds = self.buckets[self.bucket_index]
        if max_sleep_time is not None:
            sleep_seconds = min(sleep_seconds, max_sleep_time)

        self.logger.info(f"waiting for {sleep_seconds/60} minute(s)")
        time.sleep(sleep_seconds)
        # TODO: log progress steps
        self.bucket_index = min(self.bucket_index + 1, len(self.buckets) - 1)
        return sleep_seconds

    def reset(self) -> None:
        """Reset the waiting period to the first bucket"""
        self.bucket_index = 0
