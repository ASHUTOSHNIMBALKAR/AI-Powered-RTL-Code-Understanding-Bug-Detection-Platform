from rtl_verify_platform.analysis.fsm import FSMExtractor

def test_fsm_extraction():
    verilog = """
    module fsm(input clk);
        localparam IDLE = 2'b00;
        localparam READ = 2'b01;
        localparam WRITE = 2'b10;
    endmodule
    """
    extractor = FSMExtractor(verilog)
    states = extractor.extract_states()
    assert "IDLE" in states
    assert "READ" in states
    assert "WRITE" in states
