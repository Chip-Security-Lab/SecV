`timescale 1ns/1ps

module tb_mod_exp();
    parameter WIDTH = 32;
    parameter CLK_PERIOD = 10;
    parameter MAX_FAILED_CASES = 100;  // 定义最大失败用例数

    reg                 clk;
    reg                 rst;
    reg  [WIDTH-1:0]    base_in;
    reg  [WIDTH-1:0]    exponent_in;
    reg  [WIDTH-1:0]    modulus_in;
    wire [WIDTH-1:0]    result_out;
    
    // 使用普通数组替代队列
    reg [31:0] failed_cases[0:MAX_FAILED_CASES-1];
    integer failed_count;

    mod_exp #(.WIDTH(WIDTH)) dut (
        .clk(clk),
        .rst(rst),
        .base_in(base_in),
        .exponent_in(exponent_in),
        .modulus_in(modulus_in),
        .result_out(result_out)
    );

    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end

    function [WIDTH-1:0] compute_mod_exp;
        input [WIDTH-1:0] base, exponent, modulus;
        reg [WIDTH-1:0] result, base_temp, exp_temp;
        begin
            result = 1;
            base_temp = base;
            exp_temp = exponent;
            while (exp_temp > 0) begin
                if (exp_temp[0])
                    result = (result * base_temp) % modulus;
                base_temp = (base_temp * base_temp) % modulus;
                exp_temp = exp_temp >> 1;
            end
            compute_mod_exp = result;
        end
    endfunction

    task verify_result;
        input [WIDTH-1:0] base, exponent, modulus;
        input [31:0] case_num;
        reg [WIDTH-1:0] expected_result;
        begin
            base_in = base;
            exponent_in = exponent;
            modulus_in = modulus;
            expected_result = compute_mod_exp(base, exponent, modulus);
            #(20*CLK_PERIOD);
            if (result_out !== expected_result) begin
                failed_cases[failed_count] = case_num;
                failed_count = failed_count + 1;
            end
        end
    endtask

    initial begin
        rst = 1;
        base_in = 0;
        exponent_in = 0;
        modulus_in = 0;
        failed_count = 0;  // 初始化失败计数器
        
        #(5*CLK_PERIOD);
        rst = 0;
        #(CLK_PERIOD);

        verify_result(2, 3, 5, 1);    // 2^3 mod 5 = 3
        verify_result(3, 5, 7, 2);    // 3^5 mod 7 = 5
        verify_result(2, 8, 11, 3);   // 2^8 mod 11 = 3
        verify_result(4, 13, 497, 4); // 4^13 mod 497 = 445
        verify_result(3, 10, 13, 5);  // 3^10 mod 13 = 9

        #(CLK_PERIOD);
        if (failed_count == 0)
            $display("\nALL TEST CASES PASSED!");
        else begin
            $display("\nTEST CASE(S) FAILED!");
            for (integer i = 0; i < failed_count; i = i + 1)
                $display("Failed case number: %d", failed_cases[i]);
        end
        
        $finish;
    end

endmodule