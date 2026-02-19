"""
Central AI Agent — powered by Google Gemini.

Provides four capabilities:
  1. ai_analyse_skill_gap   → compare resume vs JD using AI
  2. ai_generate_test       → generate MCQ questions for any skill
  3. ai_generate_roadmap    → create a personalised weekly learning roadmap
  4. ai_interview_coach     → context-aware mock interview / mentor chat
"""

import os
import json
from google import genai
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

# ── Gemini setup ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_ID = "gemini-2.0-flash"


def _ask_gemini_json(prompt: str) -> dict | list:
    """Send a prompt to Gemini and parse the response as JSON."""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
    )
    text = response.text.strip()

    # Strip markdown code fences if Gemini wraps JSON in ```json ... ```
    if text.startswith("```"):
        # Remove first line (```json) and last line (```)
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()

    return json.loads(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. AI SKILL-GAP ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_analyse_skill_gap(resume_text: str, jd_text: str) -> Dict:
    """
    Use Gemini to extract skills from resume & JD, compare them,
    and return matched_skills, missing_skills, and match_percentage.
    """
    prompt = f"""You are an expert HR analyst and technical recruiter.

TASK: Compare the candidate's resume against the job description below.
1. Extract ALL technical and soft skills from the RESUME.
2. Extract ALL required skills from the JOB DESCRIPTION.
3. Find which JD skills the candidate HAS (matched) and which are MISSING.
4. Calculate match_percentage = (matched / total_jd_skills) * 100, rounded to 2 decimals.

RESUME:
\"\"\"
{resume_text}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{jd_text}
\"\"\"

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "match_percentage": 65.0
}}
"""
    try:
        result = _ask_gemini_json(prompt)
        # Ensure required keys exist with defaults
        return {
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "match_percentage": float(result.get("match_percentage", 0.0)),
        }
    except Exception as e:
        print(f"[AI Agent] Skill analysis error: {e}")
        # Fallback — return empty result rather than crashing
        return {
            "matched_skills": [],
            "missing_skills": [],
            "match_percentage": 0.0,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. AI TEST QUESTION GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_generate_test(skill_name: str, num_questions: int = 5) -> List[Dict]:
    """
    Use Gemini to generate interview-style MCQ questions for any skill.
    Returns a list of question dicts with question, options, correct_answer, explanation.
    """
    prompt = f"""You are an expert technical interviewer.

TASK: Generate EXACTLY {num_questions} multiple-choice interview questions for the skill: "{skill_name}".

STRICT RULES:
- You MUST return EXACTLY {num_questions} question objects in the JSON array
- Each question MUST have exactly 4 options (A, B, C, D)
- Include a mix of easy, medium, and hard questions
- Questions should be real interview-style questions
- correct_answer MUST be one of the 4 options (exact match)
- Do NOT include the answer in the question text
- Provide a brief 1-line explanation

Return ONLY a valid JSON array (no markdown, no extra text):
[
  {{
    "question": "What is ...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief reason"
  }},
  ... ({num_questions} total)
]"""
    try:
        result = _ask_gemini_json(prompt)
        if isinstance(result, list) and len(result) >= 1:
            return result[:num_questions]
        return _fallback_questions(skill_name, num_questions)
    except Exception as e:
        print(f"[AI Agent] Test generation error: {e}")
        return _fallback_questions(skill_name, num_questions)


def _fallback_questions(skill_name: str, count: int) -> List[Dict]:
    """Return basic fallback questions if AI fails."""
    base = [
        {"question": f"What is the most fundamental concept in {skill_name}?",
         "options": ["Core fundamentals", "Advanced patterns", "Syntax only", "None of the above"],
         "correct_answer": "Core fundamentals",
         "explanation": "Understanding fundamentals is the foundation of any skill."},
        {"question": f"Which approach is best for learning {skill_name}?",
         "options": ["Practice-based learning", "Only reading docs", "Watching videos only", "Memorisation"],
         "correct_answer": "Practice-based learning",
         "explanation": "Hands-on practice is the most effective learning method."},
        {"question": f"How should you stay updated with {skill_name}?",
         "options": ["Follow official docs and community", "Ignore updates", "Only use old versions", "Avoid forums"],
         "correct_answer": "Follow official docs and community",
         "explanation": "Official docs and community forums are the best sources."},
        {"question": f"What is most important when applying {skill_name} in a project?",
         "options": ["Understanding the problem first", "Writing code immediately", "Copying from internet", "Skipping tests"],
         "correct_answer": "Understanding the problem first",
         "explanation": "Problem understanding leads to better solutions."},
        {"question": f"What helps most in a {skill_name} interview?",
         "options": ["Explaining your thought process", "Memorising answers", "Speed coding", "Guessing"],
         "correct_answer": "Explaining your thought process",
         "explanation": "Interviewers value clear thinking over just the right answer."},
    ]
    return base[:count]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. AI ROADMAP GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_generate_roadmap(missing_skills: List[str], total_weeks: int = 4) -> List[Dict]:
    """
    Use Gemini to create a personalised weekly learning roadmap
    for the given missing skills.
    """
    if not missing_skills:
        return [{
            "week": 1,
            "title": "You're all set!",
            "skills": [],
            "notes": "Your resume already covers the JD requirements. Keep practising!",
            "resources": [],
        }]

    skills_str = ", ".join(missing_skills)
    prompt = f"""You are an expert career coach and learning strategist.

TASK: Create a detailed {total_weeks}-week learning roadmap for a job candidate who needs to learn these skills: {skills_str}

STRICT RULE: Every time you are asked, generate a UNIQUE and fresh roadmap. Do not repeat previous templates exactly.
Requirements:
- Distribute skills logically across {total_weeks} weeks (related skills close together)
- For each week provide: a title, the skills to focus on, detailed study notes/action items, and real learning resources (URLs)
- Resources should be real, well-known websites (official docs, freeCodeCamp, Coursera, YouTube channels, GeeksforGeeks, etc.)
- Notes should include specific topics to cover, projects to build, and practice exercises
- Order from foundational skills to advanced ones
- Ensure the advice is tailored specifically to these skills.

Return ONLY valid JSON in this exact format (no markdown, no explanation):
[
  {{
    "week": 1,
    "title": "Week 1: Foundations of ...",
    "skills": ["skill1", "skill2"],
    "notes": "Detailed study plan and action items for this week...",
    "resources": [
      {{"skill": "skill1", "url": "https://..."}},
      {{"skill": "skill2", "url": "https://..."}}
    ]
  }}
]
"""
    try:
        result = _ask_gemini_json(prompt)
        if isinstance(result, list):
            return result
        return []
    except Exception as e:
        print(f"[AI Agent] Roadmap generation error: {e}")
        # Fallback — basic roadmap
        return [{
            "week": 1,
            "title": f"Week 1: Start Learning {', '.join(missing_skills[:3])}",
            "skills": missing_skills,
            "notes": f"Focus on learning: {skills_str}. Start with official documentation.",
            "resources": [
                {"skill": s, "url": f"https://www.google.com/search?q=learn+{s.replace(' ', '+')}"}
                for s in missing_skills
            ],
        }]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3.1 AI PROJECT GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_generate_projects(missing_skills: List[str], count: int = 2) -> List[Dict]:
    """
    Use Gemini to create unique, hands-on mini projects for the given skills.
    """
    if not missing_skills:
        return []

    skills_str = ", ".join(missing_skills)
    prompt = f"""You are a technical project mentor.
    
TASK: Generate {count} unique mini-project ideas that specifically help a candidate learn these skills: {skills_str}.

STRICT RULES:
- Each project must be UNIQUE and practical.
- Provide a catchy title, difficulty level (Easy/Medium/Hard), a brief description, and 3-4 key technical features to implement.
- Each project should be achievable in 3-7 days.
- Tailor projects specifically to the combination of skills provided.

Return ONLY valid JSON in this format (no markdown):
[
  {{
    "title": "Project Title",
    "difficulty": "Medium",
    "description": "Short explanation of the project...",
    "features": ["Feature 1", "Feature 2", "Feature 3"]
  }}
]
"""
    try:
        result = _ask_gemini_json(prompt)
        if isinstance(result, list):
            return result[:count]
        return []
    except Exception as e:
        print(f"[AI Agent] Project generation error: {e}")
        return []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. AI INTERVIEW COACH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERVIEW_COACH_PROMPT = """You are an elite AI Interview Coach and Career Mentor. Your role is to:

1. **Mock Interviewer**: Conduct realistic mock interviews — both technical and behavioral (HR).
   - Ask one question at a time and wait for the user's answer
   - Give detailed, constructive feedback on each answer
   - Rate their answer (Excellent / Good / Needs Improvement)
   - Suggest a better/ideal answer when appropriate

2. **Technical Mentor**: Help users understand concepts deeply.
   - Explain complex topics in simple terms
   - Provide code examples when relevant
   - Ask follow-up questions to test understanding

3. **Career Guide**: Help with interview strategy.
   - Teach the STAR method for behavioral questions
   - Help with salary negotiation tips
   - Suggest how to present strengths and handle weaknesses

4. **Adaptive Difficulty**: Start with moderate difficulty and adjust based on user performance.

Keep replies concise and spoken-friendly (the user may hear your answer via text-to-speech).
Use simple language. Be encouraging but honest.
"""

# Store per-user chat sessions in memory
_coach_sessions: dict[str, genai.Chat] = {}


def get_interview_coach(user_email: str):
    """Return (or create) a Gemini interview coach session for this user."""
    if user_email not in _coach_sessions:
        _coach_sessions[user_email] = client.chats.create(
            model=MODEL_ID,
            config=genai.types.GenerateContentConfig(
                system_instruction=INTERVIEW_COACH_PROMPT
            ),
            history=[
                genai.types.Content(
                   role="model",
                   parts=[genai.types.Part(text="I'm your AI Interview Coach! I can help you with:\n"
                                               "• Mock interviews (technical & behavioral)\n"
                                               "• Detailed feedback on your answers\n"
                                               "• Learning concepts for your skill gaps\n"
                                               "• Interview tips and career guidance\n\n"
                                               "What would you like to practise today?")]
                )
            ]
        )
    return _coach_sessions[user_email]


def ai_interview_coach(user_message: str, user_email: str = "anonymous") -> str:
    """Send a message to the AI interview coach and get a response."""
    chat = get_interview_coach(user_email)
    response = chat.send_message(user_message)
    return response.text
