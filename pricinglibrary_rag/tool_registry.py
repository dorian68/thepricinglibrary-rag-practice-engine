"""Auditable tool registry for the agentic desk and quant-research DAG.

The registry is intentionally deterministic and local-first.  A tool can be a
real pricing/calculation adapter, a validator, a data loader, or a report
producer, but it must always have a typed contract, permissions, audit metadata,
and a replayable result.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


def _implementation(name: str) -> str:
    if name.startswith("canonical."):
        from .canonical_tools import list_canonical_tools
        tool=next((t for t in list_canonical_tools() if t["id"]==name.split(".",1)[1]),None)
        return "calculated" if tool and tool["available"] else "unavailable"
    leaf=name.split(".")[-1]
    if name in {"calc.black_scholes","calc.black76","calc.garman_kohlhagen","calc.greeks","risk.compute_greeks","calc.no_arbitrage_checks"} or leaf in {
        "price_vanilla_option","price_black76_option","price_black76_commodity_option","price_garman_kohlhagen","price_fx_option","price_crypto_option",
        "compute_delta","compute_gamma","compute_vega","compute_theta","compute_rho","price_autocall","price_autocall_mc"}:
        return "calculated"
    if name in {"risk.check_limits","book.limit_usage","calc.swap_pv_dv01","calc.cds_cs01"}:return "calculated"
    if name in {"tool.list","tool.describe","tool.healthcheck","tool.validate_input","tool.audit","tool.replay"}:return "implemented"
    if name.endswith("live_trading_guard"):return "implemented"
    if leaf in {"capture_rfq","parse_intent"}:return "implemented"
    if "hash" in name or name.endswith("snapshot_freeze"):return "implemented"
    if name.startswith("report.") and name!="report.export_pdf":return "implemented"
    return "unavailable"


PERMISSIONS = {
    "read",
    "calculate",
    "quote",
    "book_shadow",
    "book_live",
    "trade_live",
    "approve",
    "report",
    "compliance",
    "research",
    "validate",
    "admin",
}

DESK_ROLES = (
    "Sales",
    "Structurer",
    "Market Data",
    "Quant",
    "Pricing",
    "Trader",
    "Risk",
    "Report",
)

QUANT_RESEARCH_ROLES = (
    "Quant Researcher",
    "Data Engineer",
    "Feature Engineer",
    "ML / Quant Dev",
    "Validator / Skeptic",
    "Research Risk Manager",
    "Portfolio Manager",
    "Execution / Cost",
)

DESKS = ("Commodities", "Rates", "Credit", "FX", "Exotics", "CryptoVol")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    owner_agent: str
    orchestration: str
    permission: str
    category: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    artifact: str
    desk: str | None = None
    deterministic: bool = True
    mutates_state: bool = False
    requires_confirmation: bool = False
    audit_level: str = "full"
    evidence_required: tuple[str, ...] = ("source", "timestamp", "version")
    job_expectations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value=asdict(self)
        status=_implementation(self.name)
        value.update({"implementation_status":status,"executable":status!="unavailable",
                      "capability_notice":"Executed adapter, subject to validated inputs." if status!="unavailable" else
                          "Descriptor retained; no executable adapter is connected. Calls return unavailable without fabricated results."})
        return value


@dataclass(frozen=True)
class AgentSpec:
    role: str
    orchestration: str
    seniority: str
    mandate: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    forbidden_tools: tuple[str, ...]
    required_outputs: tuple[str, ...]
    job_profile_sources: tuple[str, ...]
    satisfaction_bar: float = 0.98

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolCallRecord:
    id: str
    tool_name: str
    agent_role: str
    desk: str | None
    payload: dict[str, Any]
    output: dict[str, Any]
    ok: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _schema(required: list[str] | None = None, properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "required": required or [],
        "properties": properties or {
            "query": {"type": "string"},
            "symbol": {"type": "string"},
            "payload": {"type": "object"},
            "confirmed": {"type": "boolean"},
        },
        "additionalProperties": True,
    }


COMMON_TOOLS = {
    "Tool Registry": [
        "tool.list", "tool.describe", "tool.validate_input", "tool.run",
        "tool.audit", "tool.replay", "tool.healthcheck",
    ],
    "Evidence Ledger": [
        "evidence.attach_source", "evidence.attach_market_snapshot",
        "evidence.attach_formula", "evidence.attach_model_version",
        "evidence.attach_backtest_run", "evidence.attach_risk_check",
        "evidence.sign_verdict", "evidence.export_report",
    ],
    "Market Data Spine": [
        "market.provider_status", "market.get_spot", "market.get_curve",
        "market.get_surface", "market.get_chain", "market.get_history",
        "market.get_corporate_actions", "market.get_calendar",
        "market.get_conventions", "market.staleness_check",
        "market.cross_source_reconcile", "market.snapshot_freeze",
    ],
    "Calculation Core": [
        "calc.black_scholes", "calc.black76", "calc.garman_kohlhagen",
        "calc.discount_curve", "calc.swap_pv_dv01", "calc.cds_cs01",
        "calc.var_cvar", "calc.greeks", "calc.scenario_grid",
        "calc.no_arbitrage_checks", "calc.reconcile_two_models",
    ],
    "Risk Core": [
        "risk.compute_greeks", "risk.compute_factor_exposure",
        "risk.compute_pnl_explain", "risk.compute_stress",
        "risk.compute_var_cvar", "risk.check_limits",
        "risk.check_concentration", "risk.check_liquidity",
        "risk.check_gap", "risk.kill_switch_status", "risk.position_size",
        "risk.margin_check",
    ],
    "Compliance Core": [
        "compliance.classify_client", "compliance.check_product_eligibility",
        "compliance.detect_advice_boundary", "compliance.check_disclaimer_required",
        "compliance.check_regulatory_flags", "compliance.check_restricted_underlying",
        "compliance.approval_required", "compliance.audit_language",
    ],
    "Report Core": [
        "report.generate_termsheet", "report.generate_pricing_note",
        "report.generate_risk_memo", "report.generate_model_validation_note",
        "report.generate_trade_ticket", "report.generate_research_memo",
        "report.generate_investment_committee_pack", "report.export_markdown",
        "report.export_pdf",
    ],
    "Book Core": [
        "book.snapshot", "book.add_position", "book.revalue",
        "book.pnl_today", "book.exposure_by_factor", "book.limit_usage",
        "book.position_lifecycle", "book.rollback", "book.mode_status",
    ],
    "Security Core": [
        "security.permission_check", "security.secret_redaction",
        "security.confirmation_required", "security.live_trading_guard",
        "security.rate_limit", "security.cost_cap",
        "security.entitlement_check", "security.log_redacted",
    ],
    "QA Core": [
        "qa.agent_smoke", "qa.tool_contract_test", "qa.replay_fixture",
        "qa.golden_case", "qa.diff_against_expected", "qa.fail_fast",
        "qa.coverage_report",
    ],
}

DESK_AGENT_TOOLS: dict[str, list[str]] = {
    "Sales": [
        "capture_rfq", "parse_intent", "classify_client_type",
        "classify_objective", "extract_underlying", "extract_horizon",
        "extract_directional_view", "extract_notional", "extract_currency",
        "extract_constraints", "detect_missing_fields", "ask_clarifying_question",
        "suitability_precheck", "product_eligibility_precheck",
        "advice_boundary_check", "retrieve_client_context",
        "retrieve_previous_rfqs", "route_to_desk", "create_rfq_ticket",
        "send_quote_summary", "log_client_language",
        "generate_sales_summary", "handoff_to_structurer",
    ],
    "Structurer": [
        "load_product_catalog", "match_objective_to_product_family",
        "build_vanilla_option_spec", "build_forward_spec", "build_swap_spec",
        "build_cap_floor_spec", "build_swaption_spec", "build_cds_spec",
        "build_cln_spec", "build_call_spread_spec", "build_put_spread_spec",
        "build_collar_spec", "build_barrier_spec", "build_autocall_spec",
        "build_range_accrual_spec", "build_calendar_spec",
        "build_risk_reversal_spec", "compare_payoff_profiles",
        "compare_cost_vs_protection", "compare_liquidity_complexity",
        "detect_embedded_leverage", "detect_path_dependency",
        "detect_model_risk", "draft_term_sheet", "explain_tradeoffs",
        "handoff_to_market_data",
    ],
    "Market Data": [
        "provider_status", "load_spot", "load_forward_curve",
        "load_discount_curve", "load_ois_curve", "load_swap_curve",
        "load_credit_curve", "load_cds_spreads", "load_fx_forward_points",
        "load_fx_vol_surface", "load_equity_vol_surface",
        "load_commodity_curve", "load_commodity_vol",
        "load_crypto_option_chain", "load_realized_vol",
        "load_correlation_matrix", "load_dividend_curve",
        "load_recovery_assumption", "load_holiday_calendar",
        "load_day_count_convention", "staleness_check", "outlier_check",
        "cross_provider_reconcile", "interpolate_curve",
        "interpolate_surface", "freeze_market_snapshot",
        "mark_data_quality", "handoff_to_quant",
    ],
    "Quant": [
        "select_model", "select_measure", "validate_product_model_match",
        "calibrate_black_scholes_vol", "calibrate_black76",
        "calibrate_garman_kohlhagen", "bootstrap_curve",
        "calibrate_hull_white", "bootstrap_hazard_curve",
        "calibrate_survival_curve", "calibrate_svi_smile",
        "calibrate_local_vol", "calibrate_local_stoch_vol",
        "calibrate_correlation", "run_monte_carlo", "run_pde_or_tree",
        "compute_greeks_model_side", "compute_model_error_bounds",
        "run_no_arbitrage_checks", "run_sensitivity_to_inputs",
        "compare_model_alternatives", "document_assumptions",
        "document_model_risk", "handoff_to_pricing",
    ],
    "Pricing": [
        "price_vanilla_option", "price_black76_option", "price_fx_option",
        "price_forward", "price_swap", "price_cap_floor", "price_swaption",
        "price_cds", "price_cln", "price_barrier", "price_autocall_mc",
        "price_crypto_option", "compute_delta", "compute_gamma",
        "compute_vega", "compute_theta", "compute_rho", "compute_dv01",
        "compute_cs01", "compute_correlation_risk", "compute_break_even",
        "compute_max_loss", "compute_payoff_grid", "scenario_reprice",
        "reconcile_price_vs_frontend", "reconcile_price_vs_secondary_model",
        "rounding_policy_apply", "generate_pricing_explanation",
        "handoff_to_trader",
    ],
    "Trader": [
        "load_book_inventory", "load_market_depth", "estimate_bid_ask_spread",
        "apply_bid_ask", "apply_structuring_margin", "apply_credit_charge",
        "apply_funding_charge", "apply_liquidity_charge",
        "apply_inventory_skew", "build_delta_hedge", "build_dv01_hedge",
        "build_cs01_hedge", "build_vega_hedge", "build_correlation_hedge",
        "estimate_slippage", "estimate_hedge_cost",
        "check_trade_size_vs_liquidity", "quote_validity_window",
        "generate_bid_mid_ask", "update_shadow_book", "prepare_trade_ticket",
        "request_risk_approval", "handoff_to_risk",
    ],
    "Risk": [
        "compute_position_greeks", "compute_factor_exposure", "compute_dv01",
        "compute_cs01", "compute_vega", "compute_gamma",
        "compute_jump_to_default", "compute_gap_risk",
        "compute_correlation_risk", "compute_var", "compute_cvar",
        "stress_parallel_shift", "stress_vol_shift",
        "stress_credit_widening", "stress_fx_gap", "stress_commodity_gap",
        "stress_crypto_weekend", "check_limit_usage", "check_concentration",
        "check_liquidity", "check_wrong_way_risk",
        "check_model_risk_rating", "approve_reject_or_escalate",
        "generate_risk_memo", "handoff_to_report",
    ],
    "Report": [
        "assemble_rfq_summary", "assemble_product_summary",
        "assemble_market_snapshot", "assemble_model_assumptions",
        "assemble_pricing_table", "assemble_greeks_table",
        "assemble_scenario_table", "assemble_risk_summary",
        "assemble_hedge_plan", "assemble_limitations", "generate_termsheet",
        "generate_pricing_note", "generate_risk_memo", "generate_client_email",
        "generate_internal_ticket", "apply_compliance_language",
        "attach_sources_and_audit", "export_markdown", "export_pdf",
        "archive_report", "send_to_user",
    ],
}

ASSET_CLASS_TOOLS: dict[str, list[str]] = {
    "Commodities": [
        "load_futures_curve", "load_storage_cost", "load_convenience_yield",
        "load_seasonality", "load_inventory_data", "load_opec_calendar",
        "load_roll_calendar", "price_black76_commodity_option",
        "price_calendar_spread", "compute_roll_yield", "stress_curve_parallel",
        "stress_curve_twist", "stress_inventory_shock", "hedge_with_futures",
    ],
    "Rates": [
        "load_ois_curve", "load_ibor_curve", "bootstrap_multi_curve",
        "load_swaption_cube", "compute_annuity", "compute_forward_swap_rate",
        "price_swap", "price_cap_floor", "price_swaption",
        "compute_dv01_bucketed", "compute_key_rate_duration",
        "curve_shift_stress", "curve_steepener_flattener_stress",
        "hedge_with_swap_futures",
    ],
    "Credit": [
        "load_cds_curve", "load_bond_curve", "load_recovery_assumption",
        "bootstrap_hazard_rates", "price_cds", "price_cln", "compute_cs01",
        "compute_jump_to_default", "basis_cds_bond",
        "issuer_concentration_check", "sector_concentration_check",
        "stress_spread_widening", "stress_downgrade", "hedge_with_index_cds",
    ],
    "FX": [
        "load_fx_spot", "load_forward_points", "load_domestic_foreign_curves",
        "load_fx_vol_surface", "price_forward", "price_garman_kohlhagen",
        "price_risk_reversal", "price_barrier_fx",
        "compute_delta_premium_adjusted", "compute_vega_by_tenor",
        "fixing_calendar_check", "gap_risk_around_fixing",
        "hedge_with_spot_forward",
    ],
    "Exotics": [
        "load_correlation_matrix", "load_dividend_curve", "load_smile_surface",
        "calibrate_local_vol", "calibrate_stoch_vol", "run_monte_carlo_paths",
        "price_autocall", "price_barrier", "price_range_accrual",
        "compute_pathwise_greeks", "compute_correlation_greek",
        "compute_gap_risk_barrier", "scenario_underlying_correlation_vol",
        "hedge_exotic_risk_decomposition",
    ],
    "CryptoVol": [
        "fetch_deribit_chain", "load_exchange_index_price", "load_perp_funding",
        "load_realized_vol", "load_implied_vol_surface", "calibrate_svi",
        "compute_skew", "price_crypto_option", "price_calendar",
        "price_risk_reversal", "compute_weekend_gap_risk",
        "compute_funding_basis", "liquidity_depth_check",
        "hedge_delta_perp_spot",
    ],
}

QUANT_AGENT_TOOLS: dict[str, list[str]] = {
    "Quant Researcher": [
        "literature_search", "mechanism_library", "economic_prior_builder",
        "hypothesis_template", "signal_spec_builder", "universe_spec_builder",
        "horizon_spec_builder", "cost_assumption_spec", "primary_metric_spec",
        "decision_threshold_spec", "expected_sign_magnitude_spec",
        "parameter_grid_spec", "n_trials_estimator",
        "pre_registration_writer", "pre_registration_hash", "spec_freeze",
        "spec_diff_detector", "reject_no_mechanism", "handoff_to_data_engineer",
    ],
    "Data Engineer": [
        "provider_status", "download_ohlcv", "download_index_membership_asof",
        "download_delisting_returns", "download_corporate_actions",
        "normalize_ohlcv", "adjust_splits_dividends", "align_sessions",
        "align_timezones", "calendar_join", "missing_data_report",
        "outlier_detection", "stale_data_detection", "survivorship_audit",
        "lookahead_audit", "asof_snapshot_freeze", "dataset_hash",
        "dataset_lineage_report", "train_validation_lockbox_split",
        "handoff_to_feature_engineer",
    ],
    "Feature Engineer": [
        "trailing_return_features", "rolling_vol_features", "ema_features",
        "atr_features", "rsi_features", "macd_features", "donchian_features",
        "bollinger_features", "zscore_features", "volume_features",
        "realized_vol_features", "regime_features",
        "fractional_differentiation", "stationarity_test_adf",
        "feature_winsorization", "feature_standardization_train_only",
        "feature_lagging", "leakage_scan_center_true",
        "negative_shift_scan", "shift_invariance_test",
        "feature_importance_precheck", "feature_manifest",
        "handoff_to_ml_quant_dev",
    ],
    "ML / Quant Dev": [
        "primary_signal_runner", "strategy_factory", "parameter_grid_runner",
        "triple_barrier_labeling", "label_endtime_builder", "purged_kfold",
        "cpcv_splitter", "embargo_applier", "sample_uniqueness_weights",
        "sequential_bootstrap_sampler", "meta_feature_matrix_builder",
        "calibrated_classifier_fit", "probability_calibration_in_fold",
        "threshold_policy_builder", "probability_to_size",
        "risk_multiplier_clamp", "mda_feature_importance",
        "nested_regime_router_cv", "dl_sequence_filter_train",
        "dl_architecture_grid_accounting", "walk_forward_runner",
        "bar_return_extractor", "perf_matrix_builder", "trial_ledger_record",
        "model_card_writer", "handoff_to_validator",
    ],
    "Validator / Skeptic": [
        "trial_ledger_load", "true_n_trials_compute", "probabilistic_sharpe",
        "deflated_sharpe", "harvey_liu_haircut", "pbo_cscv",
        "bh_fdr_correction", "bonferroni_correction",
        "parameter_neighborhood_test", "min_trade_count_check",
        "best_trade_concentration_check", "worst_path_check",
        "fold_dispersion_check", "regime_mapping_stability_check",
        "lockbox_register", "lockbox_evaluate_once",
        "lockbox_second_read_guard", "oos_retention_check",
        "materiality_floor_check", "net_of_cost_check",
        "negative_results_report", "verdict_writer", "promote_or_kill",
        "handoff_to_risk_manager",
    ],
    "Research Risk Manager": [
        "position_sizing", "vol_targeting", "regime_risk_multiplier",
        "max_drawdown_policy", "daily_loss_limit", "weekly_loss_limit",
        "kill_switch", "var_cvar", "tail_stress", "gap_stress",
        "margin_check", "minimum_lot_check", "tradability_check",
        "exposure_aggregation", "correlation_to_book",
        "liquidity_adjusted_size", "risk_state_persistence",
        "risk_breach_report", "paper_risk_policy",
        "handoff_to_portfolio_manager",
    ],
    "Portfolio Manager": [
        "load_validated_edges", "edge_correlation_matrix",
        "crisis_correlation_stress", "asset_selector", "capital_allocator",
        "risk_budget_allocator", "max_corr_gate", "diversification_score",
        "portfolio_backtest", "portfolio_var_cvar", "portfolio_drawdown",
        "marginal_contribution_to_risk", "capacity_by_edge",
        "rebalance_policy", "allocation_freeze", "portfolio_report",
        "handoff_to_execution_cost",
    ],
    "Execution / Cost": [
        "spread_model", "commission_model", "swap_financing_model",
        "slippage_model", "market_impact_model", "capacity_curve",
        "turnover_analysis", "holding_period_analysis", "order_sizing",
        "order_manager", "stop_manager", "trade_lifecycle", "broker_specs",
        "broker_simulator", "mt5_adapter_guard", "paper_order_router",
        "live_trading_guard", "execution_replay", "net_edge_after_costs",
        "execution_report",
    ],
}

JOB_PROFILE_SOURCES = (
    "O*NET Financial Quantitative Analysts 13-2099.01",
    "O*NET Securities, Commodities, and Financial Services Sales Agents 41-3031.00",
    "O*NET Financial Risk Specialists 13-2054.00",
    "O*NET Financial and Investment Analysts 13-2051.00",
    "O*NET Business Intelligence Analysts 15-2051.01",
    "BLS Financial Analysts Occupational Outlook Handbook",
    "BLS Securities, Commodities, and Financial Services Sales Agents Occupational Outlook Handbook",
)

ROLE_JOB_EXPECTATIONS: dict[str, tuple[str, ...]] = {
    "Sales": ("client qualification", "RFQ capture", "market explanation", "regulated advice boundary", "transaction records"),
    "Structurer": ("financial package structuring", "payoff comparison", "term sheet drafting", "client objective fit", "model risk escalation"),
    "Market Data": ("data repository querying", "data quality maintenance", "market intelligence reporting", "staleness controls", "metadata documentation"),
    "Quant": ("model specification", "derivative valuation", "risk model development", "analytical support to traders", "independent verification"),
    "Pricing": ("security valuation", "pricing model use", "scenario analysis", "result interpretation", "model reconciliation"),
    "Trader": ("bid/offer making", "market and position monitoring", "trade tickets", "hedge strategy", "transaction records"),
    "Risk": ("market and credit exposure measurement", "statistical risk analysis", "scenario stress", "limits", "risk disclosure"),
    "Report": ("custom report generation", "stakeholder communication", "template library maintenance", "technical documentation", "audit-ready outputs"),
    "Quant Researcher": ("falsifiable hypothesis", "literature review", "model specification", "research reporting", "trial budget discipline"),
    "Data Engineer": ("data acquisition", "quality controls", "lineage", "point-in-time snapshots", "data repository maintenance"),
    "Feature Engineer": ("causal features", "stationarity", "leakage controls", "feature documentation", "analytical support"),
    "ML / Quant Dev": ("model libraries", "software testing", "portfolio optimization", "performance measurement", "trading-system metrics"),
    "Validator / Skeptic": ("independent model verification", "risk model methodology", "statistical deflation", "lockbox discipline", "negative reporting"),
    "Research Risk Manager": ("risk limits", "tail scenarios", "drawdown policy", "position sizing", "contingency planning"),
    "Portfolio Manager": ("portfolio construction", "allocation", "investment strategy explanation", "risk diversification", "stakeholder reporting"),
    "Execution / Cost": ("trade execution", "transaction costs", "market impact", "capacity", "broker/order controls"),
}


def _permission_for(tool_name: str, role: str) -> str:
    t = tool_name.lower()
    if t.startswith(("security.", "compliance.")) or "compliance" in t or "suitability" in t or "eligibility" in t:
        return "compliance"
    if t.startswith(("report.", "evidence.")) or any(k in t for k in ("report", "memo", "termsheet", "email", "export", "archive", "note", "summary")):
        return "report"
    if "live" in t or "order_manager" in t:
        return "trade_live"
    if "book.add" in t or "update_shadow_book" in t:
        return "book_shadow"
    if any(k in t for k in ("approve", "reject", "limit", "risk", "var", "stress", "kill", "lockbox", "validate", "check")):
        return "validate"
    if any(k in t for k in ("price", "calc", "compute", "calibrate", "bootstrap", "model", "simulate", "monte")):
        return "calculate"
    if role in QUANT_RESEARCH_ROLES:
        return "research"
    return "read"


def _artifact_for(role: str) -> str:
    return {
        "Sales": "RFQTicket",
        "Structurer": "ProductSpec",
        "Market Data": "MarketSnapshot",
        "Quant": "ModelCard",
        "Pricing": "PricingPack",
        "Trader": "QuotePack",
        "Risk": "RiskVerdict",
        "Report": "ClientReport",
        "Quant Researcher": "PreRegistration",
        "Data Engineer": "DatasetManifest",
        "Feature Engineer": "FeatureManifest",
        "ML / Quant Dev": "CVRecord",
        "Validator / Skeptic": "ValidationVerdict",
        "Research Risk Manager": "RiskPolicy",
        "Portfolio Manager": "AllocationPlan",
        "Execution / Cost": "ExecutionVerdict",
        "Common": "EvidenceRecord",
    }.get(role, "Artifact")


def _category_for(tool_name: str) -> str:
    if "." in tool_name:
        return tool_name.split(".", 1)[0]
    for marker, category in (
        ("price", "pricing"),
        ("compute", "risk_calculation"),
        ("load", "market_data"),
        ("calibrate", "modeling"),
        ("stress", "risk"),
        ("report", "reporting"),
        ("handoff", "handoff"),
        ("audit", "audit"),
    ):
        if marker in tool_name:
            return category
    return "workflow"


def _title(tool_name: str) -> str:
    return tool_name.replace("_", " ").replace(".", " / ")


def _tool_id(orchestration: str, role: str, tool_name: str, desk: str | None = None) -> str:
    role_slug = role.lower().replace(" / ", "_").replace(" ", "_")
    if orchestration == "common":
        return tool_name
    prefix = "desk" if orchestration == "agentic_desk" else "quant"
    if desk:
        return f"{prefix}.{desk.lower()}.{role_slug}.{tool_name}"
    return f"{prefix}.{role_slug}.{tool_name}"


def _make_tool(orchestration: str, role: str, tool_name: str, desk: str | None = None) -> ToolSpec:
    permission = _permission_for(tool_name, role)
    return ToolSpec(
        name=_tool_id(orchestration, role, tool_name, desk),
        owner_agent=role,
        desk=desk,
        orchestration=orchestration,
        permission=permission,
        category=_category_for(tool_name),
        description=f"{role} capability: {_title(tool_name)}.",
        input_schema=_schema(required=["query"] if tool_name in {"capture_rfq", "parse_intent"} else []),
        output_schema=_schema(properties={
            "status": {"type": "string"},
            "artifact": {"type": "string"},
            "summary": {"type": "string"},
            "evidence": {"type": "array"},
            "warnings": {"type": "array"},
        }),
        artifact=_artifact_for(role),
        deterministic=permission not in {"trade_live"},
        mutates_state=permission in {"book_shadow", "book_live", "trade_live"},
        requires_confirmation=permission in {"book_live", "trade_live"},
        job_expectations=ROLE_JOB_EXPECTATIONS.get(role, ()),
    )


def _build_tools() -> dict[str, ToolSpec]:
    tools: dict[str, ToolSpec] = {}
    for group, names in COMMON_TOOLS.items():
        for name in names:
            spec = ToolSpec(
                name=name,
                owner_agent="Common",
                orchestration="common",
                permission=_permission_for(name, "Common"),
                category=group,
                description=f"Shared service: {_title(name)}.",
                input_schema=_schema(),
                output_schema=_schema(properties={
                    "status": {"type": "string"},
                    "summary": {"type": "string"},
                    "evidence": {"type": "array"},
                }),
                artifact="EvidenceRecord",
            )
            tools[spec.name] = spec

    for role, names in DESK_AGENT_TOOLS.items():
        for name in names:
            spec = _make_tool("agentic_desk", role, name)
            tools[spec.name] = spec
        for desk, desk_names in ASSET_CLASS_TOOLS.items():
            for name in desk_names:
                if role in {"Market Data", "Quant", "Pricing", "Trader", "Risk"}:
                    spec = _make_tool("agentic_desk", role, name, desk=desk)
                    tools[spec.name] = spec

    for role, names in QUANT_AGENT_TOOLS.items():
        for name in names:
            spec = _make_tool("quant_pipeline", role, name)
            tools[spec.name] = spec
    from .canonical_tools import list_canonical_tools
    for canonical in list_canonical_tools():
        name="canonical."+canonical["id"]
        tools[name]=ToolSpec(name=name,owner_agent="Common",orchestration="common",permission="calculate",category="canonical_calculation",
            description="Execute the actual versioned "+canonical["id"]+" engine with its strict canonical JSON input.",
            input_schema={"type":"object","properties":{"input":{"type":"object"},"format":{"enum":canonical["formats"]}},"required":["input"],"additionalProperties":False},
            output_schema=_schema(),artifact="VerifiedCalculation")
    return tools


def _build_agents(tools: dict[str, ToolSpec]) -> dict[str, AgentSpec]:
    agents: dict[str, AgentSpec] = {}
    common = tuple(name for name, spec in tools.items() if spec.orchestration == "common")
    for role in DESK_ROLES:
        allowed = tuple(name for name, spec in tools.items() if spec.owner_agent == role and spec.orchestration == "agentic_desk")
        agents[role] = AgentSpec(
            role=role,
            orchestration="agentic_desk",
            seniority="Senior trading-floor specialist",
            mandate=ROLE_JOB_EXPECTATIONS[role],
            allowed_tools=common + allowed,
            forbidden_tools=("live_order_submit", "book_live_without_confirmation"),
            required_outputs=(_artifact_for(role),),
            job_profile_sources=JOB_PROFILE_SOURCES,
        )
    for role in QUANT_RESEARCH_ROLES:
        allowed = tuple(name for name, spec in tools.items() if spec.owner_agent == role and spec.orchestration == "quant_pipeline")
        agents[role] = AgentSpec(
            role=role,
            orchestration="quant_pipeline",
            seniority="Institutional quant-research gate owner",
            mandate=ROLE_JOB_EXPECTATIONS[role],
            allowed_tools=common + allowed,
            forbidden_tools=("lockbox_second_read", "unregistered_backtest", "live_trading_without_guard"),
            required_outputs=(_artifact_for(role),),
            job_profile_sources=JOB_PROFILE_SOURCES,
        )
    return agents


class ToolRegistry:
    def __init__(self, tools: dict[str, ToolSpec] | None = None) -> None:
        self.tools = tools or _build_tools()
        self.agents = _build_agents(self.tools)
        self.audit_log: dict[str, ToolCallRecord] = {}

    def list(self, agent_role: str | None = None, desk: str | None = None, permission_scope: str | None = None) -> list[dict[str, Any]]:
        specs = self.tools.values()
        if agent_role:
            specs = [s for s in specs if s.owner_agent == agent_role or s.owner_agent == "Common"]
        if desk:
            specs = [s for s in specs if s.desk in (None, desk)]
        if permission_scope:
            specs = [s for s in specs if s.permission == permission_scope]
        return [s.to_dict() for s in sorted(specs, key=lambda item: item.name)]

    def describe(self, tool_name: str) -> dict[str, Any]:
        return self._resolve(tool_name).to_dict()

    def validate_input(self, tool_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        spec = self._resolve(tool_name)
        payload = payload or {}
        if not isinstance(payload,dict):
            return {'ok':False,'tool':spec.name,'missing':[],'errors':['payload must be an object'],'schema':spec.input_schema}
        missing = [key for key in spec.input_schema.get("required", []) if key not in payload]
        errors=[];leaf=spec.name.split('.')[-1]
        exclusions={'risk.check_limits','book.limit_usage','calc.swap_pv_dv01','calc.cds_cs01'}
        if _implementation(spec.name)=='calculated' and not spec.name.startswith('canonical.') and spec.name not in exclusions and leaf not in {'price_autocall','price_autocall_mc'}:
            from .trusted_analytics import normalise_ticket
            model='black76' if 'black76' in leaf else 'gk' if leaf in {'garman_kohlhagen','price_garman_kohlhagen','price_fx_option'} else 'bsm'
            try:normalise_ticket(payload,model=model)
            except (ValueError,TypeError) as exc:errors.append(str(exc))
        return {"ok": not missing and not errors, "tool": spec.name, "missing": missing,'errors':errors,"schema": spec.input_schema,
                'validation_scope':'Declared required keys and supported input adapters; model/market validation and deployment approval are not implied.'}

    def healthcheck(self, tool_name: str) -> dict[str, Any]:
        spec = self._resolve(tool_name)
        contract = bool(spec.input_schema and spec.output_schema and spec.permission in PERMISSIONS)
        return {
            "ok": contract and _implementation(spec.name)!="unavailable",
            "descriptor_ok": contract,
            "implementation_status":_implementation(spec.name),
            "tool": spec.name,
            "permission": spec.permission,
            "audit_level": spec.audit_level,
            "deterministic": spec.deterministic,
            "artifact": spec.artifact,
        }

    def run(self, tool_name: str, payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        spec = self._resolve(tool_name)
        payload = payload or {}
        context = context or {}
        validation = self.validate_input(spec.name, payload)
        if not validation["ok"]:
            output = {
                "status": "failed",
                "data": None,
                "artifact": spec.artifact,
                "summary": "Input validation failed.",
                "evidence": [],
                "warnings": ([f"missing: {', '.join(validation['missing'])}"] if validation['missing'] else [])+validation.get('errors',[]),
            }
            return self._record(spec, payload, output, ok=False)
        if spec.requires_confirmation and not payload.get("confirmed") and not context.get("confirmed"):
            output = {
                "status": "blocked",
                "artifact": spec.artifact,
                "summary": "Confirmation required for state-changing or live-trading action.",
                "evidence": [{"type": "permission", "value": spec.permission}],
                "warnings": ["confirmation_required"],
            }
            return self._record(spec, payload, output, ok=False)
        try:
            output = self._execute(spec, payload, context)
        except (ValueError,TypeError,KeyError,RuntimeError) as exc:
            output={"status":"failed","artifact":spec.artifact,"summary":"A valid explicit input is required.",
                    "data":None,"evidence":[],"warnings":[str(exc)]}
        return self._record(spec, payload, output, ok=output.get("status") == "ok")

    def audit(self, tool_call_id: str) -> dict[str, Any]:
        if tool_call_id not in self.audit_log:
            raise KeyError(f"Unknown tool call id: {tool_call_id}")
        return self.audit_log[tool_call_id].to_dict()

    def replay(self, tool_call_id: str) -> dict[str, Any]:
        record = self.audit(tool_call_id)
        return self.run(record["tool_name"], payload=record["payload"])

    def coverage_report(self) -> dict[str, Any]:
        per_agent = {}
        for role, spec in self.agents.items():
            role_specific = [t for t in spec.allowed_tools if self.tools[t].owner_agent != "Common"]
            per_agent[role] = {
                "orchestration": spec.orchestration,
                "role_specific_tools": len(role_specific),
                "shared_tools": len(spec.allowed_tools) - len(role_specific),
                "required_outputs": list(spec.required_outputs),
                "job_expectations": list(spec.mandate),
                "bar": spec.satisfaction_bar,
                "ok": len(role_specific) >= (17 if spec.orchestration == "quant_pipeline" else 21),
            }
        descriptors_ok=all(v["ok"] for v in per_agent.values())
        executable=sum(_implementation(name)!="unavailable" for name in self.tools)
        return {
            "agents": per_agent,
            "tool_count": len(self.tools),
            "common_tool_count": sum(1 for s in self.tools.values() if s.owner_agent == "Common"),
            "agent_count": len(self.agents),
            "all_ok": descriptors_ok and executable==len(self.tools),
            "all_descriptors_valid":descriptors_ok,
            "executable_tool_count":executable,
            "unavailable_tool_count":len(self.tools)-executable,
            "coverage_notice":"Descriptor counts are not implementation coverage, financial validation or a satisfaction score.",
        }

    def agent(self, role: str) -> dict[str, Any]:
        return self.agents[role].to_dict()

    def _resolve(self, tool_name: str) -> ToolSpec:
        if tool_name in self.tools:
            return self.tools[tool_name]
        suffix_matches = [s for s in self.tools.values() if s.name.endswith(f".{tool_name}")]
        if len(suffix_matches) == 1:
            return suffix_matches[0]
        if suffix_matches:
            names = ", ".join(s.name for s in suffix_matches[:8])
            raise KeyError(f"Ambiguous tool name {tool_name!r}; use one of: {names}")
        raise KeyError(f"Unknown tool: {tool_name}")

    def _record(self, spec: ToolSpec, payload: dict[str, Any], output: dict[str, Any], ok: bool) -> dict[str, Any]:
        call_id = f"toolcall_{uuid.uuid4().hex[:12]}"
        record = ToolCallRecord(
            id=call_id,
            tool_name=spec.name,
            agent_role=spec.owner_agent,
            desk=spec.desk,
            payload=_redact(payload),
            output=output,
            ok=ok,
        )
        self.audit_log[call_id] = record
        result = record.to_dict()
        result["tool_spec"] = {
            "permission": spec.permission,
            "artifact": spec.artifact,
            "audit_level": spec.audit_level,
        }
        return result

    def _execute(self, spec: ToolSpec, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        from .trusted_analytics import option_analysis, autocall_analysis, number
        status=_implementation(spec.name)
        if status=="unavailable":
            return {"status":"unavailable","artifact":spec.artifact,"data":None,
                    "summary":"This capability is registered but has no executable adapter.",
                    "evidence":[],"warnings":["capability_not_implemented"],
                    "implementation_status":status}
        name=spec.name;leaf=name.split(".")[-1]
        model="black76" if "black76" in leaf else "gk" if leaf in {"garman_kohlhagen","price_garman_kohlhagen","price_fx_option"} else "bsm"
        if name.startswith("canonical."):
            from .canonical_tools import run_canonical_tool
            result=run_canonical_tool(name.split(".",1)[1],payload["input"],payload.get("format","json"))
            data=result if isinstance(result,dict) else {"format":payload.get("format"),"content":result}
        elif status=="calculated" and name not in {"risk.check_limits","book.limit_usage","calc.swap_pv_dv01","calc.cds_cs01"}:
            if leaf in {"price_autocall","price_autocall_mc"}:
                data=autocall_analysis(payload)
            else:
                data=option_analysis(payload,model=model)
                if leaf.startswith("compute_") and leaf.removeprefix("compute_") in data["greeks"]:
                    data={**data,"value":data["greeks"][leaf.removeprefix("compute_")],"metric":leaf.removeprefix("compute_"),
                          "unit":data["conventions"].get(leaf.removeprefix("compute_"),"per underlying price unit")}
        elif name in {"risk.check_limits","book.limit_usage"}:
            loss=number(payload.get("loss"),"loss",-1e15,1e15)
            limit=number(payload.get("limit"),"limit",1e-12,1e15)
            usage=abs(loss)/limit
            data={"loss":loss,"limit":limit,"limit_usage":usage,"verdict":"WITHIN_LIMIT" if usage<=1 else "BREACHED",
                  "blocks_deployment":usage>1,"scope":"Comparison of supplied educational scenario loss and supplied limit, not a production risk approval."}
        elif name in {"calc.swap_pv_dv01","calc.cds_cs01"}:
            notional=number(payload.get("notional"),"notional",0,1e15)
            annuity=number(payload.get("annuity"),"annuity",0,100)
            dv01=notional*annuity*.0001
            data={"value":dv01,"unit":"currency per basis point","inputs":{"notional":notional,"annuity":annuity},
                  "formula":"notional * supplied annuity * 0.0001","metric":"CS01" if name.endswith("cs01") else "DV01",
                  "limitations":["Supplied annuity approximation; this is not an independently bootstrapped curve or hazard calibration."]}
            if name=="calc.swap_pv_dv01" and "parRate" in payload and "fixedRate" in payload:
                data["payer_pv"]=notional*annuity*(number(payload["parRate"],"parRate",-1,1)-number(payload["fixedRate"],"fixedRate",-1,1))
        elif name=="tool.list":data={"tools":self.list()}
        elif name=="tool.describe":data=self.describe(payload["tool_name"])
        elif name=="tool.healthcheck":data=self.healthcheck(payload["tool_name"])
        elif name=="tool.validate_input":data=self.validate_input(payload["tool_name"],payload.get("payload"))
        elif name=="tool.audit":data=self.audit(payload["tool_call_id"])
        elif name=="tool.replay":data=self.replay(payload["tool_call_id"])
        elif name.endswith("live_trading_guard"):
            data={"live_execution_enabled":False,"blocked":True,"order_submitted":False,
                  "reason":"No live broker execution adapter is configured by this tool. Confirmation records do not enable live trading.",
                  "approval_recorded":bool(context.get("confirmed") or payload.get("confirmed"))}
        elif leaf in {"capture_rfq","parse_intent"}:
            from .desk import parse_request
            data=parse_request(str(payload["query"]))
            data["scope"]="Deterministic local intent parsing; explicit requested ticket fields are retained."
        elif "hash" in name or name.endswith("snapshot_freeze"):
            digest=hashlib.sha256(json.dumps(_redact(payload),sort_keys=True,default=str).encode()).hexdigest()
            data={"hash":digest,"algorithm":"sha256","scope":"Content hash of supplied redacted payload; no external data retrieval, signature or market validation implied."}
        else:
            # Render supplied evidence into a real communication artifact;
            # never invent prices, sources or an external delivery event.
            data={"format":"markdown","content":"# "+_title(name)+"\n\n"+json.dumps(_redact(payload),indent=2,ensure_ascii=False),
                  "scope":"Report assembled from caller-supplied data; not externally sent or independently verified."}
        return {"status":"ok","artifact":spec.artifact,"summary":"Executed "+name+" with explicit inputs.",
                "data":data,"evidence":[{"type":"implementation","value":"tpl.trusted-analytics.v1"}],
                "warnings":list(data.get("limitations",[])),"implementation_status":status}


def _redact(value: Any) -> Any:
    if isinstance(value,float) and not math.isfinite(value):
        return "invalid_non_finite_number"
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if any(secret in key.lower() for secret in ("token", "secret", "password", "api_key")):
                text = str(item)
                out[key] = f"{text[:4]}...{text[-4:]}(len={len(text)})" if text else ""
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


_REGISTRY: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ToolRegistry()
    return _REGISTRY


def role_tool_names(role: str, desk: str | None = None, include_common: bool = False) -> list[str]:
    registry = get_tool_registry()
    names = [
        spec.name for spec in registry.tools.values()
        if spec.owner_agent == role and spec.orchestration == "agentic_desk" and spec.desk in (None, desk)
    ]
    if include_common:
        names.extend(spec.name for spec in registry.tools.values() if spec.owner_agent == "Common")
    return sorted(names)

