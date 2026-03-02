# Copyright (c) Antmicro
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Any, Optional, Union
from tabulate import tabulate

from .common import Emitter, ToggleDirection


@dataclass
class TableRow:
    module: str
    instance: str
    type: str
    what: str
    reason: str

    @classmethod
    def header(cls, include_instance: bool) -> list[str]:
        if include_instance:
            return ["Module", "Instance", "Coverage Type", "What", "Reason"]
        else:
            return ["Module", "Coverage Type", "What", "Reason"]

    def to_tuple(self, include_instance: bool) -> tuple[str, ...]:
        if include_instance:
            return (self.module, self.instance, self.type, self.what, self.reason)
        else:
            return (self.module, self.type, self.what, self.reason)


class MDEmitter(Emitter):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.current_module: str = ""
        self.current_instance: str = ""
        self.current_reason: str = ""
        self.rows: list[TableRow] = []
        self.has_instance_specific_waivers: bool = False

    def set_reason(self, reason: str) -> None:
        self.current_reason = reason

    def start_module(self, module_name: str, module_path: Optional[str]) -> None:
        self.current_module = module_name

    def start_instance(self, instance_name: str) -> None:
        self.has_instance_specific_waivers = True
        self.current_instance = instance_name

    def end_instance(self) -> None:
        self.current_instance = ""

    def exclude_fully(self) -> None:
        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="module" if len(self.current_instance) == 0 else "instance",
            what="-",
            reason=self.current_reason,
        ))

    def exclude_line(self, number: int) -> None:
        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="line",
            what=str(number),
            reason=self.current_reason
        ))

    def exclude_branch(self, branch: Union[str, int], vector: Optional[int]) -> None:
        what = str(branch)
        if vector is not None:
            what += f" ({vector})"

        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="cond",
            what=what,
            reason=self.current_reason
        ))

    def exclude_cond(self, cond: Union[str, int], row: Optional[str]) -> None:
        what = str(cond)
        if row is not None:
            what += f" ({row})"

        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="cond",
            what=what,
            reason=self.current_reason
        ))

    def exclude_fsm(self, fsm: str, transition: Optional[str]) -> None:
        what = str(fsm)
        if transition is not None:
            what += f" ({transition})"

        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="fsm",
            what=what,
            reason=self.current_reason
        ))

    def exclude_assert(self, name: str) -> None:
        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type="assert",
            what=name,
            reason=self.current_reason
        ))

    def exclude_toggle(self, name: str, dir: ToggleDirection, bits: Optional[list[Union[int, tuple[int, int]]]]) -> None:
        type = "toggle"
        if dir is not None:
            type += f" {dir}"

        what = name
        if bits is not None:
            what += "[" + "][".join(str(x) if isinstance(x, int) else f"{x[1]}:{x[0]}" for x in bits) + "]"

        self.rows.append(TableRow(
            module=self.current_module,
            instance=self.current_instance,
            type=type,
            what=what,
            reason=self.current_reason
        ))

    def stringify(self) -> str:
        output: list[tuple[str, ...]] = []
        for row in self.rows:
            output.append(row.to_tuple(include_instance=self.has_instance_specific_waivers))

        return tabulate(output, tablefmt="github", headers=TableRow.header(self.has_instance_specific_waivers))
