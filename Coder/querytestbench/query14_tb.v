`timescale 1ns/1ps

module register_write_once_example_tb;

    // DUT Signals
    reg [15:0] Data_in;
    reg Clk;
    reg ip_resetn;
    reg global_resetn;
    reg write;
    wire [15:0] Data_out;

    // Instantiate DUT
    register_write_once_example dut (
        .Data_in(Data_in),
        .Clk(Clk),
        .ip_resetn(ip_resetn),
        .global_resetn(global_resetn),
        .write(write),
        .Data_out(Data_out)
    );

    // Clock Generation
    initial begin
        Clk = 0;
        forever #5 Clk = ~Clk; // Clock period = 10ns
    end

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("register_write_once_example_tb.vcd");
        $dumpvars(0, register_write_once_example_tb);

        // Initialize signals
        ip_resetn = 1;
        global_resetn = 1;
        write = 0;
        Data_in = 16'h0000;

        $display("START TESTING...");

        // Test Case 1: Reset
        ip_resetn = 0;
        #10;
        ip_resetn = 1;
        #10;
        if (Data_out !== 16'h0000) begin
            $display("FAIL: Test Case 1 - Reset failed, Data_out=%h", Data_out);
            error_count = error_count + 1;
        end

        // Test Case 2: Hold state
        #20;
        if (Data_out[0] !== 1'b0) begin
            $display("FAIL: Test Case 2 - Hold state failed, LSB of Data_out=%b", Data_out[0]);
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
