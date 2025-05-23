import os
import subprocess
from typing import Tuple, Dict, List
from collections import defaultdict

class VerilogTester:
    def __init__(self, design_file: str, testbench_file: str):
        self.verilog_files = [design_file, testbench_file]
        self.compiled_file = "simulation.out"

    def check_syntax_and_simulate(self) -> Tuple[bool, str]:

        syntax_ok, compile_output = self._compile_verilog()
        if not syntax_ok:
            return False, compile_output

        simulation_output = self._run_simulation()
        return True, simulation_output

    def _compile_verilog(self) -> Tuple[bool, str]:
        compile_command = ["iverilog", "-o", self.compiled_file] + self.verilog_files
        try:
            result = subprocess.run(compile_command, 
                                  check=False,
                                  capture_output=True,
                                  text=True)
            return result.returncode == 0, result.stderr
        except Exception as e:
            return False, str(e)

    def _run_simulation(self) -> str:
        try:
            result = subprocess.run(["vvp", self.compiled_file],
                                  check=False,
                                  capture_output=True,
                                  text=True)
            return result.stdout
        except Exception as e:
            return str(e)
        finally:
            if os.path.exists(self.compiled_file):
                os.remove(self.compiled_file)

def get_result_folders() -> List[Tuple[str, str, str]]:
    """获取所有最底层文件夹的路径
    返回格式: [(query_folder, subfolder, full_path), ...]
    例如: [("query1", "result4", "result/query1/result4"), ...]
    """
    folders = []
    base_path = "result"
    
    # 检查基础目录是否存在
    if not os.path.exists(base_path):
        print(f"error: {base_path} not found")
        return []
    
    for i in range(1, 24):  # 1 到 23
        query_folder = f"query{i}"
        query_path = os.path.join(base_path, query_folder)
        if os.path.exists(query_path):
            try:
                # 获取该query文件夹下的所有子文件夹
                subfolders = [f for f in os.listdir(query_path) 
                            if os.path.isdir(os.path.join(query_path, f))]
                for subfolder in subfolders:
                    full_path = os.path.join(query_path, subfolder)
                    folders.append((query_folder, subfolder, full_path))
            except Exception as e:
                print(f"error: process {query_path} failed: {str(e)}")
                continue
    
    if not folders:
        print("warning: no folders to process")  
    return folders

def process_result_folder(query_folder: str, subfolder: str, full_path: str) -> List[Tuple[str, bool, str, bool]]:
    """处理单个result子文件夹的所有文件
    返回: [(文件名, 编译成功, 输出内容, 仿真通过), ...]
    """
    results = []
    
    if not os.path.exists(full_path):
        print(f"error: {full_path} not found")
        return []
        
    files = [f for f in os.listdir(full_path) 
            if os.path.isfile(os.path.join(full_path, f))]
    
    if not files:
        print(f"warning: {full_path} has no files")
        return []
    
    query_num = query_folder.replace("query", "")
    testbench_file = f"querytestbench/query{query_num}_tb.v"
    
    if not os.path.exists(testbench_file):
        print(f"error: testbench file {testbench_file} not found")
        return []
    
    for file in files:
        design_file = os.path.join(full_path, file)
        
        tester = VerilogTester(design_file, testbench_file)
        syntax_ok, output = tester.check_syntax_and_simulate()
        
        # 检查是否通过所有测试用例
        simulation_passed = False
        if syntax_ok and "ALL TEST CASES PASSED!" in output:
            simulation_passed = True
            
        results.append((file, syntax_ok, output, simulation_passed))
    
    return results

def batch_test_all_folders() -> Dict[str, Dict]:
    all_results = {}
    folders = get_result_folders()
    
    for query_folder, subfolder, full_path in folders:
        results = process_result_folder(query_folder, subfolder, full_path)
        if results:
            folder_key = f"{query_folder}/{subfolder}"
            success_count = sum(1 for _, syntax_ok, _, _ in results if syntax_ok)
            simulation_passed_count = sum(1 for _, _, _, sim_passed in results if sim_passed)
            total_count = len(results)
            
            all_results[folder_key] = {
                'total_files': total_count,
                'success_count': success_count,
                'simulation_passed_count': simulation_passed_count,
                'details': results
            }
    
    return all_results

if __name__ == "__main__":
    results = batch_test_all_folders()
    
    print("writing results to simulation_results.txt")
    # 创建输出文件
    with open("simulation_results.txt", "w") as f:
        # 输出统计结果
        for folder_key, folder_data in results.items():
            f.write(f"\n=== {folder_key}  ===\n")
            f.write(f"total: {folder_data['total_files']}\n")
            f.write(f"syntax pass: {folder_data['success_count']}\n") 
            f.write(f"function pass: {folder_data['simulation_passed_count']}\n")
            
            f.write("\nDetailed Results:\n")
            for file, syntax_ok, output, sim_passed in folder_data['details']:
                f.write(f"\nFile: {file}\n")
                f.write(f"Compilation: {'Pass' if syntax_ok else 'Fail'}\n")
                if syntax_ok:
                    f.write(f"Simulation: {'Pass' if sim_passed else 'Fail'}\n")
                    f.write(f"Simulation Output:\n{output}\n")
    print("done")