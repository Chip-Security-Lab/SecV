`timescale 1ns/1ps

module acct_wrapper_tb;

    // Parameters
    localparam AcCt_MEM_SIZE = 8;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg rst_6;
    wire [AcCt_MEM_SIZE*32-1:0] acct_mem;

    // Instantiate DUT
    acct_wrapper #(
        .AcCt_MEM_SIZE(AcCt_MEM_SIZE)
    ) dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .rst_6(rst_6),
        .acct_mem(acct_mem)
    );

    // Clock Generation
    initial begin
        clk_i = 0;
        forever #5 clk_i = ~clk_i; // Clock period = 10ns
    end

    // Testbench Variables
    integer error_count = 0;
    integer i;

    // Test Procedure
    initial begin
        $dumpfile("acct_wrapper_tb.vcd");
        $dumpvars(0, acct_wrapper_tb);

        // Initialize signals
        rst_ni = 1;
        rst_6 = 1;

        $display("START TESTING...");

        // Test Case: Normal operation
        #20; // Let the clock run without reset
        for (i = 0; i < AcCt_MEM_SIZE; i = i + 1) begin
            if (acct_mem[i*32 +: 32] !== 32'h00000000) begin
                $display("FAIL: Normal operation - acct_mem[%0d] changed unexpectedly, got 0x%08h", i, acct_mem[i*32 +: 32]);
                error_count = error_count + 1;
            end
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end

        $finish;
    end

endmodule
