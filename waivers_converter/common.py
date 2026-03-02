# Copyright (c) Antmicro
# SPDX-License-Identifier: Apache-2.0

import sys
from typing import Any, Literal, Optional, Union


MODULE_EXCLUDE = "fully_excluded_modules"
INSTANCE_EXCLUDE = "fully_excluded_instances"
SOURCE_PATH = "source_path"
SOURCE_SHA = "source_sha"
SCHEMA_VERSION = "schema_version"
MODULE_SPECIFIC = "all"
SPECIAL_KEYS = {SCHEMA_VERSION, SOURCE_PATH, SOURCE_SHA, MODULE_EXCLUDE, INSTANCE_EXCLUDE, MODULE_SPECIFIC}


def eprint(*values: object):
    print(*values, file=sys.stderr)


ToggleDirection = Literal["0->1", "1->0", None]


class Emitter:
    def __init__(self, *args: Any) -> None:
        pass

    # State callbacks

    def set_reason(self, reason: str) -> None:
        pass  # Do nothing by default

    def start_block(self, block_name: str) -> None:
        pass  # Do nothing by default

    def end_block(self) -> None:
        pass  # Do nothing by default

    def start_module(self, module_name: str, module_path: Optional[str]) -> None:
        pass  # Do nothing by default

    def end_module(self) -> None:
        pass  # Do nothing by default

    def start_instance(self, instance_name: str) -> None:
        pass  # Do nothing by default

    def end_instance(self) -> None:
        pass  # Do nothing by default

    # Exclude callbacks

    def exclude_fully(self) -> None:
        pass  # Do nothing by default

    def exclude_line(self, number: int) -> None:
        pass  # Do nothing by default

    def exclude_branch(self, branch: Union[str, int], vector: Optional[int]) -> None:
        pass  # Do nothing by default

    def exclude_cond(self, cond: Union[str, int], row: Optional[str]) -> None:
        pass  # Do nothing by default

    def exclude_fsm(self, fsm: str, transition: Optional[str]) -> None:
        pass  # Do nothing by default

    def exclude_assert(self, name: str) -> None:
        pass  # Do nothing by default

    def exclude_toggle(self, name: str, dir: ToggleDirection, bits: Optional[list[Union[int, tuple[int, int]]]]) -> None:
        pass  # Do nothing by default

    # Misc

    def stringify(self) -> str:
        return ""
