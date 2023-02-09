from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Union,
)

class ConfigError(Exception): ...

class ConfigAlreadyRegisteredError(ConfigError):
    def __init__(self, name) -> None: ...

class ConfigValueParsingError(ConfigError):
    def __init__(self, name, value) -> None: ...

class ConfigValueValidationError(ConfigError):
    def __init__(self, name, value) -> None: ...

class ConfigUnknownOptionError(ConfigError):
    def __init__(self, option_or_name) -> None: ...

class Option:
    name: str
    help: str
    default: Any
    parse: Callable[[str], Any]
    validate: Optional[Callable[[Any], bool]]
    @staticmethod
    def parse_optional_bool(v: str) -> Optional[bool]: ...
    @staticmethod
    def validate_optional_bool(v: Any) -> bool: ...
    def __init__(self, name, help, default, parse, validate) -> None: ...

class Options(Mapping):
    def __init__(self, other: Options = ...) -> None: ...
    def register(
        self,
        name: str,
        help: str,
        default: Any,
        parse: Callable[[str], Any],
        validate: Optional[Callable[[Any], bool]] = ...,
    ) -> Option: ...
    def register_option(self, option: Option) -> Option: ...
    def is_registered(self, option: Option) -> bool: ...
    def __getitem__(self, key: str) -> Option: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...

class AbstractConfig(MutableMapping):
    options: ClassVar[Options]
    @classmethod
    def register_option(
        cls,
        name: str,
        help: str,
        default: Any,
        parse: Callable[[str], Any],
        validate: Optional[Callable[[Any], bool]] = ...,
    ) -> Option: ...
    def __init__(
        self,
        values: Union[AbstractConfig, Dict[Union[Option, str], Any]] = ...,
        parse_values: bool = ...,
        skip_unknown: bool = ...,
    ) -> None: ...
    def set(
        self,
        option_or_name: Union[Option, str],
        value: Any,
        parse_values: bool = ...,
        skip_unknown: bool = ...,
    ): ...
    def get(self, option_or_name: Union[Option, str], default: Any = ...) -> Any: ...
    def copy(self): ...
    def __getitem__(self, option_or_name: Union[Option, str]) -> Any: ...
    def __setitem__(self, option_or_name: Union[Option, str], value: Any) -> None: ...
    def __delitem__(self, option_or_name: Union[Option, str]) -> None: ...
    def __iter__(self) -> Iterable[str]: ...  # type: ignore
    def __len__(self) -> int: ...
