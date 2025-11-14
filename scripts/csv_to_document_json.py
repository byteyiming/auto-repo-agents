"""Convert the document management CSV into the runtime JSON catalog.

Usage:
    python scripts/csv_to_document_json.py \
        --input JobTrackrAI_Document_Management_Template_v3.csv \
        --output config/document_definitions.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, MutableMapping, Optional

CSV_ENCODING = "utf-8"
DEFAULT_PROMPT_SUFFIX = "_prompt"

SPECIAL_AGENT_OVERRIDES: Dict[str, Dict[str, str]] = {
    # Legacy special-case agents that must stay bespoke.
    "requirements": {"agent_class": "special", "special_key": "requirements_analyst"},
    "quality_review": {"agent_class": "special", "special_key": "quality_reviewer"},
    "document_improver": {"agent_class": "special", "special_key": "document_improver"},
    "format_converter": {"agent_class": "special", "special_key": "format_converter"},
    "code_analyst": {"agent_class": "special", "special_key": "code_analyst"},
}

ID_OVERRIDES: Dict[str, str] = {
    "Project Charter": "project_charter",
    "Requirements Document": "requirements",
    "Business Model": "business_model",
    "Marketing Plan": "marketing_plan",
    "Product Charter": "product_charter",
    "PRD (Product Requirements Doc)": "prd",
    "FSD (Functional Spec Doc)": "fsd",
    "TAD (Technical Architecture Doc)": "tad",
    "Developer Guide / README": "developer_guide",
    "User Support Document": "user_support_doc",
    "Support Playbook": "support_playbook",
    "Support Team Training Document": "support_training_doc",
    "Knowledge Base": "knowledge_base",
    "Experimentation / A/B Testing Docs": "ab_testing_docs",
    "Privacy Policy / GDPR Compliance": "privacy_policy",
    "Legal / Terms of Service (ToS)": "terms_of_service",
    "Go-To-Market (GTM) Strategy": "gtm_strategy",
    "Backup & Recovery Plan": "backup_recovery_plan",
    "SLA / Service Level Agreement": "sla",
    "Business Continuity Plan (BCP)": "bcp",
    "Market Research & Competitive Analysis": "market_research",
    "Technical Audit / Compliance Audit Reports": "technical_audit",
    "Experimentation / Feature Flag Docs": "feature_flag_docs",
    "Data Governance / Data Quality Policy": "data_governance_policy",
    "Work Breakdown Structure (WBS)": "wbs",
    "PM Management Doc": "pm_management_doc",
    "Stakeholders Document": "stakeholders_doc",
    "Feature Roadmap": "feature_roadmap",
    "Change Management Plan": "change_management_plan",
    "Risk Management / Mitigation Plan": "risk_management_plan",
    "UI Mockups / Mockups Docs": "ui_mockups",
    "UI Style Guide": "ui_style_guide",
    "Interaction / Flow Diagrams": "interaction_flows",
    "Onboarding Flow": "onboarding_flow",
    "API Documentation": "api_documentation",
    "Database Schema": "database_schema",
    "CI/CD Pipeline Doc": "cicd_doc",
    "Deployment Plan": "deployment_plan",
    "Scalability Plan": "scalability_plan",
    "Monitoring & Logging Plan": "monitoring_logging_plan",
    "Configuration Management Plan": "configuration_management_plan",
    "Technical Debt Log / Refactoring Plan": "technical_debt_log",
    "API Versioning & Deprecation Policy": "api_versioning_policy",
    "Test Plan Document": "test_plan",
    "User Feedback Plan": "user_feedback_plan",
    "Security Plan": "security_plan",
    "Accessibility Plan / ADA Compliance": "accessibility_plan",
    "Localization / Internationalization Plan": "localization_plan",
    "Data Retention & Archiving Policy": "data_retention_policy",
    "Incident Response Plan": "incident_response_plan",
    "End-of-Life (EOL) Policy": "eol_policy",
    "KPIs / Metrics Document": "kpi_metrics_doc",
    "Dashboard Metrics Specification": "dashboard_metrics",
    "Release Notes / Version History": "release_notes",
    "Third-Party Integration Documentation": "third_party_integrations",
    "User Analytics / Behavior Tracking Doc": "user_analytics",
    "Maintenance Plan": "maintenance_plan",
    "Vendor / Supplier Management Docs": "vendor_management_docs",
    "Cloud Infrastructure / Cost Management Doc": "cloud_infrastructure_doc",
    "Performance Tuning & Optimization Doc": "performance_optimization_doc",
    "Innovation / R&D Plan": "innovation_plan",
}

PROMPT_OVERRIDES: Dict[str, str] = {
    "requirements": "REQUIREMENTS_ANALYST_PROMPT",
    "project_charter": "PROJECT_CHARTER_PROMPT",
    "business_model": "BUSINESS_MODEL_PROMPT",
    "marketing_plan": "MARKETING_PLAN_PROMPT",
    "api_documentation": "API_DOCUMENTATION_PROMPT",
    "database_schema": "DATABASE_SCHEMA_PROMPT",
    "test_plan": "TEST_PLAN_PROMPT",
    "security_plan": "SECURITY_PLAN_PROMPT",
}

CSV_COLUMNS = {
    "category": "文档类别",
    "name": "文档名称",
    "description": "用途 / 说明",
    "priority": "优先级",
    "owner": "建议负责人",
    "status": "状态",
    "audience": "适用对象",
    "stage": "阶段适用性",
    "stage_notes": "阶段说明",
    "related_docs": "依赖文档 / Related Docs",
    "notes": "改进建议 / Notes",
    "frequency": "使用频率 / Usage Frequency",
    "must_have": "是否必需 / Must-Have",
}


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to the source CSV")
    parser.add_argument("--output", required=True, type=Path, help="Path to the output JSON file")
    return parser.parse_args(argv)


def slugify(value: str) -> str:
    """Convert arbitrary text into snake_case identifier."""
    import re

    cleaned = re.sub(r"[^\w]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "document"


def normalize_list(raw: str) -> List[str]:
    if not raw:
        return []
    import re

    parts = re.split(r"[;,/、，\n]+", raw)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned


def build_document_ids(rows: List[MutableMapping[str, str]]) -> Dict[str, str]:
    """Assign deterministic IDs to each document name with collision handling."""
    id_map: Dict[str, str] = {}
    seen: Dict[str, int] = defaultdict(int)

    for row in rows:
        name = row.get(CSV_COLUMNS["name"], "").strip()
        if not name:
            raise ValueError("CSV row missing document name.")

        doc_id = ID_OVERRIDES.get(name)
        if not doc_id:
            doc_id = slugify(name)

        count = seen[doc_id]
        if count:
            doc_id = f"{doc_id}_{count+1}"
        seen[doc_id] += 1
        id_map[name] = doc_id

    duplicates = [doc for doc, count in seen.items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate document IDs detected after normalization: {duplicates}")

    return id_map


def resolve_dependencies(raw_values: List[str], id_map: Dict[str, str]) -> List[str]:
    dependencies: List[str] = []
    for raw in raw_values:
        key = raw.strip()
        if not key:
            continue
        doc_id = id_map.get(key)
        if not doc_id:
            doc_id = slugify(key)
        dependencies.append(doc_id)
    return dependencies


def determine_agent(doc_id: str) -> Dict[str, str]:
    override = SPECIAL_AGENT_OVERRIDES.get(doc_id)
    if override:
        return override
    return {"agent_class": "generic"}


def determine_prompt_key(doc_id: str) -> str:
    return PROMPT_OVERRIDES.get(doc_id, f"{doc_id}{DEFAULT_PROMPT_SUFFIX}")


def transform_rows(rows: List[MutableMapping[str, str]]) -> Dict[str, Any]:
    id_map = build_document_ids(rows)
    documents: List[Dict[str, Any]] = []

    for row in rows:
        name = row[CSV_COLUMNS["name"]].strip()
        doc_id = id_map[name]

        dependencies = resolve_dependencies(
            normalize_list(row.get(CSV_COLUMNS["related_docs"], "")),
            id_map,
        )

        agent_data = determine_agent(doc_id)

        document_entry: Dict[str, Any] = {
            "id": doc_id,
            "name": name,
            "category": row.get(CSV_COLUMNS["category"], "").strip(),
            "description": row.get(CSV_COLUMNS["description"], "").strip(),
            "prompt_key": determine_prompt_key(doc_id),
            "agent_class": agent_data["agent_class"],
            "dependencies": sorted(set(dep for dep in dependencies if dep != doc_id)),
            "priority": row.get(CSV_COLUMNS["priority"], "").strip(),
            "owner": row.get(CSV_COLUMNS["owner"], "").strip(),
            "status": row.get(CSV_COLUMNS["status"], "").strip(),
            "audience": row.get(CSV_COLUMNS["audience"], "").strip(),
            "stage": {
                "label": row.get(CSV_COLUMNS["stage"], "").strip(),
                "notes": row.get(CSV_COLUMNS["stage_notes"], "").strip(),
            },
            "must_have": row.get(CSV_COLUMNS["must_have"], "").strip(),
            "usage_frequency": row.get(CSV_COLUMNS["frequency"], "").strip(),
            "notes": row.get(CSV_COLUMNS["notes"], "").strip(),
        }

        if "special_key" in agent_data:
            document_entry["special_key"] = agent_data["special_key"]

        documents.append(document_entry)

    documents.sort(key=lambda item: (item["category"], item["priority"], item["name"]))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": None,
        "documents": documents,
    }


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    input_path: Path = args.input
    output_path: Path = args.output

    if not input_path.exists():
        raise SystemExit(f"Input CSV not found: {input_path}")

    with input_path.open("r", encoding=CSV_ENCODING, newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            reader.fieldnames = [
                (name or "").strip().lstrip("\ufeff") for name in reader.fieldnames
            ]

        rows: List[MutableMapping[str, str]] = []
        for raw_row in reader:
            sanitized_row: Dict[str, str] = {}
            for key, value in raw_row.items():
                normalized_key = (key or "").strip().lstrip("\ufeff")
                if isinstance(value, str):
                    sanitized_row[normalized_key] = value.strip()
                else:
                    sanitized_row[normalized_key] = value
            rows.append(sanitized_row)

    if not rows:
        raise SystemExit("Input CSV contains no data rows.")

    payload = transform_rows(rows)
    payload["source"] = str(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])

