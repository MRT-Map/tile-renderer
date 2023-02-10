from typing import NamedTuple

LOOKUP_DEBUG_INFO_KEY: str
LOOKUP_DEBUG_ENV_VAR: str

class LookupDebugInfo(NamedTuple):
    location: str
    name: str
    feature: list
