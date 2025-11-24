// 8-bit Arithmetic Logic Unit
module alu (
    input wire clk,
    input wire rst_n,
    input wire [7:0] a,
    input wire [7:0] b,
    input wire [2:0] opcode,
    output reg [7:0] result,
    output reg zero,
    output reg carry
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result <= 8'h00;
            zero <= 1'b0;
            carry <= 1'b0;
        end else begin
            case (opcode)
                3'b000: {carry, result} <= a + b;        // ADD
                3'b001: {carry, result} <= a - b;        // SUB
                3'b010: result <= a & b;                // AND
                3'b011: result <= a | b;                // OR
                3'b100: result <= a ^ b;                // XOR
                3'b101: result <= ~a;                   // NOT
                3'b110: result <= a << 1;               // SLL
                3'b111: result <= a >> 1;               // SRL
                default: result <= 8'h00;
            endcase
            zero <= (result == 8'h00);
        end
    end

endmodule
