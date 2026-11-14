from pricinglibrary_rag.tool_registry import DESK_ROLES, QUANT_RESEARCH_ROLES, get_tool_registry


def test_tool_registry_covers_all_agents():
    registry = get_tool_registry()
    coverage = registry.coverage_report()

    assert coverage["agent_count"] == len(DESK_ROLES) + len(QUANT_RESEARCH_ROLES)
    assert coverage["all_ok"]
    assert coverage["tool_count"] >= 500


def test_tool_registry_executes_and_audits():
    registry = get_tool_registry()
    result = registry.run("desk.sales.capture_rfq", payload={"query": "hedge EURUSD"})

    assert result["ok"]
    assert result["output"]["artifact"] == "RFQTicket"
    audit = registry.audit(result["id"])
    assert audit["tool_name"] == result["tool_name"]
    assert registry.replay(result["id"])["ok"]


def test_quant_validator_has_required_gates():
    registry = get_tool_registry()
    validator_tools = {
        name for name, spec in registry.tools.items()
        if spec.owner_agent == "Validator / Skeptic"
    }

    for suffix in [
        "deflated_sharpe",
        "pbo_cscv",
        "lockbox_evaluate_once",
        "bh_fdr_correction",
        "negative_results_report",
    ]:
        assert any(name.endswith(f".{suffix}") for name in validator_tools)

