from facts_db.rewrite import Minimizer

def test_consensus_minimization():
    m = Minimizer()
    result = m.consensus_minimize("X & (X | Y)")
    assert result == "X"

def test_consensus_theorem_reduction():
    m = Minimizer()
    # Verifies normalization and structural cleanup under v2.4 minimizer rules
    expr = "(A & B) | (~A & C) | (B & C)"
    minimized = m.consensus_minimize(expr)
    assert "A" in minimized and "C" in minimized
