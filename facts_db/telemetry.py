import json
from facts_db.core import FactsDB

class TelemetryVerifier:
    def __init__(self, standard_invariant: str = "333"):
        self.db = FactsDB()
        self.standard = standard_invariant

    def verify_payload(self, payload_json: str, invariant_expr: str) -> dict:
        """
        Validates a JSON telemetry payload against structural safety bounds 
        and runtime invariant truth evaluation.
        """
        try:
            payload = json.loads(payload_json)
            payload_str = json.dumps(payload, sort_keys=True)
            
            if len(payload_str) > self.db.max_len:
                return {"status": "REJECTED", "reason": "Payload exceeds max length boundary"}

            # Normalize invariant expression via AST
            ast = self.db.to_ast(invariant_expr)
            normalized_ast = self.db._normalize_ast(ast)
            
            # Evaluate AST against payload context
            if not self._evaluate_ast(normalized_ast, payload):
                return {"status": "REJECTED", "reason": "Payload violates invariant assertion"}

            normalized_inv = self.db.ast_to_string(normalized_ast)
            
            return {
                "status": "APPROVED",
                "standard": self.standard,
                "invariant": normalized_inv,
                "payload_keys": list(payload.keys())
            }
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)}

    def _evaluate_ast(self, ast: dict, payload: dict) -> bool:
        """Recursively evaluates an AST node against payload key-values."""
        if "literal" in ast:
            lit = ast["literal"]
            # Handle equality checks or raw boolean truth keys
            if "==" in lit:
                parts = [p.strip() for p in lit.split("==")]
                if len(parts) == 2:
                    key, val = parts
                    return str(payload.get(key)) == val
            return bool(payload.get(lit, True))
            
        op = ast.get("op")
        args = ast.get("args", [])
        
        if op == "AND":
            return all(self._evaluate_ast(arg, payload) for arg in args)
        elif op == "OR":
            return any(self._evaluate_ast(arg, payload) for arg in args)
        elif op == "NOT":
            return not self._evaluate_ast(ast.get("arg"), payload)
            
        return True
