`timescale 1ns/1ps

module csr_access_check_tb;

    // Parameters
    localparam CSR_ADDR_WIDTH = 12;
    localparam PRIV_LVL_WIDTH = 2;

    // DUT Signals
    reg csr_we;
    reg csr_read;
    reg [CSR_ADDR_WIDTH-1:0] csr_addr_i;
    reg [PRIV_LVL_WIDTH-1:0] priv_lvl_o;
    reg debug_mode_q;
    wire csr_exception_valid;
    wire [1:0] csr_exception_cause;

    // Instantiate DUT
    csr_access_check #(
        .CSR_ADDR_WIDTH(CSR_ADDR_WIDTH),
        .PRIV_LVL_WIDTH(PRIV_LVL_WIDTH)
    ) dut (
        .csr_we(csr_we),
        .csr_read(csr_read),
        .csr_addr_i(csr_addr_i),
        .priv_lvl_o(priv_lvl_o),
        .debug_mode_q(debug_mode_q),
        .csr_exception_valid(csr_exception_valid),
        .csr_exception_cause(csr_exception_cause)
    );

    // Testbench Variables
    integer error_count = 0;

    // Test Procedure
    initial begin
        // Open VCD file for waveform analysis
        $dumpfile("csr_access_check_tb.vcd");
        $dumpvars(0, csr_access_check_tb);

        // Initialize signals
        csr_we = 0;
        csr_read = 0;
        csr_addr_i = 12'h000;
        priv_lvl_o = 2'b00;
        debug_mode_q = 0;

        $display("START TESTING...");

        // Test Case 1: No CSR access
        #10;
        if (csr_exception_valid !== 0 || csr_exception_cause !== 2'b00) begin
            $display("FAIL: Test Case 1 - Unexpected exception when no CSR access");
            error_count = error_count + 1;
        end 

        // Test Case 2: Debug mode access violation
        csr_we = 1;
        csr_addr_i = 12'h7b0;  // Debug-specific CSR address
        debug_mode_q = 0;      // Not in debug mode
        #10;
        if (csr_exception_valid !== 1 || csr_exception_cause !== 2'b01) begin
            $display("FAIL: Test Case 2 - Exception not triggered on debug access violation");
            error_count = error_count + 1;
        end 

        // Final Report
        if (error_count == 0) begin
            $display("ALL TEST CASES PASSED!");
        end else begin
            $display("%d TEST CASES FAILED!", error_count);
        end

        // End Simulation
        $finish;
    end

endmodule
