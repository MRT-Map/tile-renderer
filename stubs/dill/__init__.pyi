from _typeshed import Incomplete

from . import detect as detect
from . import session as session
from . import source as source
from . import temp as temp
from ._dill import CONTENTS_FMODE as CONTENTS_FMODE
from ._dill import DEFAULT_PROTOCOL as DEFAULT_PROTOCOL
from ._dill import FILE_FMODE as FILE_FMODE
from ._dill import HANDLE_FMODE as HANDLE_FMODE
from ._dill import HIGHEST_PROTOCOL as HIGHEST_PROTOCOL
from ._dill import PickleError as PickleError
from ._dill import Pickler as Pickler
from ._dill import PickleWarning as PickleWarning
from ._dill import PicklingError as PicklingError
from ._dill import PicklingWarning as PicklingWarning
from ._dill import Unpickler as Unpickler
from ._dill import UnpicklingError as UnpicklingError
from ._dill import UnpicklingWarning as UnpicklingWarning
from ._dill import check as check
from ._dill import copy as copy
from ._dill import dump as dump
from ._dill import dumps as dumps
from ._dill import load as load
from ._dill import loads as loads
from ._dill import pickle as pickle
from ._dill import pickles as pickles
from ._dill import register as register
from .session import dump_module as dump_module
from .session import dump_session as dump_session
from .session import load_module as load_module
from .session import load_module_asdict as load_module_asdict
from .session import load_session as load_session
from .settings import settings as settings

parent: Incomplete
objects: Incomplete

def load_types(pickleable: bool = ..., unpickleable: bool = ...) -> None: ...
def extend(use_dill: bool = ...) -> None: ...
def license() -> None: ...
def citation() -> None: ...
