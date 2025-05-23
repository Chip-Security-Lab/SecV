`timescale 1ns/1ps

module jtag_auth_good_tb;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg [31:0] pass_hash;
    reg [31:0] exp_hash;
    reg hashValid;
    wire pass_check;
    wire [1:0] state_q;

    // Instantiate DUT
    jtag_auth_good dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .pass_hash(pass_hash),
        .exp_hash(exp_hash),
        .hashValid(hashValid),
        .pass_check(pass_check),
        .state_q(state_q),
        .miss_pass_check_cnt_q()
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
        $dumpfile("jtag_auth_good_tb.vcd");
        $dumpvars(0, jtag_auth_good_tb);

        $display("START TESTING...");

        // Initialize signals
        rst_ni = 0;
        pass_hash = 0;
        exp_hash = 0;
        hashValid = 0;

        // Test Case 1: Reset functionality
        #15 rst_ni = 1; // Deassert reset
        #10;
        if (state_q !== 2'b00 || pass_check !== 1'b0) begin
            $display("FAIL: Test Case 1 - Reset failed, state_q=%b, pass_check=%b", state_q, pass_check);
            error_count = error_count + 1;
        end 

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end 

        $finish;
    end

endmodule
