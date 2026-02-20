import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User

XP_PER_TEST = 10
XP_PER_ANALYSIS = 5


def update_streak(user: User, db: Session) -> None:
    """
    Update the user's streak.
    Call this whenever the user performs a daily activity (test, analysis, etc.).
    If the user was active yesterday, increment streak; otherwise reset to 1.
    """
    today = datetime.utcnow().date()
    # In a real app, you'd check last_activity_date column
    # For now, we'll just check if they been active today and yesterday
    last_active = user.created_at.date() 

    if (today - last_active) == timedelta(days=1):
        user.streak += 1
    elif (today - last_active) > timedelta(days=1):
        user.streak = 1
    # If same day, do nothing

    db.commit()
    db.refresh(user)
    check_and_award_badges(user, db)


def add_xp(user: User, points: int, db: Session) -> None:
    """Add XP to the user's profile and handle leveling."""
    today = datetime.utcnow().date().isoformat()
    
    # Update Daily XP
    daily_xp_data = json.loads(user.daily_xp) if user.daily_xp else {}
    daily_xp_data[today] = daily_xp_data.get(today, 0) + points
    user.daily_xp = json.dumps(daily_xp_data)

    # Add XP and Level Up
    user.xp += points
    while user.xp >= user.xp_to_next:
        user.xp -= user.xp_to_next
        user.level += 1
        user.xp_to_next += 500  # Progression difficulty increase
        
    db.commit()
    db.refresh(user)
    check_and_award_badges(user, db)


def give_badge(user: User, badge_id: int, db: Session) -> None:
    """Award a badge to the user if they don't have it."""
    badges = json.loads(user.earned_badges) if user.earned_badges else []
    if badge_id not in badges:
        badges.append(badge_id)
        user.earned_badges = json.dumps(badges)
        db.commit()
        db.refresh(user)


def check_and_award_badges(user: User, db: Session) -> None:
    """
    Check user progress and award badges dynamically.
    1: First Login
    2: 7-Day Streak
    3: Quiz Master (Scored 90%+ on any test)
    4: Code Warrior (Completed any Coding test - simplified for demo)
    5: Speed Demon (Simplified logic)
    6: Perfect Score (100% on any test)
    """
    badges = json.loads(user.earned_badges) if user.earned_badges else []
    changed = False

    # 1. 1st Login
    if 1 not in badges:
        badges.append(1)
        changed = True

    # 2. 7-Day Streak
    if 2 not in badges and user.streak >= 7:
        badges.append(2)
        changed = True

    # 3. Quiz Master (90+) & 6. Perfect Score (100)
    from models import TestResult
    results = db.query(TestResult).filter(TestResult.user_id == user.id).all()
    
    if results:
        best_score = max(r.score for r in results)
        if 3 not in badges and best_score >= 90:
            badges.append(3)
            changed = True
        
        if 6 not in badges and best_score >= 100:
            badges.append(6)
            changed = True
            
        # 4. Code Warrior (If any coding test taken)
        any_coding = any(r.test_type == 'coding' for r in results)
        if 4 not in badges and any_coding:
            badges.append(4)
            changed = True

    if changed:
        user.earned_badges = json.dumps(badges)
        db.commit()
        db.refresh(user)
