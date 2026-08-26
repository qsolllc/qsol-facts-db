import pytest
from facts_db.core import FactsDB

def test_absorption_and_idempotence():
    db = FactsDB()
    assert db.normalize("X & (X | Y)") == "X"
    assert db.normalize("X & X") == "X"

def test_commutativity_and_associativity():
    db = FactsDB()
    assert db.verify_equivalence("b & a", "a & b")
    assert db.verify_equivalence("(y | x) | z", "x | (y | z)")
    assert not db.verify_equivalence("a & b", "a | b")

def test_expansions():
    db = FactsDB()
    assert db.expand_distributivity("A & (B | C)") == "((A & B) | (A & C))"
    assert db.demorgan("~(A & B)") == "(~A | ~B)"

def test_json_ir_roundtrip():
    db = FactsDB()
    expr = "(a & b) | c"
    ast = db.to_ast(expr)
    reconstructed_str = db.ast_to_string(ast)
    assert db.verify_equivalence(expr, reconstructed_str)

def test_depth_guardrail():
    db = FactsDB()
    deep_expr = "(((((((((((a)))))))))))"
    with pytest.raises(ValueError, match="Maximum depth"):
        db._split_top(deep_expr, ["&"])
