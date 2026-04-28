# waivers-converter

Copyright (c) 2025-2026 [Antmicro](https://www.antmicro.com)

Tool converting generic waivers to HDL simulator-specific waivers.

## Usage

Input YAML files with waivers (see example below) can be converted with:
```
waivers-converter example-waivers.yaml <output-file> --format <format>
```

Supported formats are:
* `md` - Generates a Markdown table listing the exclusions
* `el` - Generates an EL file

### Example input YAML file

```yaml
top:                                 # Name of the block, there can be multiple blocks in the file
  sample_module:                     # Name of the module for which the exclusions should apply
    source_path: "some/file/module.sv"
    sample_instance:                 # Name of an instance of the `sample_module` module, for which the exclusions below should apply
                                     # If the name is `all` the exclusions apply to the entire module instead
      Exclusion reason:
        line: [10-20, 168]           # Exclude lines 10-20 and 168 from "some/file/module.sv"
        toggle:                      # Both 0->1 and 1->0 transitions will be excluded
          - signal0                  # Fully exclude signal0
          - signal1: [1, 3-5, 12]    # Exclude signal[1], signal1[3-5] and signal1[12]
        toggle_10:                   # Use toggle_01 to exclude 0->1 transitions instead
          - signal2                  # Exclude 1->0 transitions from all bits of signal2
          - signal3: [5-7]           # Exclude 1->0 transitions from bits 5-7 of signal3
        fsm:
          - fsm0:
            - STATE0->STATE1 "0->1"  # Exclude the STATE0->STATE1 transition from fsm0. "0->1" is the numerical representation of the states.
          - fsm1                     # Fully exclude fsm1
        assert:
          - assertion0               # Exclude assert named `assertion0`
        branch:
          - 5: [2]                   # Exclude vector 2 from branch 5
          - 27                       # Exclude branch 27 fully
        cond:
          - 3: [2 "01"]              # Exclude subexpression '2 "01"' from condition 3
          - 12                       # Exclude condition 12 fully

    fully_excluded_instances:        # List of instances of the `sample_module` module that should be fully excluded
      Exclusion reason:
        - sample_instance2
        - sample_instance3

  fully_excluded_modules:            # List of modules that should be fully excluded
    Exclusion reason:
      - sample_module2
```
