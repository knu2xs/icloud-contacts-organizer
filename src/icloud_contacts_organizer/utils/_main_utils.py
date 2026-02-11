"""Useful utility functions for icloud_contacts_organizer."""

from ._logging import get_logger

# set up module-level logger
logger = get_logger("icloud_contacts_organizer.utils", level="DEBUG", add_stream_handler=False)
