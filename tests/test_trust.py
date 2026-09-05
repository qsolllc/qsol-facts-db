from zk_audit.trust_matrix import TrustMatrix

def test_trust_matrix_quorum_success():
    matrix = TrustMatrix(trustees=["Jeramy", "Keri", "Lorrie"], threshold=2)
    state_hash = "09fc861_state_root"
    
    # Generate valid signatures for Jeramy and Keri
    approvals = {
        "Jeramy": matrix._sign_share("Jeramy", state_hash),
        "Keri": matrix._sign_share("Keri", state_hash)
    }
    
    assert matrix.authorize_recovery(state_hash, approvals) is True

def test_trust_matrix_quorum_failure():
    matrix = TrustMatrix(trustees=["Jeramy", "Keri", "Lorrie"], threshold=2)
    state_hash = "09fc861_state_root"
    
    # Only one valid approval provided (below threshold of 2)
    approvals = {
        "Jeramy": matrix._sign_share("Jeramy", state_hash)
    }
    
    assert matrix.authorize_recovery(state_hash, approvals) is False
