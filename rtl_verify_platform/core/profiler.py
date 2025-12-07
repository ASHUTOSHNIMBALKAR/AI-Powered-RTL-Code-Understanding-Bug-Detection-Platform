import time
from contextlib import contextmanager
from rtl_verify_platform.core.logger import logger

class Profiler:
    """Execution profiler for measuring build and simulation phases."""
    
    def __init__(self):
        self.timings = {}

    @contextmanager
    def track(self, phase_name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.timings[phase_name] = elapsed
            logger.debug(f"[PROFILER] Phase '{phase_name}' completed in {elapsed:.4f}s")

profiler = Profiler()
