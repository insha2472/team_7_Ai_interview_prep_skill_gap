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
import time
from google import genai
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

# ── Gemini setup ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_ID = "gemini-1.5-flash"


def _ask_gemini_json(prompt: str, retries: int = 2) -> dict | list:
    """Send a prompt to Gemini and parse the response as JSON with retry logic."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
            )
            text = response.text.strip()

            # Robust JSON extraction: Find the first '{' or '[' and the last '}' or ']'
            start_idx = -1
            end_idx = -1
            
            # Find start
            for i, char in enumerate(text):
                if char in '{[':
                    start_idx = i
                    break
            
            # Find end
            for i in range(len(text) - 1, -1, -1):
                if text[i] in '}]':
                    end_idx = i + 1
                    break
            
            if start_idx != -1 and end_idx != -1:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
            
            raise ValueError(f"No JSON found in response: {text[:100]}...")

        except Exception as e:
            last_error = e
            print(f"[AI Agent] Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(1) # Wait before retry
            
    raise last_error


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. AI SKILL-GAP ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_analyse_skill_gap(resume_text: str, jd_text: str) -> Dict:
    """
    Use Gemini to extract skills from resume & JD, compare them,
    and return matched_skills, missing_skills, priority_skills, and match_percentage.
    """
    prompt = f"""You are an expert HR analyst and technical recruiter.

TASK: Compare the candidate's resume against the Job Description (JD).
1. Extract ALL technical and soft skills from the RESUME.
2. Extract ALL required skills from the JD.
3. Identify:
   - "matched_skills": Skills listed in the JD that the candidate ALREADY has in their resume.
   - "missing_skills": Skills required in the JD that are NOT present (or weak) in the resume.
   - "priority_skills": Top 3-5 most critical missing skills the candidate should focus on FIRST.
4. Calculate match_percentage = (matched / total_jd_skills) * 100.

RESUME:
\"\"\"
{resume_text}
\"\"\"

JD:
\"\"\"
{jd_text}
\"\"\"

Return ONLY valid JSON (no markdown):
{{
  "matched_skills": ["...", "..."],
  "missing_skills": ["...", "..."],
  "priority_skills": ["...", "..."],
  "match_percentage": 75.0
}}"""
    try:
        result = _ask_gemini_json(prompt)
        print(f"[AI Agent] Raw analysis result: {result}")
        # Ensure required keys exist with defaults
        return {
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "priority_skills": result.get("priority_skills", []),
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

def ai_generate_test(skill_name: str, num_questions: int = 5, test_type: str = "mcq") -> List[Dict]:
    """
    Use Gemini to generate unique interview-style questions (MCQ, HR, or Coding).
    """
    if test_type == "hr":
        prompt = f"""You are a senior HR Manager.
TASK: Generate EXACTLY {num_questions} Multiple Choice Questions (MCQ) for a behavioral interview.
FOCUS SKILL: "{skill_name}".

STRICT RULES:
- Each question must present a specific workplace situation.
- Provide 4 options (A, B, C, D) representing different actions.
- One option must be the most professional choice.
- Include a 1-line technical explanation of why that choice is best.
- Return EXACTLY {num_questions} questions.
- Generate UNIQUE scenarios.

Return ONLY a valid JSON array:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "..."
  }}
] [Random Key: {time.time()}]"""
    elif test_type == "coding":
        prompt = f"""You are a Lead Software Engineer.
TASK: Generate EXACTLY {num_questions} Multiple Choice Questions (MCQ) based on coding logic, Big O complexity, and algorithm design for "{skill_name}".

STRICT RULES:
- Questions should test understanding of code snippets, efficiency, or technical concepts.
- Provide 4 options (A, B, C, D) for each question.
- correct_answer MUST be one of the options.
- Include a 1-line technical explanation.
- Generate UNIQUE problems. No repeats.
- Return EXACTLY {num_questions} question objects.

Return ONLY a valid JSON array:
[
  {{
    "question": "What is the Big O complexity of...?",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "..."
  }}
] [Random Jitter: {time.time()}]"""
    else: # Default MCQ
        prompt = f"""You are an expert technical interviewer.
TASK: Generate EXACTLY {num_questions} high-quality, UNIQUE multiple-choice questions for: "{skill_name}".

STRICT RULES:
- Return EXACTLY {num_questions} question objects.
- Each must have 4 options (A, B, C, D).
- correct_answer MUST be one of the options.
- Include a 1-line explanation.
- No markdown. No repeat questions.

Return ONLY a valid JSON array:
[
  {{
    "question": "What is ...?",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "..."
  }}
] [Random Jitter: {time.time()}]"""

    try:
        result = _ask_gemini_json(prompt)
        if isinstance(result, list) and len(result) >= 1:
            return result[:num_questions]
        return _fallback_questions(skill_name, num_questions, test_type)
    except Exception as e:
        print(f"[AI Agent] Test generation error: {e}")
        return _fallback_questions(skill_name, num_questions, test_type)


def _fallback_questions(skill_name: str, count: int, test_type: str = "mcq") -> List[Dict]:
    """Return basic fallback questions if AI fails."""
    if test_type == "hr":
        base_hr = [
            {"question": f"In a project involving {skill_name}, you realize a major deadline will be missed. What is your first action?", "options": ["Inform stakeholders with a mitigation plan", "Work overtime silently", "Wait until deadline passes", "Blame the newest hire"], "correct_answer": "Inform stakeholders with a mitigation plan", "explanation": "Transparency and proactive planning are essential for project health."},
            {"question": f"A colleague is resistant to your new approach for {skill_name}. How do you handle it?", "options": ["Schedule a 1-to-1 to find common ground", "Ignore them", "Report to HR immediately", "Complain to others"], "correct_answer": "Schedule a 1-to-1 to find common ground", "explanation": "Open communication resolves friction and encourages collaboration."},
            {"question": f"You discovered a security flaw in your {skill_name} implementation. What's the best immediate step?", "options": ["Document it and inform your supervisor", "Patch it quietly", "Ignore it", "Tell friends"], "correct_answer": "Document it and inform your supervisor", "explanation": "Proper incident reporting is critical for security and accountability."},
            {"question": f"Your team is arguing over two different architectures for {skill_name}. How do you help resolve it?", "options": ["Propose a data-driven trial or PoC", "Side with the person you like", "Let them fight it out", "Decide alone"], "correct_answer": "Propose a data-driven trial or PoC", "explanation": "Evidence-based decisions reduce conflict and improve technical outcomes."},
            {"question": f"You are asked to work on a {skill_name} task using a tool you've never used. How do you respond?", "options": ["Ask for a quick ramp-up period or resources", "Refuse the task", "Lie and say you know it", "Delegate it to someone else"], "correct_answer": "Ask for a quick ramp-up period or resources", "explanation": "Accountability involves recognizing knowledge gaps and seeking to fill them."},
            {"question": f"A client asks for a feature in {skill_name} that you know will compromise performance. What do you do?", "options": ["Explain the trade-offs and suggest an alternative", "Agree and build it anyway", "Refuse without explanation", "Ignore the request"], "correct_answer": "Explain the trade-offs and suggest an alternative", "explanation": "Advisory roles require balancing requirements with technical feasibility."},
            {"question": f"How do you handle a situation where you've made a significant error in a {skill_name} module?", "options": ["Acknowledge it, fix it, and share the lesson", "Hide the error", "Blame the legacy code", "Wait for someone to find it"], "correct_answer": "Acknowledge it, fix it, and share the lesson", "explanation": "Self-correction and transparency build trust within a technical team."},
            {"question": f"A junior developer asks for help with {skill_name} while you're busy. How do you manage this?", "options": ["Schedule a brief time to help later", "Ignore their message", "Tell them to figure it out", "Do the work for them"], "correct_answer": "Schedule a brief time to help later", "explanation": "Mentorship is vital, but so is managing your own core responsibilities."},
            {"question": f"You disagree with your manager's technical decision regarding {skill_name}. What is the best approach?", "options": ["Present your case with data in a private meeting", "Argue loudly in the team meeting", "Ignore the manager", "Talk about it behind their back"], "correct_answer": "Present your case with data in a private meeting", "explanation": "Constructive dissent should be professional and evidence-based."},
            {"question": f"What is your strategy for keeping up with new developments in {skill_name}?", "options": ["Allocate regular time for learning and community", "Only learn when forced to", "I already know everything", "Hope the tech doesn't change"], "correct_answer": "Allocate regular time for learning and community", "explanation": "Continuous learning is essential in a fast-evolving technical field."}
        ]
        import random
        random.shuffle(base_hr)
        return base_hr[:count] if count <= len(base_hr) else (base_hr * (count // len(base_hr) + 1))[:count]

    if test_type == "coding":
        base_coding = [
            {"question": f"Which data structure is most efficient for a FIFO implementation in {skill_name}?", "options": ["Stack", "Queue", "Binary Tree", "Hash Map"], "correct_answer": "Queue", "explanation": "Queues specifically handle First-In-First-Out processing."},
            {"question": f"What is the time complexity of searching in a balanced BST?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "correct_answer": "O(log n)", "explanation": "Balanced search trees halve the search space at each level."},
            {"question": f"In {skill_name}, what is the main benefit of using asynchronous processing?", "options": ["Improved concurrency", "Faster single-thread speed", "Reduced memory", "Simplified debugging"], "correct_answer": "Improved concurrency", "explanation": "Async allows handling other tasks while waiting for I/O."},
            {"question": f"What does 'DRY' stand for in software development?", "options": ["Don't Repeat Yourself", "Do Repeat Yesterday", "Data Release Yearly", "Don't Run Yet"], "correct_answer": "Don't Repeat Yourself", "explanation": "DRY aims to reduce repetition of software patterns."},
            {"question": f"Which Big O notation represents constant time complexity?", "options": ["O(1)", "O(n)", "O(log n)", "O(n!)"], "correct_answer": "O(1)", "explanation": "O(1) means the execution time is independent of input size."},
            {"question": f"What is the primary purpose of a version control system (like Git) in {skill_name} projects?", "options": ["Tracking changes and collaboration", "Running the code", "Writing documentation", "Backing up files to a local drive"], "correct_answer": "Tracking changes and collaboration", "explanation": "VCS is essential for team coordination and history management."},
            {"question": f"In {skill_name}, what is a 'Higher Order Function'?", "options": ["A function that takes or returns a function", "A function with many lines of code", "A function that is called first", "A function that uses recursion"], "correct_answer": "A function that takes or returns a function", "explanation": "Higher-order functions are a staple of functional programming."},
            {"question": f"What is the space complexity of an algorithm that creates a 2D array of size n x n?", "options": ["O(n)", "O(n^2)", "O(1)", "O(log n)"], "correct_answer": "O(n^2)", "explanation": "The memory used grows with the square of the input size n."},
            {"question": f"Which of these is a pillar of Object-Oriented Programming (OOP)?", "options": ["Encapsulation", "Recursion", "Linear search", "Concurrency"], "correct_answer": "Encapsulation", "explanation": "Encapsulation, Inheritance, Polymorphism, and Abstraction are the OOP pillars."},
            {"question": f"What is the main goal of unit testing in {skill_name}?", "options": ["Verifying individual components work correctly", "Testing the entire system at once", "Checking user interface design", "Measuring performance"], "correct_answer": "Verifying individual components work correctly", "explanation": "Unit tests focus on the smallest testable parts of an application."}
        ]
        import random
        random.shuffle(base_coding)
        return base_coding[:count] if count <= len(base_coding) else (base_coding * (count // len(base_coding) + 1))[:count]
    
    base = [
        {"question": f"What is the most fundamental concept in {skill_name}?",
         "options": ["Core fundamentals", "Advanced patterns", "Syntax only", "None of the above"],
         "correct_answer": "Core fundamentals",
         "explanation": "Understanding fundamentals is the foundation of any skill."},
        {"question": f"Which approach is best for learning {skill_name}?",
         "options": ["Practice-based learning", "Only reading docs", "Watching videos only", "Memorisation"],
         "correct_answer": "Practice-based learning",
         "explanation": "Hands-on practice is the most effective learning method."},
    ]
    import random
    random.shuffle(base)
    return (base * (count // len(base) + 1))[:count]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2.1 AI TEST GRADING (FOR HR/CODING)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ai_grade_open_ended_test(test_type: str, questions: List[Dict], user_answers: List[Dict]) -> List[Dict]:
    """
    Use Gemini to evaluate open-ended HR or Coding answers.
    Returns a list of result objects with feedback and score.
    """
    eval_data = []
    for i, q in enumerate(questions):
        answer = next((ua["answer"] for ua in user_answers if ua["question_id"] == i), "No answer provided.")
        eval_data.append({
            "question": q["question"],
            "user_answer": answer,
            "ideal_concept": q.get("ideal_answer_concept", "N/A")
        })

    prompt = f"""You are an elite {test_type.upper()} Interviewer.
TASK: Grade the following user answers for a {test_type} interview.

DATA TO EVALUATE:
{json.dumps(eval_data, indent=2)}

STRICT RULES:
- For HR: Evaluate based on STAR method, clarity, and professionalism.
- For Coding: Evaluate based on logic, edge cases, complexity (Big O), and syntax.
- For each answer, provide:
    1. A numeric score (0 to 100).
    2. Constructive feedback (max 2 sentences).

Return ONLY a valid JSON array of objects:
[
  {{
    "question_id": 0,
    "score": 85,
    "feedback": "Great logic, but you should consider null edge cases."
  }},
  ...
]"""

    try:
        results = _ask_gemini_json(prompt)
        if isinstance(results, list):
            # Map back into a full result object
            final_results = []
            for res in results:
                idx = res.get("question_id", 0)
                final_results.append({
                    "question_id": idx,
                    "question": eval_data[idx]["question"],
                    "user_answer": eval_data[idx]["user_answer"],
                    "feedback": res.get("feedback", "No feedback provided."),
                    "score": float(res.get("score", 0.0))
                })
            return final_results
        return []
    except Exception as e:
        print(f"[AI Agent] Grading error: {e}")
        return []
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
- For each week provide: a title, the skills to focus on, detailed study notes/action items, real learning resources (URLs), and EXACTLY 4-6 flashcards for active recall.
- Resources should be real, well-known websites (official docs, freeCodeCamp, Coursera, YouTube channels, GeeksforGeeks, etc.)
- Notes should include specific topics to cover, projects to build, and practice exercises.
- Flashcards should have a 'q' (question) and 'a' (answer) property.
- Order from foundational skills to advanced ones.

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
    ],
    "flashcards": [
      {{"q": "What is ...?", "a": "... is the concept of ..."}},
      {{"q": "How do you ...?", "a": "You can ... by using ..."}}
    ]
  }}
]
"""
    try:
        result = _ask_gemini_json(prompt)
        if isinstance(result, list):
            # Strict Validation: Ensure flashcards exist in every week
            for week in result:
                if "flashcards" not in week or not isinstance(week["flashcards"], list) or len(week["flashcards"]) == 0:
                    print(f"[AI Agent] Patching week {week.get('week')} with default flashcards...")
                    week["flashcards"] = [
                        {"q": f"What is the primary goal of learning {week.get('skills', ['this skill'])[0]}?", "a": "To master the core concepts and apply them in real-world scenarios."},
                        {"q": "How can you practice this week's topics?", "a": "By building small projects and following the provided resources."}
                    ]
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
            "flashcards": [
                {"q": f"What is the best way to learn {missing_skills[0]}?", "a": "Practice and official documentation are key."},
                {"q": f"Why is {missing_skills[0]} important?", "a": "It is a core requirement for this job role."}
            ]
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
_coach_sessions: dict[str, Any] = {}


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
