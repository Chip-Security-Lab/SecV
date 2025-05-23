`timescale 1ns/1ps

module register_lock_tb;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg jtag_unlock;
    wire [5:0] reglk_mem;

    // Instantiate DUT
    register_lock dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .jtag_unlock(jtag_unlock),
        .reglk_mem(reglk_mem)
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
        $dumpfile("register_lock_tb.vcd");
        $dumpvars(0, register_lock_tb);

        // Initialize signals
        rst_ni = 1;
        jtag_unlock = 0;

        $display("START TESTING...");

        // Test Case 1: Global reset
        rst_ni = 0;
        #10;
        rst_ni = 1;
        #10;
        for (integer i = 0; i < 6; i = i + 1) begin
            if (reglk_mem[i] !== 1'b0) begin
                $display("FAIL: Test Case 1 - reglk_mem[%0d] expected 0, got %b", i, reglk_mem[i]);
                error_count = error_count + 1;
            end
        end

        // Test Case 2: JTAG unlock reset
        jtag_unlock = 1;
        #10;
        jtag_unlock = 0;
        #10;
        for (integer i = 0; i < 6; i = i + 1) begin
            if (reglk_mem[i] !== 1'b0) begin
                $display("FAIL: Test Case 2 - reglk_mem[%0d] expected 0, got %b", i, reglk_mem[i]);
                error_count = error_count + 1;
            end
        end

        // Test Case 3: Normal operation
        rst_ni = 1;
        jtag_unlock = 0;
        #20;
        for (integer i = 0; i < 6; i = i + 1) begin
            if (reglk_mem[i] !== 1'b0) begin
                $display("FAIL: Test Case 3 - reglk_mem[%0d] changed unexpectedly, got %b", i, reglk_mem[i]);
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
