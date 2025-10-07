"""
Gamification and education modules for Sentio 2.0
"""
from typing import List, Dict
import random

class QuizModule:
    def __init__(self):
        self.questions = [
            {
                'question': 'What is the Sharpe ratio?',
                'choices': ['Risk-adjusted return', 'Total return', 'Drawdown', 'Alpha'],
                'answer': 0
            },
            {
                'question': 'Which asset class is typically considered safest?',
                'choices': ['Stocks', 'Bonds', 'Commodities', 'Crypto'],
                'answer': 1
            },
            # Add more questions as needed
        ]

    def get_random_question(self) -> Dict:
        return random.choice(self.questions)

    def check_answer(self, question: Dict, choice_idx: int) -> bool:
        return question['answer'] == choice_idx

class ChallengeModule:
    def __init__(self):
        self.challenges = [
            'Achieve a portfolio Sharpe ratio above 1.0',
            'Reduce drawdown by 20% in a simulated stress test',
            'Optimize allocation for maximum ESG score',
        ]

    def get_random_challenge(self) -> str:
        return random.choice(self.challenges)

    def complete_challenge(self, challenge: str) -> bool:
        # Placeholder: always return True for demo
        return True
