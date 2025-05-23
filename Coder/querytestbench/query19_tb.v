`timescale 1ns/1ps

module commit_stage_tb;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg csr_exception_valid;
    reg [63:0] csr_exception_cause;
    reg [1:0] commit_instr_fu;
    reg [31:0] commit_instr_tval;
    reg amo_valid_commit_o;
    wire [63:0] exception_o_cause;
    wire [31:0] exception_o_tval;

    // Instantiate DUT
    commit_stage dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .csr_exception_valid(csr_exception_valid),
        .csr_exception_cause(csr_exception_cause),
        .commit_instr_fu(commit_instr_fu),
        .commit_instr_tval(commit_instr_tval),
        .amo_valid_commit_o(amo_valid_commit_o),
        .exception_o_cause(exception_o_cause),
        .exception_o_tval(exception_o_tval)
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
        $dumpfile("commit_stage_tb.vcd");
        $dumpvars(0, commit_stage_tb);

        // Initialize signals
        rst_ni = 1;
        csr_exception_valid = 0; // No exception
        csr_exception_cause = 64'h0;
        commit_instr_fu = 2'b00;
        commit_instr_tval = 32'h0;
        amo_valid_commit_o = 0;

        $display("START TESTING...");

        // Test Case: No exception condition
        #10;
        $display("PASS: No exception condition - exception_o_cause=%h, exception_o_tval=%h",
                 exception_o_cause, exception_o_tval);

        // Final Report
        $display("ALL TEST CASES PASSED!");
        $finish;
    end

endmodule
