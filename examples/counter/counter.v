module counter (
    input wire clk,
    input wire rst_n,
    output reg [7:0] count
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 8'h00;
        end else begin
            count <= count + 1'b1;
        end
    end

endmodule
