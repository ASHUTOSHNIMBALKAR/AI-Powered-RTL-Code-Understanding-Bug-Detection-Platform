# Platform Architecture Specification

## Overview
The platform provides a dual-layer verification bridge:
1. **Hardware Layer**: Verilog/SystemVerilog -> Verilator -> C++ Testbench -> VCD Waveform
2. **Intelligence Layer**: VCD Signal Analysis -> LLM Reasoning -> Bug Diagnosis Report

## Core Components
- `rtl_verify_platform.core.config`: YAML ConfigManager with dot-notation lookup.
- `rtl_verify_platform.core.logger`: Structured Rich console logging.
- `rtl_verify_platform.simulation.engine`: Orchestrates compile and simulation workflows.
- `rtl_verify_platform.simulation.templates`: Jinja-style C++ testbench generation.
- `rtl_verify_platform.cli.main`: Typer CLI with interactive tables and panels.
