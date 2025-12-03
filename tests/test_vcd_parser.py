from pathlib import Path
from rtl_verify_platform.simulation.vcd_parser import VCDParser

def test_vcd_parser_empty(tmp_path):
    dummy_vcd = tmp_path / "test.vcd"
    dummy_vcd.write_text("$timescale 1ns $end\n$var wire 1 # clk $end\n$enddefinitions $end\n#0\n0#\n")
    
    parser = VCDParser(dummy_vcd)
    res = parser.parse()
    assert res["signal_count"] == 1
    assert "#" in res["signals"]
    assert res["signals"]["#"]["name"] == "clk"
