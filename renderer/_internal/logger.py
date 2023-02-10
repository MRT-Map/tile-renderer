import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt=" ",
    handlers=[RichHandler(markup=True, show_path=False)],
)

log = logging.getLogger("rich")
