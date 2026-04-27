import logging
from pathlib import Path


class AppLogger:
    """Centralized logging for the NomNom app."""

    def __init__(self, log_file: str = ".nomnom_data/app.log"):
        """Initialize logger."""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)

        self.logger = logging.getLogger("nomnom")
        self.logger.setLevel(logging.DEBUG)

        # File handler (logs to file)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        if kwargs:
            self.logger.debug(f"{message} | {kwargs}")
        else:
            self.logger.debug(message)

    def info(self, message: str, **kwargs):
        """Log info message."""
        if kwargs:
            self.logger.info(f"{message} | {kwargs}")
        else:
            self.logger.info(message)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        if kwargs:
            self.logger.warning(f"{message} | {kwargs}")
        else:
            self.logger.warning(message)

    def error(self, message: str, **kwargs):
        """Log error message."""
        if kwargs:
            self.logger.error(f"{message} | {kwargs}")
        else:
            self.logger.error(message)


# Global logger instance
logger = AppLogger()
