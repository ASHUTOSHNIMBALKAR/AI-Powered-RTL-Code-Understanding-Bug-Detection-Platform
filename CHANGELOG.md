# Changelog

All notable changes to the AI-Powered RTL Code Understanding & Bug Detection Platform will be documented here.

## [0.1.0] - 2026-10-20

### Added
- **Simulation Engine**: Support for Verilator compilation and execution with auto C++ testbench generation.
- **Auto Port Detection**: Regex-based automatic detection of clock and reset ports.
- **Mock Fallback**: Synthetic simulation and VCD waveform output when Verilator is unavailable.
- **VCD Parser**: Value Change Dump parser for extracting signals and transition timelines.
- **CLI Framework**: Typer and Rich console integration with `compile` and `simulate` commands.
- **Configuration**: YAML-based configuration manager with dot-notation lookup.
- **AI Stubs**: Architecture and interfaces for OpenAI GPT-4 and HuggingFace code reasoning.
- **Analysis Modules**: FSM state extraction and glitch detection stubs.
- **Examples**: Counter, Shift Register, and Arithmetic Logic Unit (ALU) Verilog models.
- **Test Suite**: Pytest suite covering simulation, parsing, and configuration.
