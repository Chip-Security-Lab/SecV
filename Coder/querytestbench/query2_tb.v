`timescale 1ns/1ps

module foo_bar_tb;

    // Parameters
    localparam DATA_WIDTH = 32;

    // DUT Signals
    reg [DATA_WIDTH-1:0] data_in;
    reg [DATA_WIDTH-1:0] incoming_id;
    reg clk;
    reg rst_n;
    wire [DATA_WIDTH-1:0] data_out;

    // Instantiate DUT
    foo_bar dut (
        .data_out(data_out),
        .data_in(data_in),
        .incoming_id(incoming_id),
        .address(), // Address not used, keep unconnected
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
        $dumpfile("foo_bar_tb.vcd");
        $dumpvars(0, foo_bar_tb);

        // Initialize signals
        data_in = 32'h0;
        incoming_id = 32'h0;
        rst_n = 1;

        $display("START TESTING...");

        // Test Case 1: Reset functionality
        rst_n = 0;
        #10;
        if (data_out !== 32'h0 || dut.q !== 32'h0) begin
            $display("FAIL: Test Case 1 - Reset failed, data_out=%h, q=%h", data_out, dut.q);
            error_count = error_count + 1;
        end
        rst_n = 1;

        // Test Case 2: Write authorization fails
        data_in = 32'hA5A5A5A5;
        incoming_id = 32'h0; // No match with acl_oh_allowlist
        #10;
        if (data_out === data_in) begin
            $display("FAIL: Test Case 2 - Unauthorized write failed, data_out=%h", data_out);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end

        $finish;
    end

endmodule
