#!/usr/bin/env python3
"""Evaluation harness for OPAL Orchestrator.

This script runs test cases against the planner and evaluates:
1. % of steps with citations
2. # unique labs recommended
3. # capabilities retrieved (>= K threshold)
4. Plan structure validity
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.models.database import async_session_maker, init_db
from app.services.planner import get_planner_service


async def run_test_case(test_case: dict) -> dict:
    """Run a single test case and return results."""
    print(f"  Running: {test_case['name']}...")

    async with async_session_maker() as session:
        planner = get_planner_service(session)

        try:
            plan = await planner.generate_plan(
                goal=test_case["description"],
                context=None,
                constraints=None,
            )

            # Analyze results
            total_steps = len(plan.steps)
            steps_with_citations = sum(
                1 for step in plan.steps if len(step.citations) > 0
            )
            citation_rate = steps_with_citations / total_steps if total_steps > 0 else 0

            # Count unique facilities/labs
            unique_facilities = set()
            for step in plan.steps:
                if step.recommended_facility:
                    unique_facilities.add(step.recommended_facility.lower())

            # Count hypotheses
            hypothesis_steps = sum(1 for step in plan.steps if step.is_hypothesis)

            result = {
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "success": True,
                "plan_generated": True,
                "metrics": {
                    "total_steps": total_steps,
                    "steps_with_citations": steps_with_citations,
                    "citation_rate": citation_rate,
                    "unique_facilities": len(unique_facilities),
                    "hypothesis_steps": hypothesis_steps,
                    "meets_min_labs": len(unique_facilities) >= test_case.get("expected_min_labs", 1),
                    "meets_min_steps": total_steps >= test_case.get("expected_min_steps", 1),
                },
                "plan": {
                    "goal_summary": plan.goal_summary,
                    "assumptions": plan.assumptions,
                    "steps": [
                        {
                            "step_id": s.step_id,
                            "objective": s.objective,
                            "facility": s.recommended_facility,
                            "has_citations": len(s.citations) > 0,
                            "is_hypothesis": s.is_hypothesis,
                        }
                        for s in plan.steps
                    ],
                    "open_questions": plan.open_questions,
                    "risks_count": len(plan.risks_and_alternatives),
                },
                "error": None,
            }

        except Exception as e:
            result = {
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "success": False,
                "plan_generated": False,
                "metrics": None,
                "plan": None,
                "error": str(e),
            }

    return result


async def run_evaluation(test_cases_path: Path, output_dir: Path) -> dict:
    """Run all test cases and generate reports."""
    # Load test cases
    with open(test_cases_path) as f:
        data = json.load(f)
        test_cases = data["test_cases"]

    print(f"Running {len(test_cases)} test cases...")

    # Initialize database
    await init_db()

    # Run test cases
    results = []
    for test_case in test_cases:
        result = await run_test_case(test_case)
        results.append(result)

    # Calculate aggregate metrics
    successful = [r for r in results if r["success"]]
    total_citation_rate = (
        sum(r["metrics"]["citation_rate"] for r in successful) / len(successful)
        if successful
        else 0
    )
    avg_steps = (
        sum(r["metrics"]["total_steps"] for r in successful) / len(successful)
        if successful
        else 0
    )
    avg_facilities = (
        sum(r["metrics"]["unique_facilities"] for r in successful) / len(successful)
        if successful
        else 0
    )
    meets_lab_threshold = (
        sum(1 for r in successful if r["metrics"]["meets_min_labs"]) / len(successful)
        if successful
        else 0
    )
    meets_step_threshold = (
        sum(1 for r in successful if r["metrics"]["meets_min_steps"]) / len(successful)
        if successful
        else 0
    )

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_test_cases": len(test_cases),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "aggregate_metrics": {
            "avg_citation_rate": total_citation_rate,
            "avg_steps_per_plan": avg_steps,
            "avg_unique_facilities": avg_facilities,
            "pct_meets_min_labs": meets_lab_threshold,
            "pct_meets_min_steps": meets_step_threshold,
        },
        "results": results,
    }

    # Write JSON report
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "eval_report.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"JSON report written to: {json_path}")

    # Write Markdown report
    md_report = generate_markdown_report(report)
    md_path = output_dir / "eval_report.md"
    with open(md_path, "w") as f:
        f.write(md_report)
    print(f"Markdown report written to: {md_path}")

    return report


def generate_markdown_report(report: dict) -> str:
    """Generate a human-readable markdown report."""
    md = f"""# OPAL Orchestrator Evaluation Report

**Generated:** {report['timestamp']}

## Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | {report['total_test_cases']} |
| Successful | {report['successful']} |
| Failed | {report['failed']} |

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Average Citation Rate | {report['aggregate_metrics']['avg_citation_rate']:.1%} |
| Average Steps per Plan | {report['aggregate_metrics']['avg_steps_per_plan']:.1f} |
| Average Unique Facilities | {report['aggregate_metrics']['avg_unique_facilities']:.1f} |
| % Meeting Lab Threshold | {report['aggregate_metrics']['pct_meets_min_labs']:.1%} |
| % Meeting Step Threshold | {report['aggregate_metrics']['pct_meets_min_steps']:.1%} |

## Individual Test Results

"""

    for result in report["results"]:
        status = "PASS" if result["success"] else "FAIL"
        md += f"### {result['test_case_name']} [{status}]\n\n"

        if result["success"]:
            metrics = result["metrics"]
            md += f"- **Steps:** {metrics['total_steps']}\n"
            md += f"- **Citation Rate:** {metrics['citation_rate']:.1%}\n"
            md += f"- **Unique Facilities:** {metrics['unique_facilities']}\n"
            md += f"- **Hypothesis Steps:** {metrics['hypothesis_steps']}\n"

            if result["plan"]:
                md += f"\n**Goal Summary:** {result['plan']['goal_summary']}\n\n"
                md += "**Steps:**\n"
                for step in result["plan"]["steps"]:
                    citation_mark = "[cited]" if step["has_citations"] else "[hypothesis]"
                    md += f"1. {step['objective']} @ {step['facility']} {citation_mark}\n"
                md += "\n"
        else:
            md += f"**Error:** {result['error']}\n\n"

    return md


def main():
    parser = argparse.ArgumentParser(
        description="Run OPAL Orchestrator evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test-cases",
        type=Path,
        default=Path(__file__).parent / "test_cases.json",
        help="Path to test cases JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "eval_output",
        help="Output directory for reports",
    )

    args = parser.parse_args()

    if not args.test_cases.exists():
        print(f"Error: Test cases file not found: {args.test_cases}")
        return 1

    report = asyncio.run(run_evaluation(args.test_cases, args.output_dir))

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total: {report['total_test_cases']}, Pass: {report['successful']}, Fail: {report['failed']}")
    print(f"Avg Citation Rate: {report['aggregate_metrics']['avg_citation_rate']:.1%}")
    print(f"Avg Steps: {report['aggregate_metrics']['avg_steps_per_plan']:.1f}")
    print(f"Avg Facilities: {report['aggregate_metrics']['avg_unique_facilities']:.1f}")

    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
