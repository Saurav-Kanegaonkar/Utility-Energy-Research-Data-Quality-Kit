import csv
import json
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
AS_OF_DATE = date(2026, 5, 26)
RNG = random.Random(4237)


REGIONS = [
    "Northeast",
    "Midwest",
    "South",
    "Mountain",
    "Pacific",
    "Canada",
]
UTILITY_TYPES = ["electric", "gas", "dual fuel", "municipal", "cooperative"]
PROGRAM_AREAS = [
    "Residential weatherization",
    "Commercial lighting",
    "Demand response",
    "Heat pump adoption",
    "Income-qualified efficiency",
    "Transportation electrification",
    "Small business direct install",
]
CUSTOMER_CLASSES = ["residential", "commercial", "industrial", "mixed"]
DATA_TOOLS = [
    "Measure Insights",
    "DSM Benchmark",
    "Program Tracker",
    "Utility Data Exchange",
    "Research Library",
]
OWNERS = ["Analyst team", "Program research", "Data operations", "Subject matter expert"]
SOURCE_TYPES = [
    "utility filing",
    "program survey",
    "client spreadsheet",
    "web research",
    "analyst interview",
    "benchmark study",
]
FIELDS = [
    "annual_mwh_savings",
    "participant_count",
    "measure_cost",
    "incentive_amount",
    "eligibility_definition",
    "launch_date",
    "customer_segment",
]
CHECK_TYPES = [
    "missing source citation",
    "stale value",
    "unit conversion",
    "definition mismatch",
    "duplicate program row",
    "outlier versus benchmark",
]
REQUEST_TYPES = ["client question", "report update", "article support", "webinar exhibit", "data pull"]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def pick_weighted(options):
    values, weights = zip(*options)
    return RNG.choices(values, weights=weights, k=1)[0]


def generate_programs():
    programs = []
    for idx in range(1, 43):
        program_area = RNG.choice(PROGRAM_AREAS)
        customer_class = RNG.choice(CUSTOMER_CLASSES)
        last_verified = AS_OF_DATE - timedelta(days=RNG.randint(4, 124))
        baseline_records = RNG.randint(240, 4200)
        completeness = max(54, min(99, RNG.gauss(84, 9)))
        programs.append(
            {
                "program_id": f"UP{idx:03d}",
                "program_name": f"{RNG.choice(REGIONS)} {program_area}",
                "region": RNG.choice(REGIONS),
                "utility_type": RNG.choice(UTILITY_TYPES),
                "program_area": program_area,
                "customer_class": customer_class,
                "data_tool": RNG.choice(DATA_TOOLS),
                "owner": RNG.choice(OWNERS),
                "update_frequency": RNG.choice(["weekly", "monthly", "quarterly"]),
                "baseline_records": baseline_records,
                "completeness_pct": round(completeness, 1),
                "last_verified_date": last_verified.isoformat(),
                "annual_mwh_savings": RNG.randint(1800, 185000),
                "participant_count": RNG.randint(120, 72000),
            }
        )
    return programs


def generate_source_observations(programs):
    rows = []
    for idx in range(1, 721):
        program = RNG.choice(programs)
        source_type = RNG.choice(SOURCE_TYPES)
        field = RNG.choice(FIELDS)
        observation_date = AS_OF_DATE - timedelta(days=RNG.randint(0, 150))
        confidence = max(35, min(99, RNG.gauss(81, 12)))
        if source_type in {"utility filing", "benchmark study"}:
            confidence += RNG.uniform(1, 6)
        if source_type == "web research":
            confidence -= RNG.uniform(2, 9)
        value = RNG.randint(50, 250000) if field != "eligibility_definition" else RNG.choice(["all customers", "income qualified", "small business", "custom"])
        rows.append(
            {
                "observation_id": f"SRC{idx:04d}",
                "program_id": program["program_id"],
                "observation_date": observation_date.isoformat(),
                "source_type": source_type,
                "field_name": field,
                "submitted_value": value,
                "normalized_value": value,
                "confidence_score": round(max(25, min(99, confidence)), 1),
                "citation_status": pick_weighted(
                    [
                        ("complete", 78),
                        ("needs page reference", 13),
                        ("missing", 9),
                    ]
                ),
                "analyst_note": RNG.choice(
                    [
                        "ready for tool update",
                        "confirm definition before publication",
                        "compare against prior cycle",
                        "needs SME review",
                    ]
                ),
            }
        )
    return rows


def generate_quality_checks(programs):
    rows = []
    for idx in range(1, 181):
        program = RNG.choice(programs)
        severity = pick_weighted([("Critical", 13), ("High", 27), ("Medium", 42), ("Low", 18)])
        opened = AS_OF_DATE - timedelta(days=RNG.randint(0, 58))
        status = pick_weighted([("open", 52), ("in review", 24), ("resolved", 24)])
        affected = RNG.randint(3, 460)
        rows.append(
            {
                "check_id": f"QC{idx:04d}",
                "program_id": program["program_id"],
                "opened_date": opened.isoformat(),
                "check_type": RNG.choice(CHECK_TYPES),
                "severity": severity,
                "affected_records": affected,
                "status": status,
                "owner": RNG.choice(OWNERS),
                "procedure_step": RNG.choice(
                    [
                        "source citation review",
                        "unit normalization",
                        "metric definition check",
                        "duplicate detection",
                        "stakeholder signoff",
                    ]
                ),
            }
        )
    return rows


def generate_research_requests(programs):
    rows = []
    audiences = ["utility client", "internal analyst", "subject matter expert", "executive reviewer"]
    for idx in range(1, 97):
        program = RNG.choice(programs)
        due_date = AS_OF_DATE + timedelta(days=RNG.randint(-4, 30))
        request_type = RNG.choice(REQUEST_TYPES)
        rows.append(
            {
                "request_id": f"REQ{idx:04d}",
                "program_id": program["program_id"],
                "request_type": request_type,
                "due_date": due_date.isoformat(),
                "audience": RNG.choice(audiences),
                "research_question": RNG.choice(
                    [
                        "Which program records changed since the last published update?",
                        "Where do savings values diverge from peer benchmarks?",
                        "Which measures need source validation before the client call?",
                        "What caveats should be included in the written summary?",
                    ]
                ),
                "source_need": RNG.choice(
                    [
                        "primary utility filing plus benchmark comparison",
                        "client spreadsheet reconciliation",
                        "survey notes with page references",
                        "program history and participation trend",
                    ]
                ),
                "status": pick_weighted([("new", 28), ("triaged", 35), ("in progress", 25), ("ready", 12)]),
            }
        )
    return rows


def generate_tool_updates(programs):
    rows = []
    update_types = ["populate new row", "refresh stale field", "reconcile source conflict", "document definition", "publish summary"]
    blockers = ["none", "missing citation", "SME review", "conflicting sources", "late client file"]
    for idx in range(1, 137):
        program = RNG.choice(programs)
        pending = RNG.randint(4, 260)
        complete = max(42, min(100, RNG.gauss(float(program["completeness_pct"]), 8)))
        rows.append(
            {
                "update_id": f"UPD{idx:04d}",
                "program_id": program["program_id"],
                "data_tool": program["data_tool"],
                "update_type": RNG.choice(update_types),
                "records_pending": pending,
                "completeness_pct": round(complete, 1),
                "blocker": pick_weighted([(blocker, 1 if blocker != "none" else 3) for blocker in blockers]),
                "recommended_next_step": RNG.choice(
                    [
                        "update tool after citation check",
                        "send source question to owner",
                        "hold for SME review",
                        "publish with caveat",
                        "refresh benchmark comparison",
                    ]
                ),
            }
        )
    return rows


def severity_points(value):
    return {"Critical": 34, "High": 22, "Medium": 11, "Low": 4}[value]


def analyze():
    programs = read_csv(DATA_DIR / "utility_programs.csv")
    observations = read_csv(DATA_DIR / "source_observations.csv")
    checks = read_csv(DATA_DIR / "quality_checks.csv")
    requests = read_csv(DATA_DIR / "research_requests.csv")
    updates = read_csv(DATA_DIR / "data_tool_updates.csv")

    program_lookup = {row["program_id"]: row for row in programs}
    check_rollup = defaultdict(lambda: {"open_checks": 0, "severity_score": 0, "affected_records": 0})
    for row in checks:
        if row["status"] != "resolved":
            item = check_rollup[row["program_id"]]
            item["open_checks"] += 1
            item["severity_score"] += severity_points(row["severity"])
            item["affected_records"] += int(row["affected_records"])

    source_rollup = defaultdict(lambda: {"rows": 0, "confidence": 0.0, "missing_citations": 0})
    for row in observations:
        item = source_rollup[row["program_id"]]
        item["rows"] += 1
        item["confidence"] += float(row["confidence_score"])
        if row["citation_status"] != "complete":
            item["missing_citations"] += 1

    update_rollup = defaultdict(lambda: {"pending": 0, "rows": 0, "blockers": 0, "completeness": 0.0})
    for row in updates:
        item = update_rollup[row["program_id"]]
        item["pending"] += int(row["records_pending"])
        item["rows"] += 1
        item["completeness"] += float(row["completeness_pct"])
        if row["blocker"] != "none":
            item["blockers"] += 1

    queue = []
    for program in programs:
        pid = program["program_id"]
        last_verified = datetime.strptime(program["last_verified_date"], "%Y-%m-%d").date()
        stale_days = (AS_OF_DATE - last_verified).days
        sources = source_rollup[pid]
        checks_for_program = check_rollup[pid]
        update = update_rollup[pid]
        confidence = sources["confidence"] / sources["rows"] if sources["rows"] else 75
        update_completeness = update["completeness"] / update["rows"] if update["rows"] else float(program["completeness_pct"])
        priority = (
            (100 - update_completeness) * 0.8
            + min(stale_days, 120) * 0.22
            + checks_for_program["severity_score"] * 0.55
            + update["blockers"] * 4.5
            + sources["missing_citations"] * 1.4
            + max(0, 82 - confidence) * 0.65
        )
        queue.append(
            {
                "program_id": pid,
                "program_name": program["program_name"],
                "program_area": program["program_area"],
                "data_tool": program["data_tool"],
                "priority_score": round(priority, 1),
                "open_checks": checks_for_program["open_checks"],
                "affected_records": checks_for_program["affected_records"],
                "pending_updates": update["pending"],
                "source_rows": sources["rows"],
                "missing_citations": sources["missing_citations"],
                "avg_confidence_score": round(confidence, 1),
                "last_verified_date": program["last_verified_date"],
                "recommended_action": recommend_action(stale_days, checks_for_program, update, confidence),
            }
        )
    queue.sort(key=lambda row: row["priority_score"], reverse=True)

    request_rows = []
    for row in requests:
        program = program_lookup[row["program_id"]]
        due = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
        days_to_due = (due - AS_OF_DATE).days
        quality = next(item for item in queue if item["program_id"] == row["program_id"])
        triage_score = quality["priority_score"] * 0.55 + max(0, 18 - days_to_due) * 3.2
        request_rows.append(
            {
                "request_id": row["request_id"],
                "program_id": row["program_id"],
                "program_area": program["program_area"],
                "request_type": row["request_type"],
                "audience": row["audience"],
                "due_date": row["due_date"],
                "triage_score": round(triage_score, 1),
                "source_need": row["source_need"],
                "status": row["status"],
                "recommended_response": response_guidance(row["request_type"], quality),
            }
        )
    request_rows.sort(key=lambda row: row["triage_score"], reverse=True)

    tool_plan = []
    for row in updates:
        quality = next(item for item in queue if item["program_id"] == row["program_id"])
        tool_plan.append(
            {
                "update_id": row["update_id"],
                "program_id": row["program_id"],
                "data_tool": row["data_tool"],
                "update_type": row["update_type"],
                "records_pending": row["records_pending"],
                "completeness_pct": row["completeness_pct"],
                "blocker": row["blocker"],
                "priority_score": quality["priority_score"],
                "recommended_next_step": row["recommended_next_step"],
            }
        )
    tool_plan.sort(key=lambda row: (float(row["priority_score"]), int(row["records_pending"])), reverse=True)

    brief_pack = []
    for row in queue[:18]:
        brief_pack.append(
            {
                "program_id": row["program_id"],
                "headline": f"{row['program_area']} needs {row['recommended_action'].lower()}",
                "evidence": f"{row['open_checks']} open checks, {row['missing_citations']} source gaps, {row['pending_updates']} pending tool rows",
                "stakeholder_summary": f"Focus the next update on {row['data_tool']} records where source confidence is {row['avg_confidence_score']} and the last verification date is {row['last_verified_date']}.",
                "visual_note": "Show open checks, pending updates, and citation gaps together so nontechnical reviewers can see why the queue rank changed.",
            }
        )

    write_csv(
        OUTPUT_DIR / "program_quality_queue.csv",
        queue,
        [
            "program_id",
            "program_name",
            "program_area",
            "data_tool",
            "priority_score",
            "open_checks",
            "affected_records",
            "pending_updates",
            "source_rows",
            "missing_citations",
            "avg_confidence_score",
            "last_verified_date",
            "recommended_action",
        ],
    )
    write_csv(
        OUTPUT_DIR / "research_request_triage.csv",
        request_rows,
        [
            "request_id",
            "program_id",
            "program_area",
            "request_type",
            "audience",
            "due_date",
            "triage_score",
            "source_need",
            "status",
            "recommended_response",
        ],
    )
    write_csv(
        OUTPUT_DIR / "tool_update_plan.csv",
        tool_plan,
        [
            "update_id",
            "program_id",
            "data_tool",
            "update_type",
            "records_pending",
            "completeness_pct",
            "blocker",
            "priority_score",
            "recommended_next_step",
        ],
    )
    write_csv(
        OUTPUT_DIR / "stakeholder_brief_pack.csv",
        brief_pack,
        ["program_id", "headline", "evidence", "stakeholder_summary", "visual_note"],
    )

    app_payload = {
        "generated_at": AS_OF_DATE.isoformat(),
        "summary": {
            "programs": len(programs),
            "source_observations": len(observations),
            "open_quality_checks": sum(1 for row in checks if row["status"] != "resolved"),
            "research_requests": len(requests),
            "pending_tool_rows": sum(int(row["records_pending"]) for row in updates),
            "avg_source_confidence": round(sum(float(row["confidence_score"]) for row in observations) / len(observations), 1),
            "citation_gap_rows": sum(1 for row in observations if row["citation_status"] != "complete"),
        },
        "qualityQueue": queue[:14],
        "requestTriage": request_rows[:14],
        "toolPlan": tool_plan[:16],
        "briefPack": brief_pack[:10],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "app_payload.json").write_text(json.dumps(app_payload, indent=2))
    return app_payload


def recommend_action(stale_days, checks_for_program, update, confidence):
    if checks_for_program["severity_score"] >= 70:
        return "Escalate source QA"
    if update["blockers"] >= 3:
        return "Resolve update blockers"
    if stale_days >= 75:
        return "Refresh stale fields"
    if confidence < 74:
        return "Validate citations"
    return "Publish with caveat"


def response_guidance(request_type, quality):
    if request_type in {"report update", "webinar exhibit"} and quality["missing_citations"] > 5:
        return "Draft summary after citation cleanup"
    if quality["open_checks"] >= 5:
        return "Answer with QA caveat and owner follow-up"
    if request_type == "client question":
        return "Send concise finding with source note"
    return "Prepare analyst-ready evidence pack"


def generate_all():
    programs = generate_programs()
    observations = generate_source_observations(programs)
    checks = generate_quality_checks(programs)
    requests = generate_research_requests(programs)
    updates = generate_tool_updates(programs)

    write_csv(
        DATA_DIR / "utility_programs.csv",
        programs,
        [
            "program_id",
            "program_name",
            "region",
            "utility_type",
            "program_area",
            "customer_class",
            "data_tool",
            "owner",
            "update_frequency",
            "baseline_records",
            "completeness_pct",
            "last_verified_date",
            "annual_mwh_savings",
            "participant_count",
        ],
    )
    write_csv(
        DATA_DIR / "source_observations.csv",
        observations,
        [
            "observation_id",
            "program_id",
            "observation_date",
            "source_type",
            "field_name",
            "submitted_value",
            "normalized_value",
            "confidence_score",
            "citation_status",
            "analyst_note",
        ],
    )
    write_csv(
        DATA_DIR / "quality_checks.csv",
        checks,
        [
            "check_id",
            "program_id",
            "opened_date",
            "check_type",
            "severity",
            "affected_records",
            "status",
            "owner",
            "procedure_step",
        ],
    )
    write_csv(
        DATA_DIR / "research_requests.csv",
        requests,
        [
            "request_id",
            "program_id",
            "request_type",
            "due_date",
            "audience",
            "research_question",
            "source_need",
            "status",
        ],
    )
    write_csv(
        DATA_DIR / "data_tool_updates.csv",
        updates,
        [
            "update_id",
            "program_id",
            "data_tool",
            "update_type",
            "records_pending",
            "completeness_pct",
            "blocker",
            "recommended_next_step",
        ],
    )


if __name__ == "__main__":
    generate_all()
    payload = analyze()
    top = payload["qualityQueue"][0]
    print(
        f"{top['program_id']}: priority_score={top['priority_score']}, "
        f"open_checks={top['open_checks']}, pending_updates={top['pending_updates']}, "
        f"action={top['recommended_action']}"
    )
