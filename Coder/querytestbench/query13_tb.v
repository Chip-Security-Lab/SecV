`timescale 1ns/1ps

module aes1_wrapper_tb;

    // Parameters
    localparam KEY_WIDTH = 8;

    // DUT Signals
    reg debug_mode_i;
    reg [KEY_WIDTH-1:0] key_reg0;
    reg [KEY_WIDTH-1:0] key_reg1;
    wire [KEY_WIDTH-1:0] core_key0;
    wire [KEY_WIDTH-1:0] core_key1;

    // Instantiate DUT
    aes1_wrapper #(
        .KEY_WIDTH(KEY_WIDTH)
    ) dut (
        .debug_mode_i(debug_mode_i),
        .key_reg0(key_reg0),
        .key_reg1(key_reg1),
        .core_key0(core_key0),
        .core_key1(core_key1)
    );

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("aes1_wrapper_tb.vcd");
        $dumpvars(0, aes1_wrapper_tb);

        $display("START TESTING...");

        // Initialize signals
        debug_mode_i = 0;
        key_reg0 = 8'hAA; // 1010 1010
        key_reg1 = 8'h55; // 0101 0101

        // Test Case 1: Normal operation (debug_mode_i = 0)
        #10;
        if (core_key0 !== key_reg0 || core_key1 !== key_reg1) begin
            $display("FAIL: Test Case 1 - Normal operation failed, core_key0=%b, core_key1=%b", core_key0, core_key1);
            error_count = error_count + 1;
        end

        // Test Case 3: Normal operation restore
        debug_mode_i = 0; // Ensure debug mode is disabled
        #10;
        if (core_key0 !== key_reg0 || core_key1 !== key_reg1) begin
            $display("FAIL: Test Case 3 - Normal operation restore failed, core_key0=%b, core_key1=%b", core_key0, core_key1);
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
