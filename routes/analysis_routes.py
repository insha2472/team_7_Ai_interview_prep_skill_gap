import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, Resume, JobDescription, SkillAnalysis, GeneratedProject, GeneratedRoadmap
from schemas.job_schema import JobDescriptionRequest, JobDescriptionResponse
from schemas.skill_schema import SkillAnalysisResponse
from utils.jwt_handler import get_current_user
from utils.skill_matcher import analyse_skill_gap
from utils.streak_logic import add_xp, update_streak, XP_PER_ANALYSIS

router = APIRouter(prefix="/analysis", tags=["Skill Gap Analysis"])


@router.post("/jd", response_model=JobDescriptionResponse, status_code=201)
def upload_jd(
    payload: JobDescriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a job description for the current user."""
    jd = JobDescription(
        user_id=current_user.id,
        company_name=payload.company_name,
        jd_text=payload.jd_text,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


@router.get("/skill-gap", response_model=SkillAnalysisResponse)
def get_skill_gap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compare the user's latest resume against their latest JD.
    Returns matched skills, missing skills, and match percentage.
    """
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Upload a resume first")

    jd = (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.uploaded_at.desc())
        .first()
    )
    if not jd:
        raise HTTPException(status_code=404, detail="Upload a job description first")

    result = analyse_skill_gap(resume.resume_text, jd.jd_text)

    analysis = SkillAnalysis(
        user_id=current_user.id,
        matched_skills=json.dumps(result["matched_skills"]),
        missing_skills=json.dumps(result["missing_skills"]),
        priority_skills=json.dumps(result.get("priority_skills", [])),
        match_percentage=result["match_percentage"],
    )
    db.add(analysis)
    
    # Clear old AI content so new ones are generated uniquely for this analysis
    db.query(GeneratedRoadmap).filter(GeneratedRoadmap.user_id == current_user.id).delete()
    db.query(GeneratedProject).filter(GeneratedProject.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(analysis)

    # Award XP and update streak
    add_xp(current_user, XP_PER_ANALYSIS, db)
    update_streak(current_user, db)

    return SkillAnalysisResponse(
        id=analysis.id,
        user_id=analysis.user_id,
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        priority_skills=result.get("priority_skills", []),
        match_percentage=result["match_percentage"],
    )
