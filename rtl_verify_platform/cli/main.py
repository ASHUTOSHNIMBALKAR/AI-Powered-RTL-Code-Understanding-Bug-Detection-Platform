import sys
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rtl_verify_platform.core.logger import logger, setup_logger
from rtl_verify_platform.core.config import config_manager
from rtl_verify_platform.simulation.engine import SimulationEngine

app = typer.Typer(
    name="rtlverify",
    help="AI RTL Verification & Waveform Intelligence Platform CLI",
    no_args_is_help=True
)

console = Console(force_terminal=True)

IS_UTF8 = sys.stdout and sys.stdout.encoding and "utf-8" in sys.stdout.encoding.lower()
CHECK_MARK = "[OK]" if sys.platform == "win32" and not IS_UTF8 else "✓"
CROSS_MARK = "[FAIL]" if sys.platform == "win32" and not IS_UTF8 else "✗"

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Platform callback to configure verbosity."""
    if verbose:
        setup_logger(level=10)

@app.command()
def compile(
    rtl: List[Path] = typer.Argument(..., help="Path to RTL source file(s)"),
    top: str = typer.Option(..., "--top", "-t", help="Name of the top-level module"),
):
    """Compiles the RTL files using Verilator."""
    console.print(Panel(f"[bold blue]Compiling RTL Modules[/bold blue]\nTop Module: [cyan]{top}[/cyan]", expand=False))
    
    engine = SimulationEngine()
    res = engine.compile_and_simulate(rtl, top, max_sim_time=0)
    
    if res.get("success") or res.get("stage") == "simulate":
        console.print(f"[bold green]{CHECK_MARK} Compilation successful![/bold green]")
        if res.get("stdout"):
            console.print(Panel(res["stdout"], title="Compiler Stdout", border_style="green"))
    else:
        console.print(f"[bold red]{CROSS_MARK} Compilation failed![/bold red]")
        if res.get("stderr"):
            console.print(Panel(res["stderr"], title="Compiler Stderr", border_style="red"))
        elif res.get("error"):
            console.print(f"[bold red]Error:[/bold red] {res['error']}")
        sys.exit(1)

@app.command()
def simulate(
    rtl: List[Path] = typer.Argument(..., help="Path to RTL source file(s)"),
    top: str = typer.Option(..., "--top", "-t", help="Name of the top-level module"),
    custom_tb: Optional[Path] = typer.Option(None, "--tb", help="Path to custom C++ testbench"),
    max_time: int = typer.Option(1000, "--max-time", "-m", help="Maximum simulation time ticks"),
    mock: bool = typer.Option(False, "--mock", help="Force mock simulation engine"),
):
    """Simulates RTL design, captures logs, and generates a VCD waveform file."""
    console.print(Panel(f"[bold magenta]Running Simulation[/bold magenta]\nTop Module: [cyan]{top}[/cyan]", expand=False))
    
    engine = SimulationEngine()
    res = engine.compile_and_simulate(
        rtl_files=rtl,
        top_module=top,
        custom_tb_path=custom_tb,
        max_sim_time=max_time,
        use_mock=mock
    )
    
    if res.get("success"):
        console.print(f"[bold green]{CHECK_MARK} Simulation run completed successfully![/bold green]")
        
        table = Table(title="Simulation Details", border_style="magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Engine Mode", "Mock" if "mock" in res.get("stage", "") else "Verilator")
        table.add_row("VCD Output", res.get("vcd_path") or "None")
        
        console.print(table)
        
        if res.get("stdout"):
            console.print(Panel(res["stdout"], title="Simulation Log", border_style="magenta"))
    else:
        console.print(f"[bold red]{CROSS_MARK} Simulation failed![/bold red]")
        if res.get("stderr"):
            console.print(Panel(res["stderr"], title="Error Output", border_style="red"))
        elif res.get("error"):
            console.print(f"[bold red]Error:[/bold red] {res['error']}")
        sys.exit(1)

if __name__ == "__main__":
    app()
