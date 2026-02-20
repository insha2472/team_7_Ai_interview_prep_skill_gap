import sys
import os
sys.path.append(os.getcwd())

from utils.ai_agent import ai_generate_roadmap

skills = ["PostgreSQL", "React", "Node.js"]
print(f"Testing roadmap generation for: {skills}\n")

roadmap = ai_generate_roadmap(skills)

for week in roadmap:
    print(f"Week {week.get('week')}: {week.get('title')}")
    print(f"Flashcards count: {len(week.get('flashcards', []))}")
    if 'flashcards' in week:
        print(f"First Flashcard: {week['flashcards'][0]}")
    else:
        print("MISSING FLASHCARDS!")
    print("-" * 20)
