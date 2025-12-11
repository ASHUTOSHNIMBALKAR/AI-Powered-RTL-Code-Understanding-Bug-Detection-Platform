# Simulation & Waveform Debugging Guide

## Workflow Overview
1. Check syntax with `rtlverify compile <file.v> --top <mod>`
2. Simulate with `rtlverify simulate <file.v> --top <mod> --max-time 2000`
3. Inspect `sim_build/waveform.vcd` with GTKWave or Surfer.

## Verilator Compilation Flags
The platform automatically generates trace-enabled builds:
- `--cc`: Generates C++ models.
- `--exe`: Links with generated C++ testbench wrapper.
- `--trace`: Enables VCD waveform dumping.
