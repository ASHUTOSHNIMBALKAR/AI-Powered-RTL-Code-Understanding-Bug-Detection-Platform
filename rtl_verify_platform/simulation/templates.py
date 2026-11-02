import re
from typing import List, Dict

VERILATOR_TB_TEMPLATE = """#include <iostream>
#include <memory>
#include "verilated.h"
#include "V{top_module}.h"

#if VM_TRACE
#include "verilated_vcd_c.h"
#endif

// Current simulation time
vluint64_t main_time = 0;

double sc_time_stamp() {{
    return main_time;
}}

int main(int argc, char** argv) {{
    // Prevent unused variable warning
    if (false && argc && argv) {{}}

    Verilated::commandArgs(argc, argv);

    // Instantiate design
    std::unique_ptr<V{top_module}> top(new V{top_module});

#if VM_TRACE
    Verilated::traceEverOn(true);
    std::unique_ptr<VerilatedVcdC> tfp(new VerilatedVcdC);
    top->trace(tfp.get(), 99);
    tfp->open("{vcd_filename}");
#endif

    // Initial state
    {initial_statements}

    // Run simulation for maximum cycles
    const uint64_t max_sim_time = {max_sim_time};

    while (main_time < max_sim_time && !Verilated::gotFinish()) {{
        // Toggle clock(s)
        {clock_logic}

        // Apply reset logic
        {reset_logic}

        // Eval design
        top->eval();

#if VM_TRACE
        tfp->dump(main_time);
#endif
        main_time++;
    }}

    // Finalize
    top->final();

#if VM_TRACE
    tfp->close();
#endif

    std::cout << "Simulation finished at " << main_time << " ticks." << std::endl;
    return 0;
}}
"""

def generate_cpp_tb(
    top_module: str,
    vcd_filename: str,
    clocks: List[str],
    resets: List[Dict[str, str]], # list of {"name": str, "active": "high"|"low", "duration": int}
    max_sim_time: int = 1000
) -> str:
    """Generates a custom C++ testbench wrapper for Verilator based on RTL ports."""
    
    initial_statements = []
    clock_logic = []
    reset_logic = []

    # Handle clocks
    for clk in clocks:
        # Initialise clock to 0
        initial_statements.append(f"top->{clk} = 0;")
        # Toggle clock every 5 ticks
        clock_logic.append(
            f"if ((main_time % 10) == 0) {{\n"
            f"            top->{clk} = !top->{clk};\n"
            f"        }}"
        )

    # Handle resets
    for rst in resets:
        name = rst["name"]
        active = rst["active"]
        duration = rst.get("duration", 40)
        
        active_val = "1" if active == "high" else "0"
        inactive_val = "0" if active == "high" else "1"
        
        initial_statements.append(f"top->{name} = {active_val};")
        reset_logic.append(
            f"if (main_time >= {duration}) {{\n"
            f"            top->{name} = {inactive_val};\n"
            f"        }} else {{\n"
            f"            top->{name} = {active_val};\n"
            f"        }}"
        )

    # If no clocks or resets specified, just let it run
    initial_str = "\n    ".join(initial_statements)
    clk_str = "\n        ".join(clock_logic) if clock_logic else "// No clock signals specified"
    rst_str = "\n        ".join(reset_logic) if reset_logic else "// No reset signals specified"

    return VERILATOR_TB_TEMPLATE.format(
        top_module=top_module,
        vcd_filename=vcd_filename,
        initial_statements=initial_str,
        max_sim_time=max_sim_time,
        clock_logic=clk_str,
        reset_logic=rst_str
    )
