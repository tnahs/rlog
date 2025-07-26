from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from rich.console import Console as _Console
from rich.pretty import pprint
from rich.text import Text


if TYPE_CHECKING:
    from rich.status import Status


class LogLevel(StrEnum):
    UNSET = "unset"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"
    TRACE = "trace"

    def __gt__(self, other: LogLevel) -> bool:  # pyright: ignore [reportIncompatibleMethodOverride]
        return self.as_int() > other.as_int()

    def __lt__(self, other: LogLevel) -> bool:  # pyright: ignore [reportIncompatibleMethodOverride]
        return self.as_int() < other.as_int()

    @property
    def color(self) -> str:
        match self:
            case LogLevel.TRACE:
                return "white"
            case LogLevel.DEBUG:
                return "blue"
            case LogLevel.INFO:
                return "green"
            case LogLevel.WARN:
                return "red"
            case LogLevel.ERROR:
                return "red"
            case _:  # LogLevel.UNSET
                return "white"

    def as_int(self) -> int:
        match self:
            case LogLevel.TRACE:
                return 5
            case LogLevel.DEBUG:
                return 4
            case LogLevel.INFO:
                return 3
            case LogLevel.WARN:
                return 2
            case LogLevel.ERROR:
                return 1
            case _:  # LogLevel.UNSET:
                return 0


class Console:
    _stdout = _Console()
    _stderr = _Console(stderr=True)
    _log_level = LogLevel.WARN

    @property
    def log_level(self) -> LogLevel:
        return self._log_level

    @log_level.setter
    def log_level(self, log_level: LogLevel) -> None:
        self._log_level = log_level

    def status(self, *text, **kwargs) -> Status:
        return self._stdout.status(*text, **kwargs)

    def print(self, *text, **kwargs) -> None:
        self._stdout.print(*text, **kwargs)

    def info(self, *text, raw: bool = False, **kwargs) -> None:
        self._write(*text, log_level=LogLevel.INFO, raw=raw, **kwargs)

    def debug(self, *text, raw: bool = False, **kwargs) -> None:
        self._write(*text, log_level=LogLevel.DEBUG, raw=raw, **kwargs)

    def trace(self, *text, raw: bool = False, **kwargs) -> None:
        self._write(*text, log_level=LogLevel.TRACE, raw=raw, **kwargs)

    def warn(self, *text, raw: bool = False, **kwargs) -> None:
        self._write(*text, log_level=LogLevel.WARN, raw=raw, **kwargs)

    def error(self, *text, raw: bool = False, **kwargs) -> None:
        self._write(*text, log_level=LogLevel.ERROR, raw=raw, **kwargs)

    def infop(self, obj: Any, **kwargs) -> None:
        self._pretty_print(obj, LogLevel.INFO, **kwargs)

    def debugp(self, obj: Any, **kwargs) -> None:
        self._pretty_print(obj, LogLevel.DEBUG, **kwargs)

    def tracep(self, obj: Any, **kwargs) -> None:
        self._pretty_print(obj, LogLevel.TRACE, **kwargs)

    def warnp(self, obj: Any, **kwargs) -> None:
        self._pretty_print(obj, LogLevel.WARN, **kwargs)

    def _write(
        self,
        *text,
        log_level: LogLevel,
        raw: bool = False,
        **kwargs,
    ) -> None:
        if self.log_level < log_level:
            return

        use_stderr = log_level in {LogLevel.WARN, LogLevel.ERROR}

        # Dim the text color for all non-warn log-levels.
        color = f"dim {log_level.color}" if use_stderr else log_level.color

        # Only thre prefix should be colored.
        prefix = f"[{color}]{self._timestamp()} {log_level.upper()}:[/{color}]"

        # Prevent squre-brackets from being parsed as `rich` markup.
        text = [Text(t) for t in text] if raw is True else text

        console = self._stderr if use_stderr else self._stdout
        console.print(prefix, *text, **kwargs)

    def _pretty_print(
        self,
        obj: Any,
        log_level: LogLevel,
        **kwargs,
    ) -> None:
        if self.log_level < log_level:
            return

        # Print the log-level and timestamp.
        self._write("", log_level=log_level)

        # Print the object.
        pprint(obj, **kwargs, console=self._stdout)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
