import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from rtl_verify_platform.core.logger import logger
from rtl_verify_platform.core.config import config_manager
from rtl_verify_platform.simulation.templates import generate_cpp_tb

class SimulationEngine:
    """Compiles Verilog/SystemVerilog RTL and runs simulations using Verilator or a mock fallback."""
    
    COMMENT_PATTERN = re.compile(r"//.*|/\*.*?\*/", flags=re.DOTALL)
    INPUT_PATTERN = re.compile(r"\binput\s+(?:wire\s+|reg\s+|logic\s+)?(?:\[[^\]]*\]\s*)?(\w+)\b", re.IGNORECASE)

    def __init__(self, output_dir: str | Path = None):
        config_out = config_manager.get("simulator.output_dir", "sim_build")
        self.output_dir = Path(output_dir or config_out)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verilator_path = config_manager.get("simulator.verilator_path", "verilator")
        self.cxx_compiler = config_manager.get("simulator.cxx_compiler", "g++")

    def detect_clk_rst(self, rtl_path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
        """Parses Verilog source to auto-detect clock and reset inputs."""
        clocks = []
        resets = []
        
        if not rtl_path.exists():
            return clocks, resets

        try:
            with open(rtl_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            content_no_comments = self.COMMENT_PATTERN.sub("", content)
            inputs = self.INPUT_PATTERN.findall(content_no_comments)
            
            for inp in inputs:
                inp_lower = inp.lower()
                if "clk" in inp_lower or "clock" in inp_lower:
                    clocks.append(inp)
                elif "rst" in inp_lower or "reset" in inp_lower:
                    active = "low" if ("_n" in inp_lower or "n" in inp_lower) else "high"
                    resets.append({"name": inp, "active": active})
        except Exception as e:
            logger.error(f"Error parsing RTL file {rtl_path}: {e}")
            
        return clocks, resets

    def compile_and_simulate(
        self,
        rtl_files: List[str | Path],
        top_module: str,
        custom_tb_path: str | Path = None,
        max_sim_time: int = 1000,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        rtl_paths = [Path(f) for f in rtl_files]
        vcd_name = config_manager.get("simulator.vcd_filename", "waveform.vcd")
        vcd_path = self.output_dir / vcd_name
        
        engine_mode = config_manager.get("simulator.default_engine", "verilator")
        
        if not use_mock and engine_mode == "verilator":
            if not shutil.which(self.verilator_path):
                logger.warning("Verilator not found in PATH. Falling back to MOCK mode.")
                use_mock = True

        if use_mock or engine_mode == "mock":
            return self._run_mock_simulation(top_module, vcd_path, max_sim_time)

        logger.info(f"Starting Verilator simulation compile for {top_module}...")
        
        tb_cpp_path = self.output_dir / f"tb_{top_module}.cpp"
        if custom_tb_path:
            shutil.copy(custom_tb_path, tb_cpp_path)
            logger.info(f"Using custom testbench: {custom_tb_path}")
        else:
            clocks, resets = self.detect_clk_rst(rtl_paths[0])
            if not clocks:
                clocks = ["clk"]
            if not resets:
                resets = [{"name": "rst_n", "active": "low"}]
            
            tb_content = generate_cpp_tb(
                top_module=top_module,
                vcd_filename=str(vcd_path.resolve()).replace("\\", "/"),
                clocks=clocks,
                resets=resets,
                max_sim_time=max_sim_time
            )
            with open(tb_cpp_path, "w", encoding="utf-8") as f:
                f.write(tb_content)
            logger.info(f"Auto-generated C++ testbench wrapper at {tb_cpp_path}")

        build_dir = self.output_dir / "obj_dir"
        cmd = [
            self.verilator_path,
            "--cc",
            *[str(p.resolve()) for p in rtl_paths],
            "--exe",
            str(tb_cpp_path.resolve()),
            "--trace",
            "-Mdir",
            str(build_dir.resolve()),
            "--prefix",
            f"V{top_module}",
            "-Wall"
        ]
        
        logger.debug(f"Running Verilator cmd: {' '.join(cmd)}")
        try:
            verilate_res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Verilator compilation failed:\n{e.stderr}")
            return {
                "success": False,
                "stage": "verilate",
                "stderr": e.stderr,
                "stdout": e.stdout
            }
        except FileNotFoundError:
            logger.error("Verilator executable not found.")
            return {"success": False, "error": "Verilator not installed or not in PATH."}

        make_cmd = ["make", "-C", str(build_dir.resolve()), "-f", f"V{top_module}.mk"]
        logger.debug(f"Running Make cmd: {' '.join(make_cmd)}")
        try:
            make_res = subprocess.run(make_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Make build failed:\n{e.stderr}")
            return {
                "success": False,
                "stage": "make",
                "stderr": e.stderr,
                "stdout": e.stdout
            }

        exe_path = build_dir / f"V{top_module}"
        if not exe_path.exists() and (build_dir / f"V{top_module}.exe").exists():
            exe_path = build_dir / f"V{top_module}.exe"
            
        logger.info(f"Executing simulation binary: {exe_path}")
        try:
            sim_res = subprocess.run([str(exe_path.resolve())], capture_output=True, text=True, check=True)
            return {
                "success": True,
                "stage": "completed",
                "stdout": sim_res.stdout,
                "stderr": sim_res.stderr,
                "vcd_path": str(vcd_path.resolve()) if vcd_path.exists() else None
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Simulation execution failed:\n{e.stderr}")
            return {
                "success": False,
                "stage": "simulate",
                "stderr": e.stderr,
                "stdout": e.stdout
            }

    def _run_mock_simulation(self, top_module: str, vcd_path: Path, max_sim_time: int) -> Dict[str, Any]:
        logger.info(f"Executing mock simulation run for module '{top_module}' (max_time={max_sim_time})...")
        
        vcd_content = """$date
   Mock Simulation Date
$end
$version
   AI RTL Platform Mock Engine 1.0
$end
$timescale
   1ns
$end
$scope module mock_scope $end
$var wire 1 # clk $end
$var wire 1 $ rst_n $end
$var wire 8 % count $end
$upscope $end
$enddefinitions $end
#0
0#
0$
b00000000 %
#10
1#
1$
#20
0#
#25
1#
b00000001 %
#30
0#
#40
1#
b00000010 %
#50
0#
"""
        try:
            with open(vcd_path, "w", encoding="utf-8") as f:
                f.write(vcd_content)
        except Exception as e:
            logger.error(f"Failed to write mock VCD file: {e}")
            
        mock_log = (
            f"[MOCK] Simulation log for module: {top_module}\n"
            f"[MOCK] Clock signal auto-detected on 'clk'\n"
            f"[MOCK] Reset signal 'rst_n' deasserted at tick 10\n"
            f"[MOCK] Simulation executed for {max_sim_time} steps successfully.\n"
        )
        return {
            "success": True,
            "stage": "completed_mock",
            "stdout": mock_log,
            "stderr": "",
            "vcd_path": str(vcd_path.resolve())
        }
