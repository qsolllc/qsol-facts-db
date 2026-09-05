import pytest
from zk_audit.kernel import (
    AssuranceKernel,
    Evidence,
    SaturationScore,
    Symbol,
    Claim,
    BridgeObject,
    FormalAssuranceInput,
    Status,
    PromotionViolation,
    BridgeViolation,
    RuleViolation,
    ProvenanceViolation,
    CompositionViolation,
    DependencyGraph,
    GraphCycleViolation
)

kernel = AssuranceKernel()

# NK-001 through NK-010: Non-collapse axioms
def test_hash_does_not_promote_to_provenance():
    evidence = Evidence(id="E-I-001", evidence_class="E_I", artifact="QSOL_VAULT_RECURSIVE_SHA256.txt")
    with pytest.raises(PromotionViolation):
        kernel.promote(evidence, target_status=Status(P="PROVENANCE_ESTABLISHED"))

def test_hash_does_not_promote_to_authorship():
    evidence = Evidence(id="E-I-001", evidence_class="E_I", artifact="QSOL_VAULT_RECURSIVE_SHA256.txt")
    with pytest.raises(PromotionViolation):
        kernel.promote(evidence, target_status=Status(P="AUTHORSHIP_ESTABLISHED"))

def test_integrity_does_not_establish_truth():
    evidence = Evidence(id="E-I-001", evidence_class="E_I", artifact="QSOL_VAULT_RECURSIVE_SHA256.txt")
    with pytest.raises(PromotionViolation):
        kernel.promote(evidence, target_status=Status(T="ESTABLISHED"))

def test_metric_does_not_establish_truth():
    metric = SaturationScore(value=0.99999)
    with pytest.raises(PromotionViolation):
        kernel.promote(metric, target_status=Status(T="ESTABLISHED"))

def test_symbol_does_not_become_empirical_fact():
    symbol = Symbol(name="phi")
    with pytest.raises(PromotionViolation):
        kernel.promote(symbol, target_status=Status(O="OBSERVED"))

# NK-011 & NK-012: Derivation controls
def test_missing_premise_rejection():
    with pytest.raises(RuleViolation):
        kernel.derive(premises=[], rule="R-EULER-IDENTITY", conclusion="C-001")

def test_undeclared_rule_rejection():
    with pytest.raises(RuleViolation):
        kernel.derive(premises=["A-001"], rule="R-UNKNOWN-RULE", conclusion="C-001")

# NK-013, NK-014, NK-015: Bridge controls (with correct numeric epsilon checks)
def test_non_numeric_epsilon_rejection():
    invalid_bridge = BridgeObject(
        id="B-001", model="M-001", target="X-001", correspondence="Gamma-001",
        bridge_rules=["RB-001"], measurements=["M-001"], epsilon="EPS-001",
        uncertainty_model="U-001", assumptions=["A-001"]
    )
    with pytest.raises(BridgeViolation):
        kernel.validate_bridge(invalid_bridge)

def test_boolean_epsilon_rejection():
    invalid_bridge = BridgeObject(
        id="B-001", model="M-001", target="X-001", correspondence="Gamma-001",
        bridge_rules=["RB-001"], measurements=["M-001"], epsilon=True,
        uncertainty_model="U-001", assumptions=["A-001"]
    )
    with pytest.raises(BridgeViolation):
        kernel.validate_bridge(invalid_bridge)

def test_negative_epsilon_rejection():
    invalid_bridge = BridgeObject(
        id="B-001", model="M-001", target="X-001", correspondence="Gamma-001",
        bridge_rules=["RB-001"], measurements=["M-001"], epsilon=-0.001,
        uncertainty_model="U-001", assumptions=["A-001"]
    )
    with pytest.raises(BridgeViolation):
        kernel.validate_bridge(invalid_bridge)

def test_missing_uncertainty_model_adjudication_rejection():
    invalid_bridge = BridgeObject(
        id="B-001", model="M-001", target="X-001", correspondence="Gamma-001",
        bridge_rules=["RB-001"], measurements=["M-001"], epsilon=0.001, uncertainty_model="", assumptions=["A-001"]
    )
    with pytest.raises(BridgeViolation):
        kernel.validate_bridge(invalid_bridge)

# NK-016: Evidence / Provenance controls
def test_missing_provenance_chain_rejection():
    with pytest.raises(ProvenanceViolation):
        kernel.evaluate_provenance(artifact="art-001", chain=[], rule="R-PROVENANCE-CHAIN-001")

# NK-023: Incomplete P_master rejection
def test_incomplete_p_master_rejection():
    with pytest.raises(RuleViolation):
        kernel.derive(premises=["A-001"], rule="R-EULER-IDENTITY", conclusion="P_master", is_master=True)

# NK-025 & NK-026: Evidence relevance & contradictory evidence
def test_irrelevant_evidence_rejection():
    evidence = Evidence(id="E-I-002", evidence_class="E_I", artifact="vault.txt", relevance_established=False)
    with pytest.raises(PromotionViolation):
        kernel.promote(evidence, target_status=Status(T="ESTABLISHED"))

# NK-027 through NK-035 (Compositional Attack Matrix)
def test_nk_027_composite_evidence_does_not_imply_truth():
    e_i = Evidence(id="E1", evidence_class="E_I", artifact="hash.txt")
    e_p = Evidence(id="E2", evidence_class="E_P", artifact="provenance.log")
    with pytest.raises(PromotionViolation):
        kernel.promote(e_i, target_status=Status(T="ESTABLISHED"))
    with pytest.raises(PromotionViolation):
        kernel.promote(e_p, target_status=Status(T="ESTABLISHED"))

def test_nk_028_tla_scope_isolation():
    assurance = FormalAssuranceInput(
        specification="DaemonState.tla",
        property="SafetyInvariant",
        result="ESTABLISHED",
        scope="ModelA",
        evidence="tla_out.log"
    )
    kernel.ingest_formal_assurance(assurance)
    assert kernel.query_scoped_verification("DaemonState.tla", "SafetyInvariant", "ModelA") is True
    assert kernel.query_scoped_verification("DaemonState.tla", "SafetyInvariant", "ModelB-Unauthorized") is False

def test_nk_029_provenance_plus_integrity_does_not_equal_authorship():
    e_i = Evidence(id="E1", evidence_class="E_I", artifact="hash.txt")
    with pytest.raises(PromotionViolation):
        kernel.promote(e_i, target_status=Status(P="AUTHORSHIP_ESTABLISHED"))

def test_nk_031_p_master_requires_complete_graph():
    with pytest.raises(CompositionViolation):
        kernel.derive(
            premises=["C-001", "C-002"],
            rule="R-MASTER-DERIVATION",
            conclusion="P_master",
            is_master=True,
            evidence_objects=[Evidence(id="E1", evidence_class="E_P", artifact="art1")]
        )

# NK-036 through NK-044 (Adversarial Graph Closure & Path-Validity Tests)
def test_nk_041_cyclic_dependency_rejection():
    cyclic_graph = DependencyGraph(
        nodes={
            "C-001": [("C-002", None)],
            "C-002": [("C-003", None)],
            "C-003": [("C-001", None)]
        },
        allow_recursion=False
    )
    with pytest.raises(GraphCycleViolation):
        kernel.validate_dependency_graph(cyclic_graph)

def test_nk_042_self_referential_claim_rejection():
    self_ref_graph = DependencyGraph(
        nodes={
            "C-001": [("C-001", None)]
        },
        allow_recursion=False
    )
    with pytest.raises(GraphCycleViolation):
        kernel.validate_dependency_graph(self_ref_graph)

def test_nk_029_enhanced_provenance_plus_integrity_authorship_rejection():
    e_i = Evidence(id="E1", evidence_class="E_I", artifact="hash.txt")
    e_p = Evidence(id="E2", evidence_class="E_P", artifact="prov.log")
    with pytest.raises(PromotionViolation):
        kernel.promote([e_i, e_p], target_status=Status(P="AUTHORSHIP_ESTABLISHED"))

def test_acyclic_graph_acceptance():
    valid_graph = DependencyGraph(
        nodes={
            "C-003": [("C-002", None)],
            "C-002": [("C-001", None)],
            "C-001": []
        },
        allow_recursion=False
    )
    assert kernel.validate_dependency_graph(valid_graph) is True

# NK-050 through NK-060 (Semantic Laundering & Compositional Attack Suite)
def test_nk_051_verification_plus_integrity_does_not_equal_truth():
    e_i = Evidence(id="E1", evidence_class="E_I", artifact="hash.txt")
    with pytest.raises(PromotionViolation):
        kernel.promote([e_i, "VERIFIED_TAG"], target_status=Status(T="ESTABLISHED"))

def test_nk_052_observation_plus_measurement_does_not_equal_causation():
    class ObservationMock:
        evidence_class = "E_O"
        relevance_established = True
    with pytest.raises(PromotionViolation):
        kernel.promote(ObservationMock(), target_status=Status(T="C_CAUSAL"))

def test_nk_053_provenance_does_not_equal_authorship():
    class ProvenanceMock:
        evidence_class = "E_P"
        relevance_established = True
    with pytest.raises(PromotionViolation):
        kernel.promote(ProvenanceMock(), target_status=Status(P="AUTHORSHIP_ESTABLISHED"))

def test_nk_059_missing_evidence_is_not_refutation():
    class MissingEvidenceMock:
        evidence_class = "MISSING_EVIDENCE"
        relevance_established = True
    with pytest.raises(PromotionViolation):
        kernel.promote(MissingEvidenceMock(), target_status=Status(T="REFUTED"))

def test_nk_060_failed_establishment_is_not_false():
    class FailedEstMock:
        evidence_class = "FAILED_ESTABLISHMENT"
        relevance_established = True
    with pytest.raises(PromotionViolation):
        kernel.promote(FailedEstMock(), target_status=Status(T="REFUTED"))

def test_provenance_chain_validation_success():
    chain = [
        Evidence(id="E1", evidence_class="E_P", artifact="stage1.log"),
        Evidence(id="E2", evidence_class="E_P", artifact="final_target.bin")
    ]
    result = kernel.validate_provenance_chain("final_target.bin", chain, "R-PROVENANCE-CHAIN-001")
    assert result.status.P == "PROVENANCE_ESTABLISHED"

def test_provenance_chain_validation_termination_failure():
    chain = [
        Evidence(id="E1", evidence_class="E_P", artifact="stage1.log"),
        Evidence(id="E2", evidence_class="E_P", artifact="wrong_target.bin")
    ]
    with pytest.raises(ProvenanceViolation):
        kernel.validate_provenance_chain("final_target.bin", chain, "R-PROVENANCE-CHAIN-001")

# Positive controls
def test_valid_derivation_acceptance():
    result = kernel.derive(premises=["A-001", "A-002"], rule="R-EULER-IDENTITY", conclusion="C-001")
    assert result.status.T == "ESTABLISHED"

def test_explicit_provenance_acceptance():
    result = kernel.evaluate_provenance(artifact="art-001", chain=["E-P-001"], rule="R-PROVENANCE-CHAIN-001")
    assert result.status.P == "PROVENANCE_ESTABLISHED"

def test_valid_bridge_acceptance():
    valid_bridge = BridgeObject(
        id="B-001", model="M-001", target="X-001", correspondence="Gamma-001",
        bridge_rules=["RB-001"], measurements=["M-001"], epsilon=0.001,
        uncertainty_model="U-001", assumptions=["A-001"]
    )
    assert kernel.validate_bridge(valid_bridge) is True

def test_formal_assurance_ingestion():
    assurance = FormalAssuranceInput(
        specification="DaemonState.tla",
        property="SafetyInvariant",
        result="ESTABLISHED",
        scope="ModelA",
        evidence="tla_output.log"
    )
    status = kernel.ingest_formal_assurance(assurance)
    assert status.V == "VERIFIED"
