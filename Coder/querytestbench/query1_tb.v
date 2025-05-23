`timescale 1ns/1ps

module foo_bar_tb;

    // Parameters
    localparam DATA_WIDTH = 70;
    localparam USER_ID_WIDTH = 20;

    // DUT Signals
    reg [DATA_WIDTH-1:0] data_in;
    reg [USER_ID_WIDTH-1:0] usr_id;
    reg clk;
    reg rst_n;
    wire [DATA_WIDTH-1:0] data_out;

    // Instantiate DUT
    foo_bar dut (
        .data_out(data_out),
        .usr_id(usr_id),
        .data_in(data_in),
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
        data_in = 70'h0;
        usr_id = 20'h0;
        rst_n = 1;

        // Test Case 1: Reset functionality
        rst_n = 0;
        #10;
        if (data_out !== 70'h0) begin
            $display("FAIL: Test Case 1 - Reset failed, data_out=%h", data_out);
            error_count = error_count + 1;
        end
        rst_n = 1;

        // Test Case 2: Authorized access
        data_in = 70'hABCDE12345;
        usr_id = 20'h4; // Authorized user
        #10;
        if (data_out !== data_in) begin
            $display("FAIL: Test Case 2 - Authorized access failed, data_out=%h", data_out);
            error_count = error_count + 1;
        end

        // Test Case 3: Unauthorized access
        data_in = 70'hFEDCBA9876;
        usr_id = 20'h5; // Unauthorized user
        #10;
        if (data_out === data_in) begin
            $display("FAIL: Test Case 3 - Unauthorized access failed, data_out=%h", data_out);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end 

        $finish;
    end

endmodule
