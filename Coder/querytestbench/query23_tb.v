`timescale 1ns/1ps

module glitchEx_tb;

    // DUT Signals
    reg in0, in1, sel;
    wire z;

    // Instantiate DUT
    glitchEx dut (
        .in0(in0),
        .in1(in1),
        .sel(sel),
        .z(z)
    );

    // Testbench Variables
    integer error_count = 0;
    reg expected_case1, expected_case2;

    // Test Procedure
    initial begin
        $dumpfile("glitchEx_tb.vcd");
        $dumpvars(0, glitchEx_tb);

        $display("START TESTING...");

        // Test Case 1: sel=0, in0=0, in1=0
        sel = 0; in0 = 0; in1 = 0;
        #10;
        expected_case1 = (in0 & ~sel) | (in1 & sel);
        expected_case2 = expected_case1 | (in0 & in1);
        if (z !== expected_case1 && z !== expected_case2) begin
            $display("FAIL: Test Case 1 - Expected z=%b or z=%b, got z=%b", expected_case1, expected_case2, z);
            error_count = error_count + 1;
        end

        // Test Case 2: sel=0, in0=1, in1=0
        sel = 0; in0 = 1; in1 = 0;
        #10;
        expected_case1 = (in0 & ~sel) | (in1 & sel);
        expected_case2 = expected_case1 | (in0 & in1);
        if (z !== expected_case1 && z !== expected_case2) begin
            $display("FAIL: Test Case 2 - Expected z=%b or z=%b, got z=%b", expected_case1, expected_case2, z);
            error_count = error_count + 1;
        end

        // Test Case 3: sel=1, in0=0, in1=1
        sel = 1; in0 = 0; in1 = 1;
        #10;
        expected_case1 = (in0 & ~sel) | (in1 & sel);
        expected_case2 = expected_case1 | (in0 & in1);
        if (z !== expected_case1 && z !== expected_case2) begin
            $display("FAIL: Test Case 3 - Expected z=%b or z=%b, got z=%b", expected_case1, expected_case2, z);
            error_count = error_count + 1;
        end

        // Test Case 4: sel=1, in0=1, in1=1
        sel = 1; in0 = 1; in1 = 1;
        #10;
        expected_case1 = (in0 & ~sel) | (in1 & sel);
        expected_case2 = expected_case1 | (in0 & in1);
        if (z !== expected_case1 && z !== expected_case2) begin
            $display("FAIL: Test Case 4 - Expected z=%b or z=%b, got z=%b", expected_case1, expected_case2, z);
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
