# waivers-converter

Copyright (c) 2025 [Antmicro](https://www.antmicro.com)

Tool converting generic waivers to HDL simulator-specific waivers.

## Usage

Input YAML files with waivers (see example below) can be converted with:
```
waivers-converter --out <output-file> --top example_top example-waivers.yaml
```

### Example input YAML file

```yaml
Example waivers:
  # Waivers specified below will only be present in output files for
  # top modules listed below, i.e., with `--top example_top` passed.
  only:
  - example_top

  # By default signals are `partial` which causes prepending top names to the
  # `signals` entries. For example, `example_instance.signal.a` will become
  # `example_top.*example_instance.signal.a` if `waivers-converter` is called
  # with `--top example_top`. The alternative is `signals-type: full` in which
  # case `signals` entries need to start with top module names.
  signals-type: partial

  # Note that signals specified below will be waived regardless of module.
  # Entries from `modules` and `files` don't restrict signal waivers to
  # these modules and files but are independent waivers.
  signals:
  - example_instance.signal.a
  - example_instance.signal.b.*
  - another_instance.signal.c[63:32]
  - another_signal_with_some_bits_unused[20:16]
  - another_signal_with_some_bits_unused[12:4]

  # The modules specified below will be waived.
  modules:
  - example_module
  - ...

  # The files specified below will be waived.
  files:
  - example_file.sv
  - ...


Reserved bits:
  # Waivers specified below will be present in output files for all
  # top modules except `another_top`.
  except:
  - another_top

  signals:
  - reserved_bit
  - ...

Tied to zero:
  # Waivers specified below will be present in output files regardless
  # of the name of the top module.
  signals:
  - ...
```
