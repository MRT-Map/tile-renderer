from _typeshed import Incomplete
from dill import detect as detect
from dill.logger import stderr_handler as stderr_handler

test_obj: Incomplete

def test_logging(should_trace): ...
def test_trace_to_file(stream_trace) -> None: ...
