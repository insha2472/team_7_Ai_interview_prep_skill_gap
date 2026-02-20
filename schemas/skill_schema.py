from pydantic import BaseModel
from typing import List, Optional


class SkillAnalysisResponse(BaseModel):
    id: int
    user_id: int
    matched_skills: List[str]
    missing_skills: List[str]
    priority_skills: List[str]
    match_percentage: float

    class Config:
        from_attributes = True
