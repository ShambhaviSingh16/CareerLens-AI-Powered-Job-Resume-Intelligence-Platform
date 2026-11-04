"""Explicit retention cleanup; preview counts by default. Never runs on app startup."""
import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from database import SessionLocal
from models import Analysis, AnalysisAttempt, DailyUsage, Job, Resume


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older-than-days", type=int, default=30)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.older_than_days < 1:
        parser.error("Retention must be at least one day")
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.older_than_days)
    with SessionLocal() as db:
        rows = db.scalars(select(Analysis).where(Analysis.created_at < cutoff)).all()
        print(f"{len(rows)} analyses older than {args.older_than_days} days. " + ("Applying cleanup." if args.apply else "Preview only; use --apply to delete."))
        if not args.apply:
            return
        resume_ids, job_ids = [row.resume_id for row in rows], [row.job_id for row in rows]
        db.execute(delete(Analysis).where(Analysis.created_at < cutoff).execution_options(synchronize_session=False))
        # Do not delete a document that is still referenced by a retained analysis.
        db.execute(delete(Resume).where(Resume.id.in_(resume_ids), ~Resume.id.in_(select(Analysis.resume_id))).execution_options(synchronize_session=False))
        db.execute(delete(Job).where(Job.id.in_(job_ids), ~Job.id.in_(select(Analysis.job_id))).execution_options(synchronize_session=False))
        db.execute(delete(AnalysisAttempt).where(AnalysisAttempt.created_at < cutoff).execution_options(synchronize_session=False))
        db.execute(delete(DailyUsage).where(DailyUsage.day < cutoff.date()).execution_options(synchronize_session=False))
        db.commit()


if __name__ == "__main__":
    main()
