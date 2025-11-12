# Configuration Schema Guide

The platform uses YAML configuration located at `configs/default_config.yaml`.

## Schema Sections

### `simulator`
- `default_engine`: "verilator" or "mock"
- `verilator_path`: Path to Verilator binary
- `cxx_compiler`: C++ compiler (default: g++)
- `output_dir`: Simulation build directory (default: sim_build)
- `vcd_filename`: Output waveform filename (default: waveform.vcd)

### `ai`
- `provider`: "openai" | "huggingface" | "mock"
- `model`: Model identifier (e.g. gpt-4-turbo)
- `local_hf_model`: HuggingFace model repo
- `temperature`: LLM sampling temperature
