# Copyright (c) Antmicro
# SPDX-License-Identifier: Apache-2.0

import argparse
from collections.abc import Callable
from pathlib import Path
import sys
import yaml


TOP_COMMENT = 'File generated automatically, see comments above waiver groups for their sources'


class Waiver:
    def __init__(self, definition : str, type : str):
        self.definition : str = definition
        self.type : str = type


class SignalWaiver(Waiver):
    def __init__(self, prefix_with_top : bool, definition : str):
        super().__init__(definition, 'signal')
        self.prefix_with_top : bool = prefix_with_top


class WaiversDef:
    SIGNAL_TYPE_KEY = 'signals-type'
    DEFAULT_SIGNAL_TYPE = 'partial'

    class IgnoredException(Exception):
        def __init__(self, cause : str):
            self.cause : str = cause

    def __init__(self, top : str, path : Path, name : str, def_keys : dict[str, dict]):
        self.name : str = name
        self.path : Path = path
        self.waivers : list[Waiver] = []

        warn: Callable[[str], None] = lambda line: print(f'{name}: {line}')

        except_values : list[str] = def_keys.pop('except', [])
        if top in except_values:
            raise self.IgnoredException(f'top in "except": {except_values}')

        only_values : list[str] = def_keys.pop('only', [top])
        if top not in only_values:
            raise self.IgnoredException(f'top not in "only": {only_values}')

        signal_type : str = def_keys.pop(self.SIGNAL_TYPE_KEY, self.DEFAULT_SIGNAL_TYPE)
        if signal_type not in ['full', 'partial']:
            warn(f'Invalid {self.SIGNAL_TYPE_KEY}: {signal_type}')
            signal_type = self.DEFAULT_SIGNAL_TYPE
        prefix_with_top : bool = signal_type == 'partial'

        # Note that `pop` was used before so the keys above aren't in def_keys anymore.
        for key in def_keys:
            if key == 'signals':
                for definition in def_keys['signals']:
                    self.waivers.append(SignalWaiver(prefix_with_top, definition))
            elif key in ['files', 'modules']:
                for definition in def_keys[key]:
                    self.waivers.append(Waiver(definition, type=key.removesuffix('s')))
            else:
                warn(f'Unsupported key: {key}')


def parse_waivers_file(path : Path, top : str) -> list[WaiversDef]:
    print(f'Parsing {path}...')
    with open(path) as f:
        data : dict = yaml.safe_load(f)

    waiver_defs : list[WaiversDef] = []
    for def_name, def_keys in data.items():
        try:
            waiver_defs.append(WaiversDef(top, path, def_name, def_keys))
        except WaiversDef.IgnoredException as e:
            print(f'{def_name}: Ignoring due to {e.cause}')
            continue
    return waiver_defs


class CmCfg:
    @staticmethod
    def _get_keyword(waiver : Waiver):
        if waiver.type == 'signal':
            return 'node'
        return waiver.type

    def __init__(self, top : str):
        self.lines = [
            f'// {TOP_COMMENT}',
            f'+tree {top}',
            f'-module {top}',
            '',
        ]
        self.top = top
        self.signal_waivers = {}

    def add_waivers(self, waivers_def : WaiversDef):
        full_name = f'{waivers_def.path} : {waivers_def.name}'
        self.lines.append(f'// {full_name}')
        for waiver in waivers_def.waivers:
            definition = waiver.definition
            if isinstance(waiver, SignalWaiver) and waiver.prefix_with_top:
                definition = f"{self.top}.*{definition}"
            self.lines.append(f'-{self._get_keyword(waiver)} {definition}')
        self.lines.append('')

    def save(self, output : Path):
        with open(output, 'wt') as file:
            file.write('\n'.join(self.lines))


OUTPUT_CONVERTERS = {
    'cm.cfg': CmCfg,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('waiver_files', type=Path, nargs='+', help='Yaml files with waiver definitions')
    parser.add_argument('-o', '--output', type=Path, required=True, help='Output path for the created file with waivers')
    parser.add_argument('--top', type=str, required=True, help='Top level module name')
    args = parser.parse_args()

    filename: str = args.output.name
    print(f'Converting waivers for top={args.top}, output type: {filename}')

    if filename not in OUTPUT_CONVERTERS:
        print(f'Unknown file type: {filename}')
        sys.exit(1)
    converter: type = OUTPUT_CONVERTERS[filename]

    waivers_defs : list[WaiversDef] = []
    for file in args.waiver_files:
        waivers_defs.extend(parse_waivers_file(file, args.top))

    cm_hier = converter(args.top)
    for waivers_def in waivers_defs:
        cm_hier.add_waivers(waivers_def)
    cm_hier.save(args.output)

    print(f'Output saved in {args.output}')
