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
            with open(rtl_path, "r") as f:
                content = f.read()

            # Remove comments to avoid false matches
            content_no_comments = re.sub(r"//.*|/\*.*?\*/", "", content, flags=re.DOTALL)
            
            # Match input ports
            # Match: input [width] name
            input_pattern = re.compile(r"\binput\s+(?:wire\s+|reg\s+|logic\s+)?(?:\[[^\]]*\]\s*)?(\w+)\b", re.IGNORECASE)
            inputs = input_pattern.findall(content_no_comments)
            
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
        """Runs the entire compilation and simulation workflow.
        
        Returns:
            Dict containing build status, sim status, logs, and pathways to outputs.
        """
        rtl_paths = [Path(f) for f in rtl_files]
        vcd_name = config_manager.get("simulator.vcd_filename", "waveform.vcd")
        vcd_path = self.output_dir / vcd_name
        
        # Determine engine
        engine_mode = config_manager.get("simulator.default_engine", "verilator")
        
        # Check if verilator is available, else force mock
        if not use_mock and engine_mode == "verilator":
            if not shutil.which(self.verilator_path):
                logger.warning(f"Verilator not found in PATH. Falling back to MOCK mode.")
                use_mock = True

        if use_mock or engine_mode == "mock":
            return self._run_mock_simulation(top_module, vcd_path, max_sim_time)

        # Real Verilator simulation workflow
        logger.info(f"Starting Verilator simulation compile for {top_module}...")
        
        # 1. Testbench Setup
        tb_cpp_path = self.output_dir / f"tb_{top_module}.cpp"
        if custom_tb_path:
            shutil.copy(custom_tb_path, tb_cpp_path)
            logger.info(f"Using custom testbench: {custom_tb_path}")
        else:
            clocks, resets = self.detect_clk_rst(rtl_paths[0])
            if not clocks:
                clocks = ["clk"] # Default fallback
            if not resets:
                resets = [{"name": "rst_n", "active": "low"}]
            
            tb_content = generate_cpp_tb(
                top_module=top_module,
                vcd_filename=str(vcd_path.resolve()).replace("\\", "/"),
                clocks=clocks,
                resets=resets,
                max_sim_time=max_sim_time
            )
            with open(tb_cpp_path, "w") as f:
                f.write(tb_content)
            logger.info(f"Auto-generated C++ testbench wrapper at {tb_cpp_path}")

        # 2. Verilator Compilation
        # Command: verilator --cc <rtl> --exe <tb> --trace -Mdir <build_dir> --prefix V<top> -Wall
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

        logger.debug(f"Verilator command: {' '.join(cmd)}")
        
        try:
            compile_res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if compile_res.returncode != 0:
                logger.error("Verilator compilation failed!")
                return {
                    "success": False,
                    "stage": "compile",
                    "returncode": compile_res.returncode,
                    "stdout": compile_res.stdout,
                    "stderr": compile_res.stderr,
                    "vcd_path": None
                }
        except Exception as e:
            logger.error(f"Verilator execution error: {e}")
            return {
                "success": False,
                "stage": "compile_exec",
                "error": str(e),
                "vcd_path": None
            }

        # 3. Compile the generated C++ files to binary executable
        # Command: make -C <build_dir> -j -f V<top>.mk V<top>
        make_cmd = [
            "make",
            "-C",
            str(build_dir.resolve()),
            "-j",
            "-f",
            f"V{top_module}.mk",
            f"V{top_module}"
        ]
        
        logger.debug(f"Make command: {' '.join(make_cmd)}")
        try:
            make_res = subprocess.run(
                make_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if make_res.returncode != 0:
                logger.error("Make compilation of Verilator C++ sources failed!")
                return {
                    "success": False,
                    "stage": "make",
                    "returncode": make_res.returncode,
                    "stdout": make_res.stdout,
                    "stderr": make_res.stderr,
                    "vcd_path": None
                }
        except Exception as e:
            logger.error(f"Make execution error: {e}")
            return {
                "success": False,
                "stage": "make_exec",
                "error": str(e),
                "vcd_path": None
            }

        # 4. Execute the simulation binary
        sim_exe = build_dir / f"V{top_module}"
        logger.info(f"Running simulation binary {sim_exe}...")
        try:
            sim_res = subprocess.run(
                [str(sim_exe.resolve())],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if sim_res.returncode != 0:
                logger.error("Simulation run failed!")
                return {
                    "success": False,
                    "stage": "simulate",
                    "returncode": sim_res.returncode,
                    "stdout": sim_res.stdout,
                    "stderr": sim_res.stderr,
                    "vcd_path": None
                }
            
            logger.info("Simulation completed successfully.")
            return {
                "success": True,
                "stage": "completed",
                "stdout": sim_res.stdout,
                "stderr": sim_res.stderr,
                "vcd_path": str(vcd_path.resolve())
            }
        except Exception as e:
            logger.error(f"Simulation execution error: {e}")
            return {
                "success": False,
                "stage": "simulate_exec",
                "error": str(e),
                "vcd_path": None
            }

    def _run_mock_simulation(self, top_module: str, vcd_path: Path, max_sim_time: int) -> Dict[str, Any]:
        """Runs a mock simulation generating basic outputs and a valid synthetic VCD file."""
        logger.info(f"[MOCK MODE] Simulating {top_module}...")
        
        # Write dummy VCD waveform file
        vcd_content = f"""$date
   Tue Jun 30 12:00:00 2026
$end
$version
   AI RTL Platform Mock Sim
$end
$timescale
   1ns
$end
$scope module {top_module} $end
$var wire 1 # clk $end
$var wire 1 $ rst_n $end
$var wire 8 % count [7:0] $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0#
0$
b00000000 %
$end
#10
1$
#20
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
            with open(vcd_path, "w") as f:
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
