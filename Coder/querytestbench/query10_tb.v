`timescale 1ns/1ps

module csr_regfile_tb;

    
    parameter PRIV_LVL_M = 2'b11;
    parameter PRIV_LVL_U = 2'b00;

    // DUT Signals
    reg clk;
    reg rst;
    reg umode_i;
    reg [1:0] priv_lvl_q;
    reg ebreakm;
    reg ebreaku;
    wire debug_mode_q;
    wire [1:0] priv_lvl_o;

    // Instantiate DUT
    csr_regfile dut (
        .clk(clk),
        .rst(rst),
        .umode_i(umode_i),
        .priv_lvl_q(priv_lvl_q),
        .ebreakm(ebreakm),
        .ebreaku(ebreaku),
        .debug_mode_q(debug_mode_q),
        .priv_lvl_o(priv_lvl_o)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test Procedure
    integer error_count = 0;

    initial begin
        $dumpfile("csr_regfile_tb.vcd");
        $dumpvars(0, csr_regfile_tb);

        $display("START TESTING...");

        // Initialize signals
        rst = 0;
        umode_i = 1'b0;
        priv_lvl_q = PRIV_LVL_U;
        ebreakm = 1'b0;
        ebreaku = 1'b0;

        // Test Case 1: Initial conditions with reset
        #10 rst = 1;
        #10 rst = 0;

        if (debug_mode_q !== 1'b0 || priv_lvl_o !== PRIV_LVL_U) begin
            $display("FAIL: Test Case 1 - Expected debug_mode_q=0, priv_lvl_o=PRIV_LVL_U, got debug_mode_q=%b, priv_lvl_o=%b", debug_mode_q, priv_lvl_o);
            error_count = error_count + 1;
        end 

        // Test Case 2: User mode does not change when ebreaku is not triggered
        #10 priv_lvl_q = PRIV_LVL_U;
        #10 ebreaku = 1'b0;
        #10;

        if (priv_lvl_o !== PRIV_LVL_U) begin
            $display("FAIL: Test Case 2 - Expected priv_lvl_o=PRIV_LVL_U, got priv_lvl_o=%b", priv_lvl_o);
            error_count = error_count + 1;
        end 

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end 

        $finish;
    end

endmodule
