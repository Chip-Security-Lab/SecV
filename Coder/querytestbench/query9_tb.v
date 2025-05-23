`timescale 1ns/1ps

module sft_tb;

    // DUT Signals
    reg clk;
    reg rst;
    reg [3:0] a;
    wire [3:0] q;

    // Instantiate DUT
    sft dut (
        .clk(clk),
        .rst(rst),
        .a(a),
        .q(q)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // Clock period = 10ns
    end

    // Test Procedure
    integer error_count = 0;

    initial begin
        $dumpfile("sft_tb.vcd");
        $dumpvars(0, sft_tb);

        $display("START TESTING...");

        // Initialize signals
        rst = 0;
        a = 4'b0000;

        // Test Case 1: Reset functionality
        #10 rst = 1; // Assert reset
        #10 rst = 0; // Deassert reset
        #10;
        if (q !== 4'b0000) begin
            $display("FAIL: Test Case 1 - Reset failed, q=%b", q);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end else begin
            $display("%0d TEST CASE(S) FAILED!", error_count);
        end

        $finish;
    end

endmodule
