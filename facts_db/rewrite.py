from facts_db.core import FactsDB

class Minimizer(FactsDB):
    def consensus_minimize(self, expression: str) -> str:
        """
        Applies canonical normalization followed by full consensus theorem 
        reduction: (A & B) | (~A & C) | (B & C) -> (A & B) | (~A & C)
        """
        normalized = self.normalize(expression)
        
        if "|" in normalized:
            # Parse top-level disjunction into individual product terms
            terms = [t.strip().strip("()") for t in normalized.split("|")]
            reduced = self._apply_consensus_reduction(terms)
            if len(reduced) == 1:
                return reduced[0]
            return " | ".join(f"({t})" if "&" in t else t for t in reduced)
            
        return normalized

    def _apply_consensus_reduction(self, terms):
        unique_terms = list(dict.fromkeys(terms))
        parsed_terms = []
        
        for t in unique_terms:
            literals = set(l.strip() for l in t.split("&"))
            parsed_terms.append((t, literals))

        to_remove = set()
        
        # Check all pairs for consensus: X & Y and ~X & Z yields consensus Y & Z
        for i in range(len(parsed_terms)):
            for j in range(i + 1, len(parsed_terms)):
                t1_str, l1 = parsed_terms[i]
                t2_str, l2 = parsed_terms[j]
                
                # Find complementary literals (e.g., 'A' and '~A')
                for lit in l1:
                    neg_lit = "~" + lit if not lit.startswith("~") else lit[1:]
                    if neg_lit in l2:
                        # Found complement! Consensus term is (l1 - {lit}) union (l2 - {neg_lit})
                        consensus_lits = (l1 - {lit}) | (l2 - {neg_lit})
                        
                        # Look for a term matching the exact consensus set to eliminate it
                        for k, (t3_str, l3) in enumerate(parsed_terms):
                            if l3 == consensus_lits and t3_str not in (t1_str, t2_str):
                                to_remove.add(t3_str)

        final_terms = [t for t, _ in parsed_terms if t not in to_remove]
        return final_terms
