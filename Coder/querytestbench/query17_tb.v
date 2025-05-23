`timescale 1ns/1ps

module lock_jtag_tb;

    // DUT Signals
    reg clk;
    reg reset;
    reg en;
    reg d;
    wire lock_jtag;

    // Instantiate DUT
    lock_jtag dut (
        .clk(clk),
        .reset(reset),
        .en(en),
        .d(d),
        .lock_jtag(lock_jtag)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // Clock period = 10ns
    end

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("lock_jtag_tb.vcd");
        $dumpvars(0, lock_jtag_tb);

        $display("START TESTING...");

        // Initialize signals
        reset = 1; en = 0; d = 0;

        // Test Case 1: Enable and set lock_jtag
        en = 1; d = 1;
        #10;
        if (lock_jtag !== 1) begin
            $display("FAIL: Test Case 1 - Enable failed, lock_jtag=%b", lock_jtag);
            error_count = error_count + 1;
        end 
        // Test Case 2: Disable and maintain lock_jtag
        en = 0; d = 0;
        #10;
        if (lock_jtag !== 1) begin
            $display("FAIL: Test Case 2 - Disable failed, lock_jtag=%b", lock_jtag);
            error_count = error_count + 1;
        end 

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end 

        $finish;
    end

endmodule
