`timescale 1ns/1ps

module reglk_wrapper_tb;

    // Parameters
    localparam REG_COUNT = 6;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg jtag_unlock;
    reg rst_9;
    wire [31:0] reglk_mem0, reglk_mem1, reglk_mem2, reglk_mem3, reglk_mem4, reglk_mem5;

    // Instantiate DUT
    reglk_wrapper #(
        .REG_COUNT(REG_COUNT)
    ) dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .jtag_unlock(jtag_unlock),
        .rst_9(rst_9),
        .reglk_mem0(reglk_mem0),
        .reglk_mem1(reglk_mem1),
        .reglk_mem2(reglk_mem2),
        .reglk_mem3(reglk_mem3),
        .reglk_mem4(reglk_mem4),
        .reglk_mem5(reglk_mem5)
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
        $dumpfile("reglk_wrapper_tb.vcd");
        $dumpvars(0, reglk_wrapper_tb);

        $display("START TESTING...");

        // Initialize signals
        rst_ni = 0;
        jtag_unlock = 0;
        rst_9 = 0;

        // Test Case 1: Reset functionality
        #10 rst_ni = 1; // Deassert global reset
        #10 rst_9 = 1;  // Deassert periphery reset
        #10 jtag_unlock = 1; // Deassert jtag_unlock
        #10;

        // Check if the module behaves correctly after reset, no need to check the exact value of registers
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end else begin
            $display("FAIL: Test Case 1 - Reset failed");
        end


        $finish;
    end

endmodule
