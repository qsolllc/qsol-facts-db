from zk_audit.merkle import MerkleTree

def test_merkle_tree_inclusion():
    leaves = ["event_alpha", "event_beta", "event_gamma", "event_delta"]
    tree = MerkleTree(leaves)
    
    assert tree.root != ""
    
    # Test proof generation and verification for index 2 ("event_gamma")
    proof = tree.generate_proof(2)
    assert len(proof) > 0
    
    is_valid = tree.verify_proof("event_gamma", proof, tree.root)
    assert is_valid is True

def test_merkle_tree_invalid_proof():
    leaves = ["node_one", "node_two"]
    tree = MerkleTree(leaves)
    proof = tree.generate_proof(0)
    
    # Tampering with leaf data should fail verification
    is_valid = tree.verify_proof("tampered_node", proof, tree.root)
    assert is_valid is False
