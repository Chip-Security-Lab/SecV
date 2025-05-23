`timescale 1ns/1ps

module axi_tb;

    // Parameters
    localparam NB_SUBORDINATE = 4; // Number of subordinates
    localparam NB_MANAGER = 2;     // Number of managers

    // DUT Signals
    reg [(NB_SUBORDINATE * NB_MANAGER * 3) - 1:0] access_ctrl_i;
    reg [2:0] priv_lvl_i;
    wire [(NB_SUBORDINATE * NB_MANAGER) - 1:0] connectivity_map_o;

    // Instantiate DUT
    axi #(
        .NB_SUBORDINATE(NB_SUBORDINATE),
        .NB_MANAGER(NB_MANAGER)
    ) dut (
        .access_ctrl_i(access_ctrl_i),
        .priv_lvl_i(priv_lvl_i),
        .connectivity_map_o(connectivity_map_o)
    );

    // Testbench Variables
    integer error_count = 0;

    // Helper function to calculate flat index
    function integer flat_index(input integer i, input integer j, input integer k);
        flat_index = (i * NB_MANAGER + j) * 3 + k;
    endfunction

    // Test Procedure
    initial begin
        $dumpfile("axi_tb.vcd");
        $dumpvars(0, axi_tb);

        $display("START TESTING...");

        // Test Case 1: Verify basic mapping
        access_ctrl_i = 0; // Initialize to zero
        access_ctrl_i[flat_index(0, 0, 0)] = 1; // Subordinate 0, Manager 0: Level 0 access
        access_ctrl_i[flat_index(0, 1, 1)] = 1; // Subordinate 0, Manager 1: Level 1 access
        access_ctrl_i[flat_index(1, 0, 2)] = 1; // Subordinate 1, Manager 0: Level 2 access
        priv_lvl_i = 3'b001; // Privilege level 1
        #10;

        if (connectivity_map_o[0] !== 0) begin
            $display("FAIL: Test Case 1 - connectivity_map_o[0] expected 0, got %b", connectivity_map_o[0]);
            error_count = error_count + 1;
        end
        if (connectivity_map_o[1] !== 1) begin
            $display("FAIL: Test Case 1 - connectivity_map_o[1] expected 1, got %b", connectivity_map_o[1]);
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
