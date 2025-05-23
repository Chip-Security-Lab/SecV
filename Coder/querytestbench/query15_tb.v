`timescale 1ns/1ps

module sha256_wrapper_tb;

    // Parameters
    localparam REG_COUNT = 4;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg rst_3;
    wire startHash;
    wire [7:0] data0, data1, data2, data3;

    // Instantiate DUT
    sha256_wrapper #(
        .REG_COUNT(REG_COUNT)
    ) dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .rst_3(rst_3),
        .wdata(8'h00), // Default values for unused inputs
        .addr(2'b00),
        .we(1'b0),
        .hashValid(1'b0),
        .startHash(startHash),
        .data0(data0),
        .data1(data1),
        .data2(data2),
        .data3(data3)
    );

    // Clock Generation
    initial begin
        clk_i = 0;
        forever #5 clk_i = ~clk_i; // Clock period = 10ns
    end

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("sha256_wrapper_tb.vcd");
        $dumpvars(0, sha256_wrapper_tb);

        $display("START TESTING...");

        // Initialize signals
        rst_ni = 0;
        rst_3 = 0;

        // Test Case 1: Reset functionality
        #10 rst_ni = 1; rst_3 = 1; // Deassert reset
        #10;
        if (startHash !== 0 || data0 !== 0 || data1 !== 0 || data2 !== 0 || data3 !== 0) begin
            $display("FAIL: Test Case 1 - Reset failed, startHash=%b, data0=%h, data1=%h, data2=%h, data3=%h", startHash, data0, data1, data2, data3);
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
