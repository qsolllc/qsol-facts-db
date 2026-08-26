import os

def test_tla_specification_existence():
    tla_path = "zk_audit/specs/DaemonState.tla"
    cfg_path = "zk_audit/specs/DaemonState.cfg"
    
    assert os.path.exists(tla_path), "DaemonState.tla specification must exist."
    assert os.path.exists(cfg_path), "DaemonState.cfg configuration must exist."
    
    with open(tla_path, "r") as f:
        content = f.read()
    assert "MODULE DaemonState" in content
    assert "NoDeadlock" in content
