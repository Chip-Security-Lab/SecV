`timescale 1ns/1ps

module fsm_tb;

    // DUT Signals
    reg [3:0] register_address;
    wire gpio_out;

    // Instantiate DUT
    fsm dut (
        .register_address(register_address),
        .gpio_out(gpio_out)
    );

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("fsm_tb.vcd");
        $dumpvars(0, fsm_tb);

        // Initialize signals
        register_address = 4'b0000;

        $display("START TESTING...");

        // Test Case 1: Default state
        #10;
        if (gpio_out !== 0) begin
            $display("FAIL: Test Case 1 - Default state failed, gpio_out=%b", gpio_out);
            error_count = error_count + 1;
        end

        // Test Case 2: Unmatched address
        register_address = 4'b0010; // Non-matching address
        #10;
        if (gpio_out !== 0) begin
            $display("FAIL: Test Case 2 - Unmatched address failed, gpio_out=%b", gpio_out);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end

        $finish;
    end

endmodule
