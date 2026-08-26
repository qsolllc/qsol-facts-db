from facts_db.core import FactsDB

class PolicyEvaluator:
    def __init__(self):
        self.db = FactsDB()

    def optimize_policy(self, rule_expr: str) -> str:
        """
        Optimizes a rule expression using absorption and idempotence.
        """
        return self.db.normalize(rule_expr)

    def check_contradiction(self, rule_expr: str) -> bool:
        """
        Checks if a rule collapses into a logical contradiction (False / 0).
        """
        norm = self.db.normalize(rule_expr)
        return norm in ["False", "0", "~A & A", "A & ~A"]

    def compare_policies(self, policy_a: str, policy_b: str) -> bool:
        """
        Proves strict logical equivalence between two access rules.
        """
        return self.db.verify_equivalence(policy_a, policy_b)
