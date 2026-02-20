from db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    xp_to_next = Column(Integer, default=500)
    streak = Column(Integer, default=0)
    earned_badges = Column(Text, default="[]")  # stored as JSON string
    daily_xp = Column(Text, default="{}")       # stored as JSON string {"YYYY-MM-DD": xp}
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")
    skill_analyses = relationship("SkillAnalysis", back_populates="user")
    test_results = relationship("TestResult", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    project_progress = relationship("ProjectProgress", back_populates="user")


class ProjectProgress(Base):
    __tablename__ = "project_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(String(255), nullable=False)
    completed_steps = Column(Text, default="[]")  # stored as JSON string [0, 1, 2]

    user = relationship("User", back_populates="project_progress")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(255), nullable=True)
    jd_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")


class SkillAnalysis(Base):
    __tablename__ = "skill_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    matched_skills = Column(Text, nullable=True)       # stored as JSON string
    missing_skills = Column(Text, nullable=True)        # stored as JSON string
    priority_skills = Column(Text, nullable=True)       # stored as JSON string
    match_percentage = Column(Float, default=0.0)

    user = relationship("User", back_populates="skill_analyses")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    test_type = Column(String(50), nullable=True)  # mcq, hr, coding
    score = Column(Float, default=0.0)
    taken_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_results")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed_skills = Column(Text, nullable=True)      # stored as JSON string
    total_progress_percentage = Column(Float, default=0.0)

    user = relationship("User", back_populates="progress")


class GeneratedProject(Base):
    __tablename__ = "generated_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    features = Column(Text, nullable=False)  # JSON string list
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedRoadmap(Base):
    __tablename__ = "generated_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    roadmap_data = Column(Text, nullable=False)  # Full roadmap JSON blob
    created_at = Column(DateTime, default=datetime.utcnow)
