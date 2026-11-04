import os
from datetime import datetime, timezone
from pathlib import PurePosixPath
from threading import BoundedSemaphore

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select, text as sql_text
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from matching.service import AnalysisError, analyze_resume
from models import Analysis, AnalysisAttempt, DailyUsage, Job, Resume, User
from resumes.parser import MAX_UPLOAD_BYTES, extract_text

router = APIRouter(prefix="/analyses", tags=["Analyses"])
# A single worker makes at most one provider call at a time.
analysis_slot = BoundedSemaphore(1)


@router.post("", status_code=201)
def create_analysis(
    resume: UploadFile = File(...),
    job_title: str = Form(..., min_length=1, max_length=255),
    job_description: str = Form(..., min_length=80, max_length=12000),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not job_title.strip() or len(job_description.strip()) < 80:
        raise HTTPException(422, "Enter a job title and at least 80 characters of job description.")
    if not analysis_slot.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running. Please try again shortly.")
    try:
        if db.get_bind().dialect.name == "postgresql":
            # Serialize quota reservations even during overlapping cloud revisions.
            db.execute(sql_text("SELECT pg_advisory_xact_lock(42819001)"))
        day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        count = db.scalar(select(func.count()).select_from(AnalysisAttempt).where(
            AnalysisAttempt.user_id == user.id, AnalysisAttempt.created_at >= day_start,
        ))
        if count >= int(os.getenv("ANALYSES_PER_DAY", "5")):
            raise HTTPException(429, "Your daily analysis limit was reached. Try again tomorrow (UTC).")
        daily_usage = db.get(DailyUsage, day_start.date())
        global_count = daily_usage.attempts if daily_usage else 0
        if global_count >= int(os.getenv("GLOBAL_ANALYSES_PER_DAY", "20")):
            raise HTTPException(429, "The demo's daily AI allowance was reached. Try the sample analysis.")
        filename = PurePosixPath((resume.filename or "resume").replace("\\", "/")).name[:255]
        try:
            text = extract_text(filename, resume.file.read(MAX_UPLOAD_BYTES + 1))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(503, "Live analysis is not configured yet. Try the sample analysis.")
        # Reserve a provider attempt before calling out. Deleting results does not reset quota.
        user_id = user.id
        db.add(AnalysisAttempt(user_id=user_id))
        if daily_usage is None:
            db.add(DailyUsage(day=day_start.date(), attempts=1))
        else:
            daily_usage.attempts += 1
        db.commit()
        try:
            result = analyze_resume(text, job_description.strip())
        except AnalysisError as exc:
            raise HTTPException(exc.status_code, str(exc)) from exc
        resume_row = Resume(user_id=user_id, filename=filename, extracted_text=text)
        job = Job(user_id=user_id, title=job_title.strip(), description=job_description.strip())
        db.add_all([resume_row, job])
        db.flush()
        analysis = Analysis(user_id=user_id, resume_id=resume_row.id, job_id=job.id,
                            match_score=result["match_score"], result=result)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return detail(analysis)
    finally:
        analysis_slot.release()
        resume.file.close()


def detail(analysis: Analysis) -> dict:
    return {"id": analysis.id, "job_title": analysis.job.title,
            "filename": analysis.resume.filename, "created_at": analysis.created_at,
            "result": analysis.result}


@router.get("")
def list_analyses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Analysis).where(Analysis.user_id == user.id)
                      .order_by(Analysis.created_at.desc(), Analysis.id.desc()).limit(50)).all()
    return [{"id": row.id, "job_title": row.job.title, "filename": row.resume.filename,
             "match_score": row.match_score, "created_at": row.created_at} for row in rows]


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id))
    if row is None:
        raise HTTPException(404, "Analysis not found.")
    return detail(row)


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id))
    if row is None:
        raise HTTPException(404, "Analysis not found.")
    resume, job = row.resume, row.job
    db.delete(row)
    db.flush()
    db.delete(resume)
    db.delete(job)
    db.commit()
