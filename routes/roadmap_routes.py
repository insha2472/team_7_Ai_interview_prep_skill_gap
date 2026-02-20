import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, SkillAnalysis, GeneratedProject, GeneratedRoadmap
from utils.jwt_handler import get_current_user
from utils.roadmap_generator import generate_roadmap, generate_mini_projects

router = APIRouter(prefix="/roadmap", tags=["AI Roadmap"])


@router.get("/")
def get_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an AI-based weekly roadmap from the user's latest skill analysis.
    """
    analysis = (
        db.query(SkillAnalysis)
        .filter(SkillAnalysis.user_id == current_user.id)
        .order_by(SkillAnalysis.id.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Run a skill-gap analysis first (POST /analysis/jd then GET /analysis/skill-gap)",
        )

    missing_skills = json.loads(analysis.missing_skills) if analysis.missing_skills else []

    # Check if we already have a generated roadmap for this specific analysis session
    existing_roadmap = db.query(GeneratedRoadmap).filter(GeneratedRoadmap.user_id == current_user.id).order_by(GeneratedRoadmap.id.desc()).first()
    
    if not existing_roadmap:
        # Generate and save new unique roadmap
        roadmap_data = generate_roadmap(missing_skills)
        new_roadmap = GeneratedRoadmap(
            user_id=current_user.id,
            roadmap_data=json.dumps(roadmap_data)
        )
        db.add(new_roadmap)
        
        # Also generate and save unique mini projects
        projects_data = generate_mini_projects(missing_skills)
        for p in projects_data:
            new_project = GeneratedProject(
                user_id=current_user.id,
                title=p["title"],
                difficulty=p["difficulty"],
                description=p["description"],
                features=json.dumps(p["features"])
            )
            db.add(new_project)
        
        db.commit()
    else:
        roadmap_data = json.loads(existing_roadmap.roadmap_data)
        
        # Check if the existing roadmap is missing or has empty flashcards (Legacy/Corrupt format)
        needs_regen = False
        if isinstance(roadmap_data, list) and len(roadmap_data) > 0:
            # If the first week doesn't have flashcards or they are empty, regenerate
            if "flashcards" not in roadmap_data[0] or not roadmap_data[0]["flashcards"]:
                needs_regen = True
        
        if needs_regen:
            print(f"[Roadmap Route] Detected legacy/corrupt roadmap for user {current_user.id}. Regenerating with flashcards...")
            roadmap_data = generate_roadmap(missing_skills)
            print(f"[Roadmap Route] Generated data: {json.dumps(roadmap_data)[:100]}...") # Debug log
            existing_roadmap.roadmap_data = json.dumps(roadmap_data)
            db.commit()

    # Fetch projects for this user
    projects = db.query(GeneratedProject).filter(GeneratedProject.user_id == current_user.id).all()
    projects_list = [
        {
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "description": p.description,
            "features": json.loads(p.features)
        }
        for p in projects
    ]

    return {
        "user_id": current_user.id,
        "match_percentage": analysis.match_percentage,
        "roadmap": roadmap_data,
        "mini_projects": projects_list,
    }
