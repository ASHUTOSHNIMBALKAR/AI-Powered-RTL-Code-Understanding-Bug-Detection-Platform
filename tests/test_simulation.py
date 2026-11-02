import os
from pathlib import Path
import pytest
from rtl_verify_platform.core.config import config_manager
from rtl_verify_platform.simulation.engine import SimulationEngine

COUNTER_RTL = Path(__file__).parents[1] / "examples" / "counter" / "counter.v"

def test_config_loading():
    """Verify configuration loads key fields successfully."""
    engine = config_manager.get("simulator.default_engine")
    assert engine in ["verilator", "mock"]

def test_clk_rst_detection():
    """Verify regex-based clock and reset detection on the counter module."""
    engine = SimulationEngine()
    clocks, resets = engine.detect_clk_rst(COUNTER_RTL)
    
    assert "clk" in clocks
    assert len(resets) == 1
    assert resets[0]["name"] == "rst_n"
    assert resets[0]["active"] == "low"

def test_mock_simulation(tmp_path):
    """Verify mock simulation output structures and files."""
    engine = SimulationEngine(output_dir=tmp_path)
    res = engine.compile_and_simulate(
        rtl_files=[COUNTER_RTL],
        top_module="counter",
        use_mock=True
    )
    
    assert res["success"] is True
    assert "completed_mock" in res["stage"]
    assert res["vcd_path"] is not None
    assert Path(res["vcd_path"]).exists()
    
    # Read generated VCD file to ensure it's not empty
    with open(res["vcd_path"], "r") as f:
        vcd_content = f.read()
    assert "$scope module counter" in vcd_content
    assert "clk" in vcd_content
    assert "rst_n" in vcd_content

def test_real_or_fallback_simulation(tmp_path):
    """Verify standard compile and simulate workflow execution."""
    engine = SimulationEngine(output_dir=tmp_path)
    res = engine.compile_and_simulate(
        rtl_files=[COUNTER_RTL],
        top_module="counter"
    )
    
    # Whether mock fallback triggered or real run was executed, success should be True
    assert res["success"] is True
    assert res["vcd_path"] is not None
    assert Path(res["vcd_path"]).exists()
