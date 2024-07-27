import logging
import os
import sys

from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level=os.environ.get("LOG", "INFO").upper(),
    format="%(message)s",
    # datefmt=" ",
    handlers=[RichHandler(markup=True, show_path=False, console=Console(file=sys.stderr))],
)

log = logging.getLogger("rich")
