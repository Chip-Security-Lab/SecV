`timescale 1ns/1ps

module fsm_1_tb;

    // DUT Signals
    reg [2:0] user_input;
    reg clk;
    reg rst_n;
    wire [2:0] out;

    // Instantiate DUT
    fsm_1 dut (
        .out(out),
        .user_input(user_input),
        .clk(clk),
        .rst_n(rst_n)
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
        $dumpfile("fsm_1_tb.vcd");
        $dumpvars(0, fsm_1_tb);

        // Initialize signals
        rst_n = 0;
        user_input = 3'h0;

        $display("START TESTING...");

        // Test Case 1: Reset
        #10;
        rst_n = 1;
        #10;
        if (out !== 3'b100) begin
            $display("FAIL: Test Case 1 - Reset failed, out=%b", out);
            error_count = error_count + 1;
        end

        // Test Case 2: Input 3'h3 -> State 2'h3
        user_input = 3'h3;
        #10;
        if (out !== 3'b111) begin
            $display("FAIL: Test Case 2 - Input=3'h3, expected out=3'b111, got out=%b", out);
            error_count = error_count + 1;
        end

        // Test Case 3: Input 3'h4 -> State 2'h2
        user_input = 3'h4;
        #10;
        if (out !== 3'b110) begin
            $display("FAIL: Test Case 3 - Input=3'h4, expected out=3'b110, got out=%b", out);
            error_count = error_count + 1;
        end

        // Test Case 4: Input 3'h5 -> State 2'h1
        user_input = 3'h5;
        #10;
        if (out !== 3'b101) begin
            $display("FAIL: Test Case 4 - Input=3'h5, expected out=3'b101, got out=%b", out);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end

        $finish;
    end

endmodule
