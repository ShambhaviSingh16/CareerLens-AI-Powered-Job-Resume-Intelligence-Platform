"""Run a transparent keyword baseline, replay saved predictions, or explicitly opt into live Groq calls."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from dotenv import load_dotenv

from evaluation.dataset import CASES
from evaluation.metrics import measure, score
from matching.prompts import PROMPT_VERSION, prompt_hash
from matching.service import AnalysisError, analyze_resume, normalize


def baseline(case):
    # Oracle requirement extraction: isolates keyword matching, NOT end-to-end extraction quality.
    skills = [{"requirement_quote": expected["requirement_quote"], "required": expected["required"],
               "status": "strong" if normalize(expected["keyword"]) in normalize(case["resume"]) else "missing"}
              for expected in case["expected"]]
    return {"skills": skills, "match_score": score(skills)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "replay", "live"), default="baseline")
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--output", type=Path, default=Path("evaluation/results/latest.json"))
    parser.add_argument("--max-cases", type=int, default=len(CASES))
    parser.add_argument("--confirm-free-plan", action="store_true")
    parser.add_argument("--delay", type=float, default=15, help="Seconds between live calls; no automatic retries.")
    args = parser.parse_args()
    if not 1 <= args.max_cases <= len(CASES) or args.delay < 0:
        parser.error("max-cases or delay is outside the supported range")
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    if args.mode == "live" and (not args.confirm_free_plan or not os.getenv("GROQ_API_KEY")):
        parser.error("Live mode requires GROQ_API_KEY and --confirm-free-plan. Verify your account is on the Free plan.")
    cases = CASES[:args.max_cases]
    if args.mode == "replay":
        if not args.predictions:
            parser.error("--predictions is required for replay")
        saved = json.loads(args.predictions.read_text(encoding="utf-8"))
        predictions = saved.get("predictions", saved)
    else:
        predictions = {}
        for index, case in enumerate(cases):
            if args.mode == "baseline":
                predictions[case["id"]] = baseline(case)
                continue
            if index:
                time.sleep(args.delay)
            try:
                predictions[case["id"]] = analyze_resume(case["resume"], case["job"])
            except AnalysisError as exc:
                predictions[case["id"]] = {"error": str(exc), "status_code": exc.status_code}
                # Do not spend remaining requests when the provider is unavailable or rate-limited.
                if exc.status_code in (429, 503):
                    break
    report = {"mode": args.mode, "dataset_version": "1.0", "prompt_version": PROMPT_VERSION,
              "prompt_hash": prompt_hash(), "created_at": datetime.now(timezone.utc).isoformat(),
              "model": os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b") if args.mode == "live" else None,
              "metrics": measure(cases, predictions), "predictions": predictions,
              "limitations": "Small synthetic challenge set; manual labels need independent review. Baseline has oracle requirement extraction. No claim about hiring outcomes or general accuracy."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2))
    print(f"Saved {args.mode} report to {args.output}. This is not a live-model benchmark unless mode=live.")
    return 1 if args.mode == "live" and report["metrics"]["rejected_cases"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
