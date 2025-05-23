`timescale 1ns/1ps

module csr_regfile_tb;

    // Parameters
    localparam WIDTH = 64;

    // DUT Signals
    reg clk;
    reg rst;
    reg csr_we;
    reg [WIDTH-1:0] csr_wdata;
    reg [WIDTH-1:0] mie_q;
    reg [WIDTH-1:0] mideleg_q;
    reg [11:0] csr_addr;
    wire [WIDTH-1:0] mie_d;

    // Instantiate DUT
    csr_regfile #(
        .WIDTH(WIDTH)
    ) dut (
        .clk(clk),
        .rst(rst),
        .csr_we(csr_we),
        .csr_wdata(csr_wdata),
        .mie_q(mie_q),
        .mideleg_q(mideleg_q),
        .csr_addr(csr_addr),
        .mie_d(mie_d)
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
        $dumpfile("csr_regfile_tb.vcd");
        $dumpvars(0, csr_regfile_tb);

        $display("START TESTING...");

        // Initialize signals
        rst = 1;
        csr_we = 0;
        csr_wdata = 0;
        mie_q = 0;
        mideleg_q = 0;
        csr_addr = 12'h0;

        // Test Case 1: Reset functionality
        #10 rst = 0; // Deassert reset
        #10;
        if (mie_d !== 0) begin
            $display("FAIL: Test Case 1 - Reset failed, mie_d=%h", mie_d);
            error_count = error_count + 1;
        end

        // Test Case 2: CSR write to other address
        rst = 1; #10; rst = 0; // Ensure reset
        csr_we = 1;
        csr_addr = 12'h105; // Address not affecting MIE
        csr_wdata = 64'h5555555555555555;
        mie_q = 64'hFFFFFFFFFFFFFFFF;
        mideleg_q = 64'h0;
        #10;
        if (mie_d !== mie_q) begin
            $display("FAIL: Test Case 2 - CSR write to non-SIE address failed, mie_d=%h, expected=%h", mie_d, mie_q);
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
