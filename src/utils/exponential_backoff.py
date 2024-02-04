import time
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

    def sleep(self) -> None:
        """Wait and increase the wait time to the next bucket."""

        self.logger.info(
            f"waiting for {self.buckets[self.bucket_index]/60} minute(s)"
        )
        time.sleep(self.buckets[self.bucket_index])
        self.bucket_index = min(self.bucket_index + 1, len(self.buckets) - 1)

    def reset(self) -> None:
        """Reset the waiting period to the first bucket"""
        self.bucket_index = 0
