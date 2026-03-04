# CLI Cheat Sheet

## Compilation
```bash
# Basic compile
rtlverify compile path/to/design.v --top my_module

# Verbose compile
rtlverify -v compile path/to/design.v --top my_module
```

## Simulation
```bash
# Real simulation with Verilator
rtlverify simulate path/to/design.v --top my_module --max-time 1000

# Mock mode (no Verilator required)
rtlverify simulate path/to/design.v --top my_module --mock

# Custom testbench
rtlverify simulate design.v --top design --tb testbench.cpp
```
