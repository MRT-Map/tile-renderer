import logging
import os

from rich.logging import RichHandler

logging.basicConfig(
    level=os.environ.get("LOG", "INFO").upper(),
    format="%(message)s",
    # datefmt=" ",
    handlers=[RichHandler(markup=True, show_path=False)],
)

log = logging.getLogger("rich")
