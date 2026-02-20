import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, Progress
from schemas.progress_schema import ProgressUpdate, ProgressResponse
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

@router.get("/", response_model=ProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch current user progress."""
    progress = db.query(Progress).filter(Progress.user_id == current_user.id).first()
    if not progress:
        # Initialize progress if doesn't exist
        progress = Progress(user_id=current_user.id, completed_skills="[]", total_progress_percentage=0.0)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return {
        "user_id": progress.user_id,
        "completed_skills": json.loads(progress.completed_skills),
        "total_progress_percentage": progress.total_progress_percentage
    }

@router.patch("/update", response_model=ProgressResponse)
def update_progress(
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's completed skills and calculate progress."""
    progress = db.query(Progress).filter(Progress.user_id == current_user.id).first()
    if not progress:
        progress = Progress(user_id=current_user.id)
        db.add(progress)

    progress.completed_skills = json.dumps(payload.completed_skills)
    
    # Calculate progress percentage based on the roadmap length
    try:
        from models import GeneratedRoadmap
        roadmap = db.query(GeneratedRoadmap).filter(GeneratedRoadmap.user_id == current_user.id).order_by(GeneratedRoadmap.id.desc()).first()
        if roadmap:
            roadmap_data = json.loads(roadmap.roadmap_data)
            total_skills = 0
            for week in roadmap_data:
                total_skills += len(week.get("skills", []))
            
            if total_skills > 0:
                progress.total_progress_percentage = round((len(payload.completed_skills) / total_skills) * 100, 2)
            else:
                progress.total_progress_percentage = 0.0
    except Exception as e:
        print(f"[Progress Route] Error calculating percentage: {e}")

    db.commit()
    db.refresh(progress)

    return {
        "user_id": progress.user_id,
        "completed_skills": json.loads(progress.completed_skills),
        "total_progress_percentage": progress.total_progress_percentage
    }
