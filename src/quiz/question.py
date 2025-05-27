import json
from typing import List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Option:
    text: str
    is_correct: bool = False

@dataclass
class Question:
    question_text: str
    options: List[Option]
    explanation: Optional[str]
    image_path: Optional[str] = None

    def __post_init__(self):
        if not any(opt.is_correct for opt in self.options):
            raise ValueError("At least one option must be correct")

@dataclass
class Quiz:
    questions: List[Question]

def load_quiz_from_json(file_path: str) -> Quiz:
    """Load quiz data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions: List[Question] = []
    for q in data['questions']:
        options = [Option(**opt) for opt in q['options']]
        questions.append(Question(
            question_text=q['question_text'],
            explanation=q.get('explanation', None),
            options=options,
            image_path=q.get('image_path'),
        ))
    
    return Quiz(
        questions=questions
    )

def save_quiz_to_json(quiz: Quiz, file_path: str):
    """Save quiz data to JSON file"""
    quiz_dict = asdict(quiz)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(quiz_dict, f, indent=2, ensure_ascii=False)
