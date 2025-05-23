`timescale 1ns/1ps

module bootrom_tb;

    // Parameters
    localparam RomSize = 256;

    // DUT Signals
    reg clk_i;
    reg req_i;
    reg [31:0] addr_i;
    wire [31:0] rdata_o;

    // Instantiate DUT
    bootrom dut (
        .clk_i(clk_i),
        .req_i(req_i),
        .addr_i(addr_i),
        .rdata_o(rdata_o)
    );

    // Clock Generation
    initial begin
        clk_i = 0;
        forever #5 clk_i = ~clk_i; // Clock period = 10ns
    end

    // Initialize ROM content
    initial begin
        for (integer i = 0; i < RomSize; i = i + 1) begin
            dut.mem[i] = i; // 初始化ROM内容，地址值等于数据值
        end
    end

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("bootrom_tb.vcd");
        $dumpvars(0, bootrom_tb);

        // Initialize signals
        req_i = 0;
        addr_i = 0;

        $display("START TESTING...");

        // Test Case 1: Normal data access
        req_i = 1;
        addr_i = 32'h8; // 对应 mem[1]
        #10;
        if (rdata_o !== dut.mem[1]) begin
            $display("FAIL: Test Case 1 - Expected rdata_o=%h, got rdata_o=%h", dut.mem[1], rdata_o);
            error_count = error_count + 1;
        end

        // Test Case 2: Address update
        addr_i = 32'h10; // 对应 mem[2]
        #10;
        if (rdata_o !== dut.mem[2]) begin
            $display("FAIL: Test Case 2 - Expected rdata_o=%h, got rdata_o=%h", dut.mem[2], rdata_o);
            error_count = error_count + 1;
        end

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end

        $finish;
    end

endmodule
