import io
from facts_db.daemon import TelemetryDaemon

def test_daemon_stream_filtering():
    input_data = '{"state": "ACTIVE"}\n{"state": "DOWN"}\n'
    stream = io.StringIO(input_data)
    output = io.StringIO()
    
    daemon = TelemetryDaemon(invariant="state == ACTIVE", standard="333")
    daemon.watch_stream(stream, output_stream=output)
    
    results = output.getvalue().strip().split("\n")
    # Only the ACTIVE log should pass through the guard
    assert len(results) == 1
    assert "ACTIVE" in results[0]
