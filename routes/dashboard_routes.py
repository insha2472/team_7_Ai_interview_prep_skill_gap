import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User, SkillAnalysis, Progress, TestResult
from schemas.dashboard_schema import DashboardResponse
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def safe_json_load(data, default):
    if not data:
        return default
    try:
        return json.loads(data)
    except Exception:
        return default

@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a summary dashboard for the current user."""
    print(f"DEBUG: Entering get_dashboard for user: {current_user.email}")
    try:
        # Latest skill analysis
        analysis = (
            db.query(SkillAnalysis)
            .filter(SkillAnalysis.user_id == current_user.id)
            .order_by(SkillAnalysis.id.desc())
            .first()
        )
        print("DEBUG: analysis fetched")

        matched_skills = safe_json_load(analysis.matched_skills if analysis else None, [])
        missing_skills = safe_json_load(analysis.missing_skills if analysis else None, [])
        match_percentage = analysis.match_percentage if analysis else 0.0

        # Latest progress
        progress = (
            db.query(Progress)
            .filter(Progress.user_id == current_user.id)
            .order_by(Progress.id.desc())
            .first()
        )
        print("DEBUG: progress fetched")
        completed_skills = safe_json_load(progress.completed_skills if progress else None, [])
        total_progress = progress.total_progress_percentage if progress else 0.0

        # Recent test scores (last 10)
        recent_tests = (
            db.query(TestResult)
            .filter(TestResult.user_id == current_user.id)
            .order_by(TestResult.taken_at.desc())
            .limit(10)
            .all()
        )
        print("DEBUG: test results fetched")
        recent_test_scores = []
        for t in recent_tests:
            recent_test_scores.append({
                "skill_name": t.skill_name or "General", 
                "test_type": getattr(t, 'test_type', 'mcq') or 'mcq', 
                "score": t.score or 0.0, 
                "taken_at": str(t.taken_at)
            })

        print("DEBUG: mapping response")
        return DashboardResponse(
            user_name=current_user.name or "User",
            email=current_user.email or "",
            xp=int(current_user.xp or 0),
            level=int(current_user.level or 1),
            xp_to_next=int(current_user.xp_to_next or 500),
            streak=int(current_user.streak or 0),
            match_percentage=float(match_percentage or 0.0),
            matched_skills=matched_skills if isinstance(matched_skills, list) else [],
            missing_skills=missing_skills if isinstance(missing_skills, list) else [],
            total_progress_percentage=float(total_progress or 0.0),
            completed_skills=completed_skills if isinstance(completed_skills, list) else [],
            recent_test_scores=recent_test_scores,
            earned_badges=safe_json_load(current_user.earned_badges, []),
            daily_xp=safe_json_load(current_user.daily_xp, {}),
            project_progress=[
                {
                    "project_id": p.project_id, 
                    "completed_steps": safe_json_load(p.completed_steps, [])
                }
                for p in (current_user.project_progress or [])
            ]
        )
    except Exception as e:
        print(f"CRITICAL DASHBOARD ERROR: {e}")
        import traceback
        traceback.print_exc()
        # ABSOLUTE FALLBACK - guarantee a valid Pydantic model response
        return DashboardResponse(
            user_name=getattr(current_user, 'name', 'User') or "User",
            email=getattr(current_user, 'email', '') or "",
            xp=int(getattr(current_user, 'xp', 0) or 0),
            level=int(getattr(current_user, 'level', 1) or 1),
            xp_to_next=int(getattr(current_user, 'xp_to_next', 500) or 500),
            streak=int(getattr(current_user, 'streak', 0) or 0),
        )
