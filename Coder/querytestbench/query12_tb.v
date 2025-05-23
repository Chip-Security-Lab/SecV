`timescale 1ns/1ps

module aes0_wrapper_tb;

    // Parameters
    localparam ADDR_WIDTH = 8;
    localparam DATA_WIDTH = 32;

    // DUT Signals
    reg clk_i;
    reg rst_ni;
    reg rst_1;
    reg en;
    reg we;
    reg [ADDR_WIDTH-1:0] address;
    reg [DATA_WIDTH-1:0] wdata;
    reg ct_valid;
    reg [3:0] reglk_ctrl_i;
    wire [DATA_WIDTH-1:0] p_c0, p_c1, p_c2, p_c3;
    wire start;

    // Instantiate DUT
    aes0_wrapper #(
        .ADDR_WIDTH(ADDR_WIDTH),
        .DATA_WIDTH(DATA_WIDTH)
    ) dut (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .rst_1(rst_1),
        .en(en),
        .we(we),
        .address(address),
        .wdata(wdata),
        .ct_valid(ct_valid),
        .reglk_ctrl_i(reglk_ctrl_i),
        .p_c0(p_c0),
        .p_c1(p_c1),
        .p_c2(p_c2),
        .p_c3(p_c3),
        .start(start)
    );

    // Clock Generation
    initial begin
        clk_i = 0;
        forever #5 clk_i = ~clk_i; // Clock period = 10ns
    end

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        $dumpfile("aes0_wrapper_tb.vcd");
        $dumpvars(0, aes0_wrapper_tb);

        $display("START TESTING...");

        // Initialize signals
        rst_ni = 1;
        rst_1 = 1;
        en = 0;
        we = 0;
        address = 0;
        wdata = 0;
        ct_valid = 0;
        reglk_ctrl_i = 4'b0000;

        // Test Case 1: Reset
        rst_ni = 0; rst_1 = 1;
        #10;
        rst_ni = 1;
        #10;
        if (start !== 0 || p_c0 !== 0 || p_c1 !== 0 || p_c2 !== 0 || p_c3 !== 0) begin
            $display("FAIL: Test Case 1 - Reset failed");
            error_count = error_count + 1;
        end

        // Test Case 2: Write to locked register
        address = 8'h08; wdata = 32'hDEADBEEF; reglk_ctrl_i = 4'b1000;
        en = 1; we = 1;
        #10;
        if (p_c3 === 32'hDEADBEEF) begin
            $display("FAIL: Test Case 2 - Write to locked register succeeded, p_c3=%h", p_c3);
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
