__title__ = "icloud-contacts-organizer"
__version__ = "0.0.0"
__author__ = "Joel McCune (https://github.com/knu2xs)"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2026 by Joel McCune (https://github.com/knu2xs)"

# add specific imports below if you want to organize your code into modules, which is mostly what I do
from . import utils
from ._main import example_function, ExampleObject

__all__ = ["example_function", "ExampleObject", "utils"]

# configure package-level logging
logger = utils.get_logger("icloud_contacts_organizer", level="DEBUG", add_stream_handler=False)
