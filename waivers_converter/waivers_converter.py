# Copyright (c) Antmicro
# SPDX-License-Identifier: Apache-2.0

import argparse
from pathlib import Path
import sys
from typing import Any, Generator, Union, cast
import yaml

from .common import (
    INSTANCE_EXCLUDE,
    MODULE_EXCLUDE,
    MODULE_SPECIFIC,
    SOURCE_PATH,
    SPECIAL_KEYS,
    Emitter,
    ToggleDirection,
    eprint,
)

# Backends
from .el_backend import ELEmitter
from .md_backend import MDEmitter


def expand_range(items: Union[str, int, list[Union[str, int]]]) -> Generator[int, None, None]:
    if isinstance(items, list):
        for it in items:
            if isinstance(it, int):
                yield it
            else:
                start, end = sorted(int(x) for x in it.split("-"))
                yield from range(start, end + 1)
    elif isinstance(items, str):
        start, end = sorted(int(x) for x in items.split("-"))
        yield from range(start, end + 1)
    else:
        yield items


def expand_toggles(bits: Union[str, int]) -> list[Union[int, tuple[int, int]]]:
    if isinstance(bits, int):
        return [bits]

    result: list[Union[int, tuple[int, int]]] = []
    for part in bits.split(";"):
        if "-" in part:
            start, end = sorted(int(x) for x in part.split("-"))
            result.append((start, end))
        else:
            result.append(int(part))
    return result


def exclude_instance(emitter: Emitter, items: dict[str, dict[str, list[Union[str, int, dict[Union[str, int], list[Union[str, int]]]]]]]):
    for reason, coverage in items.items():
        emitter.set_reason(reason)

        for coverage_type, coverage_data in coverage.items():
            if coverage_type == "line":
                # This is a safe assumption based on the schema
                for line in expand_range(cast(list[Union[str, int]], coverage_data)):
                    emitter.exclude_line(line)
            elif coverage_type == "branch":
                for value in coverage_data:
                    if isinstance(value, dict):
                        for branch, vectors in value.items():
                            for vector in expand_range(vectors):
                                emitter.exclude_branch(branch, vector)
                            break
                    else:
                        for branch in expand_range(value):
                            emitter.exclude_branch(branch, None)
            elif coverage_type == "cond":
                for value in coverage_data:
                    if isinstance(value, dict):
                        for cond, rows in value.items():
                            for r in rows:
                                emitter.exclude_cond(cond, str(r))
                            break
                    else:
                        for cond in expand_range(value):
                            emitter.exclude_cond(cond, None)
            elif coverage_type == "fsm":
                for value in coverage_data:
                    if isinstance(value, str):
                        emitter.exclude_fsm(value, None)
                    elif isinstance(value, dict):
                        for name, transitions in value.items():
                            for t in transitions:
                                emitter.exclude_fsm(str(name), str(t))
                            break
                    else:
                        eprint(f"Invalid format for an fsm exclusion: {value}")
            elif coverage_type == "assert":
                for value in coverage_data:
                    if isinstance(value, str):
                        emitter.exclude_assert(value)
                    else:
                        eprint(f"Invalid format for an assert exclusion: {value}")
            elif coverage_type in ("toggle", "toggle_01", "toggle_10"):
                dir: ToggleDirection = None
                if coverage_type == "toggle_10":
                    dir = "1->0"
                elif coverage_type == "toggle_01":
                    dir = "0->1"

                for value in coverage_data:
                    if isinstance(value, str):
                        emitter.exclude_toggle(value, dir, None)
                    elif isinstance(value, dict):
                        for name, bits in value.items():
                            for b in bits:
                                emitter.exclude_toggle(str(name), dir, expand_toggles(b))
                            break
            else:
                eprint(f"Unknown coverage type: {coverage_type}")


def exclude_fully(emitter: Emitter, items: dict[str, list[str]], instance: bool):
    for reason, objects in items.items():
        emitter.set_reason(reason)
        for v in objects:
            if instance:
                emitter.start_instance(v)
            else:
                emitter.start_module(v, None)

            emitter.exclude_fully()

            if instance:
                emitter.end_instance()
            else:
                emitter.end_module()

def main():
    all_emitters: dict[str, type[Emitter]] = {
        "el": ELEmitter,
        "md": MDEmitter,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--format", type=str, required=True)
    parser.add_argument("--design", type=str)
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()

    if args.format not in all_emitters:
        print(f"Format '{args.format}' does not exist, available formats: {', '.join(all_emitters.keys())}")
        sys.exit(1)

    emitter = all_emitters[args.format](args.design)

    with Path(args.input).open("rt") as file:
        content = yaml.safe_load(file)

    for block, module in cast(dict[str, Any], content).items():
        emitter.start_block(block)

        for module_name, instances in cast(dict[str, Any], module).items():
            if module_name == MODULE_EXCLUDE:
                exclude_fully(emitter, instances, instance=False)
                continue
            elif module is SPECIAL_KEYS:
                continue

            emitter.start_module(module_name, instances.get(SOURCE_PATH))

            for instance_name, instance in instances.items():
                if instance_name == INSTANCE_EXCLUDE:
                    exclude_fully(emitter, instance, instance=True)
                    continue
                elif instance_name == MODULE_SPECIFIC:
                    pass
                elif instance_name in SPECIAL_KEYS:
                    continue

                has_instance = instance_name != MODULE_SPECIFIC
                if has_instance:
                    emitter.start_instance(instance_name)

                exclude_instance(emitter, instance)

                if has_instance:
                    emitter.end_instance()

            emitter.end_module()

        emitter.end_block()

    Path(args.output).write_text(emitter.stringify())
