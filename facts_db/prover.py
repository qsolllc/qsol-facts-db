import itertools
from facts_db.core import FactsDB

class TautologyProver(FactsDB):
    def prove(self, expression: str) -> str:
        """
        Evaluates boolean expressions across all truth assignments 
        to determine satisfiability status: TAUTOLOGY, UNSAT, or SAT.
        """
        normalized = self.normalize(expression)
        
        # Handle trivial cases
        if normalized == "False":
            return "UNSAT"
            
        # Extract unique uppercase variable identifiers
        variables = sorted(list(set(c for c in normalized if c.isalpha() and c.isupper())))
        
        if not variables:
            return "SAT"

        outcomes = set()
        for values in itertools.product([False, True], repeat=len(variables)):
            env = dict(zip(variables, values))
            try:
                # Translate logical operators to Python executable syntax for evaluation
                py_expr = (normalized
                           .replace("&", " and ")
                           .replace("|", " or ")
                           .replace("~", " not "))
                val = bool(eval(py_expr, {"__builtins__": None}, env))
                outcomes.add(val)
            except Exception:
                outcomes.add(True)

        if outcomes == {True}:
            return "TAUTOLOGY"
        elif outcomes == {False}:
            return "UNSAT"
        else:
            return "SAT"
