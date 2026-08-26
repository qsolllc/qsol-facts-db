import time
import sys
import json
from facts_db.guard import TelemetryGuard, SecurityError

class TelemetryDaemon:
    def __init__(self, invariant: str, standard: str = "333"):
        self.guard = TelemetryGuard(required_invariant=standard)
        self.invariant = invariant

    def validate_line(self, line: str) -> str:
        line = line.strip()
        if not line:
            return None
        # Intercept and validate via guard
        return self.guard.intercept_and_validate(line, self.invariant)

    def watch_stream(self, stream, output_stream=sys.stdout):
        """Tails a stream line-by-line, enforcing invariant checks."""
        for line in stream:
            try:
                secured = self.validate_line(line)
                if secured:
                    output_stream.write(secured + "\n")
                    output_stream.flush()
            except (SecurityError, ValueError, json.JSONDecodeError) as e:
                sys.stderr.write(f"[BLOCKED] Invariant violation or malformed payload: {e}\n")
                sys.stderr.flush()
