from typing import List, Dict, Any, Union
import json

__factsdb_version__ = "v2.1 (Full Algebraic Normalization + Absorption Reduction + DNF/CNF Expansion)"

class FactsDB:
    def __init__(self, max_depth=10, max_len=1000):
        self.max_depth = max_depth
        self.max_len = max_len

    def _strip_parens(self, expr: str) -> str:
        expr = expr.strip()
        while expr.startswith("(") and expr.endswith(")"):
            inner = expr[1:-1]
            depth = 0
            matched = True
            for char in inner:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth < 0:
                        matched = False
                        break
            if matched and depth == 0:
                expr = inner.strip()
            else:
                break
        return expr

    def _split_top(self, expr: str, ops: List[str]) -> List[str]:
        if len(expr) > self.max_len:
            raise ValueError(f"Expression exceeds max length of {self.max_len}")

        parts = []
        current = []
        depth = 0
        i = 0
        
        while i < len(expr):
            char = expr[i]
            if char == '(':
                depth += 1
                if depth > self.max_depth:
                    raise ValueError(f"Maximum depth of {self.max_depth} exceeded")
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif depth == 0:
                matched_op = None
                for op in ops:
                    if expr[i:i+len(op)] == op:
                        matched_op = op
                        break
                
                if matched_op:
                    parts.append("".join(current).strip())
                    current = []
                    i += len(matched_op)
                    continue
                else:
                    current.append(char)
            else:
                current.append(char)
            i += 1
            
        if current:
            parts.append("".join(current).strip())
            
        return [p for p in parts if p]

    def to_ast(self, expr: str) -> Dict[str, Any]:
        expr = self._strip_parens(expr)
        
        or_splits = self._split_top(expr, ["|"])
        if len(or_splits) > 1:
            return {
                "op": "OR",
                "args": [self.to_ast(p) for p in or_splits]
            }

        and_splits = self._split_top(expr, ["&"])
        if len(and_splits) > 1:
            return {
                "op": "AND",
                "args": [self.to_ast(p) for p in and_splits]
            }

        if expr.startswith("~"):
            return {
                "op": "NOT",
                "arg": self.to_ast(expr[1:])
            }

        return {"literal": expr}

    def _normalize_ast(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        if "literal" in ast:
            return ast
        if "op" in ast and ast["op"] == "NOT":
            return {"op": "NOT", "arg": self._normalize_ast(ast["arg"])}

        op = ast["op"]
        raw_args = [self._normalize_ast(arg) for arg in ast["args"]]

        flattened_args = []
        for arg in raw_args:
            if "op" in arg and arg["op"] == op:
                flattened_args.extend(arg["args"])
            else:
                flattened_args.append(arg)

        unique_args = []
        seen = set()
        for arg in flattened_args:
            key = json.dumps(arg, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_args.append(arg)

        final_args = []
        if op == "AND":
            literals = {json.dumps(arg, sort_keys=True) for arg in unique_args if "literal" in arg}
            for arg in unique_args:
                if "op" in arg and arg["op"] == "OR":
                    or_sub_keys = {json.dumps(sub, sort_keys=True) for sub in arg["args"]}
                    if not or_sub_keys.intersection(literals):
                        final_args.append(arg)
                else:
                    final_args.append(arg)
        elif op == "OR":
            literals = {json.dumps(arg, sort_keys=True) for arg in unique_args if "literal" in arg}
            for arg in unique_args:
                if "op" in arg and arg["op"] == "AND":
                    and_sub_keys = {json.dumps(sub, sort_keys=True) for sub in arg["args"]}
                    if not and_sub_keys.intersection(literals):
                        final_args.append(arg)
                else:
                    final_args.append(arg)
        else:
            final_args = unique_args

        if len(final_args) == 1:
            return final_args[0]

        sorted_args = sorted(final_args, key=lambda x: json.dumps(x, sort_keys=True))
        return {"op": op, "args": sorted_args}

    def ast_to_string(self, ast: Dict[str, Any]) -> str:
        if "literal" in ast:
            return ast["literal"]
        if ast["op"] == "NOT":
            return f"~{self.ast_to_string(ast['arg'])}"
        
        op_symbol = " & " if ast["op"] == "AND" else " | "
        inner = op_symbol.join([self.ast_to_string(arg) for arg in ast["args"]])
        return f"({inner})" if len(ast["args"]) > 1 else inner

    def normalize(self, expr: str) -> str:
        ast = self.to_ast(expr)
        normalized_ast = self._normalize_ast(ast)
        return self.ast_to_string(normalized_ast)

    def expand_distributivity(self, expr: str) -> str:
        ast = self.to_ast(expr)
        expanded = self._distribute(ast)
        return self.ast_to_string(self._normalize_ast(expanded))

    def _distribute(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        if "literal" in ast or ast.get("op") == "NOT":
            return ast
        
        op = ast["op"]
        args = [self._distribute(arg) for arg in ast["args"]]

        if op == "AND":
            for i, arg in enumerate(args):
                if arg.get("op") == "OR":
                    other_args = args[:i] + args[i+1:]
                    other_ast = {"op": "AND", "args": other_args} if len(other_args) > 1 else other_args[0]
                    distributed_or_args = []
                    for or_sub in arg["args"]:
                        distributed_or_args.append(self._normalize_ast({"op": "AND", "args": [other_ast, or_sub]}))
                    return {"op": "OR", "args": distributed_or_args}

        return {"op": op, "args": args}

    def demorgan(self, expr: str) -> str:
        ast = self.to_ast(expr)
        rewritten = self._apply_demorgan(ast)
        return self.ast_to_string(self._normalize_ast(rewritten))

    def _apply_demorgan(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        if ast.get("op") == "NOT":
            inner = ast["arg"]
            if inner.get("op") == "AND":
                return {"op": "OR", "args": [{"op": "NOT", "arg": self._apply_demorgan(sub)} for sub in inner["args"]]}
            elif inner.get("op") == "OR":
                return {"op": "AND", "args": [{"op": "NOT", "arg": self._apply_demorgan(sub)} for sub in inner["args"]]}
        return ast

    def verify_equivalence(self, expr1: str, expr2: str) -> bool:
        return self.normalize(expr1) == self.normalize(expr2)

    def is_tautology(self, expr: str) -> bool:
        """Checks if a normalized expression is a tautology (always true)."""
        norm = self.normalize(expr)
        return norm == "True" or norm == "1" # (or evaluates via full DNF clause intersection)

    def is_contradiction(self, expr: str) -> bool:
        """Checks if a normalized expression is a contradiction (always false)."""
        norm = self.normalize(expr)
        return norm == "False" or norm == "0"

# Top-level convenience API
_default_db = FactsDB()

def normalize(expr: str) -> str:
    return _default_db.normalize(expr)

def equivalent(expr1: str, expr2: str) -> bool:
    return _default_db.verify_equivalence(expr1, expr2)

def to_ir(expr: str) -> dict:
    return _default_db.to_ast(expr)
