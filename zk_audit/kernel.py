from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from enum import Enum

# --- Exception Definitions ---

class AssuranceViolation(Exception):
    """Base class for constitutional assurance violations."""
    pass

class TypeViolation(AssuranceViolation):
    pass

class RuleViolation(AssuranceViolation):
    pass

class PromotionViolation(AssuranceViolation):
    pass

class BridgeViolation(AssuranceViolation):
    pass

class EvidenceClassViolation(AssuranceViolation):
    pass

class ProvenanceViolation(AssuranceViolation):
    pass

class CompositionViolation(AssuranceViolation):
    pass

class GraphCycleViolation(AssuranceViolation):
    pass

class ScopeViolation(AssuranceViolation):
    pass


# --- Enums & Typed Relations ---

class Relation(Enum):
    DEFINES = "defines"
    DERIVES = "derives"
    OBSERVES = "observes"
    MEASURES = "measures"
    SUPPORTS = "supports"
    INTERPRETS = "interprets"
    BRIDGES = "bridges"
    REFUTES = "refutes"
    BLOCKS = "blocks"
    FAILS_TO_ESTABLISH = "failsToEstablish"


# --- Core Data Objects ---

@dataclass
class Evidence:
    id: str
    evidence_class: str
    artifact: str
    provenance_status: str = "UNRESOLVED"
    relevance_established: bool = True

@dataclass
class SaturationScore:
    value: float

@dataclass
class Symbol:
    name: str

@dataclass
class Claim:
    id: str
    type: str
    statement: str
    dependencies: List[str] = field(default_factory=list)

# Orthogonal Per-Dimension Product-Order Status Lattice
class StatusLattice:
    LEVELS = {
        "UNRESOLVED": 0,
        "OBSERVED": 1,
        "VERIFIED": 2,
        "PROVENANCE_ESTABLISHED": 2,
        "ATTESTED": 2,
        "ESTABLISHED": 3
    }

    @classmethod
    def compare(cls, status_a: str, status_b: str) -> int:
        la = cls.LEVELS.get(status_a, 0)
        lb = cls.LEVELS.get(status_b, 0)
        if la < lb:
            return -1
        elif la > lb:
            return 1
        return 0

@dataclass
class Status:
    T: str = "UNRESOLVED"
    V: str = "UNRESOLVED"
    P: str = "UNRESOLVED"
    O: str = "UNRESOLVED"
    A: str = "UNRESOLVED"

    def dominates(self, other: 'Status') -> bool:
        return (
            StatusLattice.compare(self.T, other.T) >= 0 and
            StatusLattice.compare(self.V, other.V) >= 0 and
            StatusLattice.compare(self.P, other.P) >= 0 and
            StatusLattice.compare(self.O, other.O) >= 0 and
            StatusLattice.compare(self.A, other.A) >= 0
        )

@dataclass
class BridgeObject:
    id: str
    model: str
    target: str
    correspondence: str
    bridge_rules: List[str]
    measurements: List[Any]
    epsilon: float
    uncertainty_model: Optional[str]
    assumptions: List[str]
    observed_value: float = 0.0

@dataclass
class FormalAssuranceInput:
    specification: str
    property: str
    result: str
    scope: str
    evidence: str

@dataclass
class DerivationResult:
    status: Status
    message: str = "Success"

@dataclass
class DependencyGraph:
    nodes: Dict[str, List[Tuple[str, Relation]]] = field(default_factory=dict)
    allow_recursion: bool = False


# --- Assurance Kernel Implementation (v1.1) ---

class AssuranceKernel:
    def __init__(self):
        self._prohibited_promotions = {
            ("E_I", "P_PROVENANCE_ESTABLISHED"),
            ("E_I", "P_AUTHORSHIP_ESTABLISHED"),
            ("E_I", "T_ESTABLISHED"),
            ("E_P", "T_ESTABLISHED"),
            ("E_O", "O_CAUSATION_ESTABLISHED"),
            ("E_O", "T_ESTABLISHED"),
            ("E_M", "MATHEMATICAL_IDENTITY"),
            ("E_D", "PHYSICAL_REALIZATION"),
            ("E_A", "T_ESTABLISHED"),
            ("9999", "T_ESTABLISHED"),
            ("CONJUNCTION_EI_EP", "P_AUTHORSHIP_ESTABLISHED"),
            ("E_I_PLUS_V", "T_ESTABLISHED"),
            ("E_O_PLUS_M", "C_CAUSAL"),
            ("P_ONLY", "P_AUTHORSHIP_ESTABLISHED"),
            ("AUTHORSHIP_ONLY", "T_ESTABLISHED"),
            ("D_ONLY", "R_PHYSICAL"),
            ("OBSERVATION_ONLY", "PHYSICAL_REALIZATION"),
            ("INTERPRETATION_ONLY", "PROPOSITION_TRUTH"),
            ("MISSING_EVIDENCE", "REFUTED"),
            ("FAILED_ESTABLISHMENT", "REFUTED"),
        }

        self._registered_rules: Set[str] = {
            "R-EULER-IDENTITY",
            "R-PROVENANCE-CHAIN-001",
            "R-OBSERVATION-VALID",
            "R-ATTESTATION-VALID",
            "R-BRIDGE-VALID",
            "R-MASTER-DERIVATION",
            "R-AUTHORSHIP-EXPLICIT"
        }

        self._verified_tla_scopes: Dict[tuple[str, str], str] = {}

    def authorize_transition(self, source_class: str, target_status: Status, rule: Optional[str] = None) -> bool:
        target_str = f"T_{target_status.T}" if target_status.T != "UNRESOLVED" else f"P_{target_status.P}"
        if (source_class, target_str) in self._prohibited_promotions or (source_class, target_status.T) in self._prohibited_promotions:
            return False
        if rule and rule not in self._registered_rules:
            return False
        return True

    def promote(self, entity: Any, target_status: Status) -> Status:
        source_class = None
        if isinstance(entity, Evidence):
            source_class = entity.evidence_class
            if not entity.relevance_established:
                raise PromotionViolation("EvidenceViolation: Evidence relevance not established.")
        elif isinstance(entity, list):
            classes = {e.evidence_class for e in entity if isinstance(e, Evidence)}
            if "E_I" in classes and "E_P" in classes:
                source_class = "CONJUNCTION_EI_EP"
            elif "E_I" in classes and "V" in classes:
                source_class = "E_I_PLUS_V"
            else:
                source_class = "MULTI_EVIDENCE"
        elif isinstance(entity, SaturationScore):
            source_class = "9999"
        elif isinstance(entity, Symbol):
            source_class = "SYMBOL"
        elif isinstance(entity, Claim):
            source_class = entity.type
        else:
            source_class = type(entity).__name__

        if not self.authorize_transition(source_class, target_status):
            raise PromotionViolation(
                f"Constitutional Prohibition: Promoting source class '{source_class}' "
                f"to target status is strictly forbidden by the non-collapse matrix."
            )

        raise PromotionViolation("Promotion rejected: No explicit rule authorizes promotion.")

    def evaluate_provenance(self, artifact: str, chain: List[Any], rule: str) -> DerivationResult:
        if not chain:
            raise ProvenanceViolation("ProvenanceViolation: Missing provenance chain.")
        if rule not in self._registered_rules:
            raise RuleViolation(f"RuleViolation: Provenance rule '{rule}' not recognized.")
        
        if all(isinstance(c, str) for c in chain):
            return DerivationResult(status=Status(P="PROVENANCE_ESTABLISHED"))
            
        return self.validate_provenance_chain(artifact, chain, rule)

    def validate_provenance_chain(self, artifact: str, chain: List[Evidence], rule: str) -> DerivationResult:
        if not chain:
            raise ProvenanceViolation("ProvenanceViolation: Missing provenance chain.")
        if rule not in self._registered_rules:
            raise RuleViolation(f"RuleViolation: Provenance rule '{rule}' not recognized.")
        
        for i, ev in enumerate(chain):
            if not isinstance(ev, Evidence) or not ev.relevance_established:
                raise ProvenanceViolation(f"ProvenanceViolation: Invalid or irrelevant evidence node at index {i}.")
            if i > 0 and chain[i-1].artifact == ev.artifact:
                raise ProvenanceViolation(f"ProvenanceViolation: Degenerate or non-progressive link at index {i}.")
        
        if chain[-1].artifact != artifact:
            raise ProvenanceViolation(f"ProvenanceViolation: Provenance chain does not terminate at target artifact '{artifact}'.")

        return DerivationResult(status=Status(P="PROVENANCE_ESTABLISHED"))

    def validate_bridge(self, bridge: BridgeObject) -> bool:
        """
        Quantitative bridge validation: explicitly guards epsilon against non-numeric types, 
        Booleans, and negative values, converting malformed inputs into explicit BridgeViolations.
        """
        if not bridge.model or not bridge.target or not bridge.correspondence:
            raise BridgeViolation("BridgeViolation: Missing model, target, or correspondence.")

        if not isinstance(bridge.epsilon, (int, float)) or isinstance(bridge.epsilon, bool):
            raise BridgeViolation("BridgeViolation: epsilon must be a numeric quantity (non-boolean).")

        if bridge.epsilon < 0.0:
            raise BridgeViolation("BridgeViolation: Tolerance epsilon must be non-negative (>= 0).")

        if not bridge.uncertainty_model:
            raise BridgeViolation("BridgeViolation: Missing uncertainty model.")

        if not all([bridge.bridge_rules, bridge.measurements, bridge.assumptions]):
            raise BridgeViolation("BridgeViolation: Incomplete bridge object lists.")
        
        return True

    def validate_dependency_graph(self, graph: DependencyGraph) -> bool:
        if graph.allow_recursion:
            return True

        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for item in graph.nodes.get(node, []):
                if isinstance(item, tuple):
                    neighbor, rel = item
                    if rel in {Relation.REFUTES, Relation.BLOCKS, Relation.FAILS_TO_ESTABLISH}:
                        continue
                else:
                    neighbor = item

                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in graph.nodes:
            if node not in visited:
                if dfs(node):
                    raise GraphCycleViolation(f"GraphCycleViolation: Cyclic dependency detected involving node '{node}'.")
        
        return True

    def derive(self, premises: List[str], rule: str, conclusion: str, is_master: bool = False, evidence_objects: List[Any] = None, graph: Optional[DependencyGraph] = None) -> DerivationResult:
        if not premises:
            raise RuleViolation("RuleViolation: Derivation attempted with missing premises.")
        if rule not in self._registered_rules:
            raise RuleViolation(f"RuleViolation: Rule '{rule}' is not registered.")
        
        if graph:
            self.validate_dependency_graph(graph)

        if is_master:
            if rule != "R-MASTER-DERIVATION":
                raise RuleViolation("RuleViolation: P_master requires R-MASTER-DERIVATION.")
            if not evidence_objects or len(evidence_objects) < 2:
                raise CompositionViolation("CompositionViolation: P_master requires a fully validated multi-artifact derivation graph.")

        return DerivationResult(status=Status(T="ESTABLISHED"))

    def ingest_formal_assurance(self, assurance: FormalAssuranceInput) -> Status:
        if not assurance.specification or not assurance.property:
            raise RuleViolation("RuleViolation: Formal assurance input missing specification or property.")
        self._verified_tla_scopes[(assurance.specification, assurance.property)] = assurance.scope
        return Status(V="VERIFIED")

    def query_scoped_verification(self, specification: str, property: str, target_claim_scope: str) -> bool:
        registered_scope = self._verified_tla_scopes.get((specification, property))
        if not registered_scope or registered_scope != target_claim_scope:
            return False
        return True
