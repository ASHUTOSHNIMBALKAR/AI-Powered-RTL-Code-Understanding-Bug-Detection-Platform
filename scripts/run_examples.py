#!/usr/bin/env python3
"""Run simulation on all example modules."""
from pathlib import Path
from rtl_verify_platform.simulation.engine import SimulationEngine

def main():
    engine = SimulationEngine()
    examples = [
        ("examples/counter/counter.v", "counter"),
        ("examples/shift_reg/shift_reg.v", "shift_reg"),
        ("examples/alu/alu.v", "alu"),
    ]
    for rtl, top in examples:
        print(f"--> Testing {top}...")
        res = engine.compile_and_simulate([Path(rtl)], top, use_mock=True)
        print(f"    Status: {'PASS' if res['success'] else 'FAIL'}")

if __name__ == "__main__":
    main()
