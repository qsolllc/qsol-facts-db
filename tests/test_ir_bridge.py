import json
from facts_db.core import FactsDB

def test_ir_json_determinism():
    db = FactsDB()
    expr = "(A & B) | ~C"
    ir_ast = db.to_ast(expr)
    
    # Verify that the AST dictionary is fully serializable and stable
    serialized_ir = json.dumps(ir_ast)
    deserialized = json.loads(serialized_ir)
    
    assert deserialized == ir_ast
