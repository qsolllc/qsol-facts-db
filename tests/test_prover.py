from facts_db.prover import TautologyProver

def test_prover_tautology():
    p = TautologyProver()
    assert p.prove("X | ~X") == "TAUTOLOGY"

def test_prover_unsat():
    p = TautologyProver()
    assert p.prove("X & ~X") == "UNSAT"

def test_prover_sat():
    p = TautologyProver()
    assert p.prove("A & B") == "SAT"
