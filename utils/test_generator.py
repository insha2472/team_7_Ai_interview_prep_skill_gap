"""
Test question generator — now powered by Gemini AI.
Delegates question creation to the central AI agent for dynamic, skill-specific MCQs.
"""

from typing import Dict, List
from utils.ai_agent import ai_generate_test


def generate_test_questions(skill_name: str, num_questions: int = 5, test_type: str = "mcq") -> List[Dict]:
    """Generate interview-style questions for any skill using AI."""
    return ai_generate_test(skill_name, num_questions, test_type)
